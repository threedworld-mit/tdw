import base64
from typing import Dict, Union, Tuple
from pkg_resources import resource_filename
from pydub import AudioSegment
from scipy.signal import fftconvolve
from scipy.ndimage import gaussian_filter1d
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.output_data import Rigidbodies, Collision, EnvironmentCollision
from tdw.py_impact import PyImpact


class PyScrape:
    """
    Generate scraping sounds from physics data.
    """

    # The scrape surface.
    SCRAPE_SURFACE: np.array = np.load(resource_filename(__name__, f"py_impact/scrape_surface.npy"))
    SCRAPE_SURFACE = np.append(SCRAPE_SURFACE, SCRAPE_SURFACE)
    CHANNELS: int = 1
    WIDTH: int = 2
    SAMPLE_RATE: int = 44100
    BUFFER_SIZE: int = 1024
    TARGET_DBFS: float = -20.0
    SILENCE_50MS: AudioSegment = AudioSegment.silent(duration=50, frame_rate=SAMPLE_RATE)
    M_PER_PIXEL: float = 1394.068 * 10 ** -9

    def __init__(self, max_vel: float = 5.0):
        """
        :param max_vel: Max velocity -- "cap" incoming velocities to this value.
        """

        self.max_vel: float = max_vel

        # Create an empty AudioSegment.
        self.summed_masters: Dict[Tuple[int, int], AudioSegment] = dict()
        # Keeping a track of previous indices.
        self.prev_ind: int = 0
        # Starting velocity magnitude of scraping object; use in calculating changing band-pass filter
        self.start_velocities: Dict[Tuple[int, int], float] = dict()
        # Initialize the scraping event counter.
        self.scrape_events_count: Dict[Tuple[int, int], int] = dict()

    def reset(self) -> None:
        """
        Reset PyScrape.
        :return:
        """
        self.summed_masters.clear()
        self.prev_ind = 0
        self.start_velocities.clear()
        self.scrape_events_count.clear()

    def get_scrape_sound_command(self, p: PyImpact, rbody, collision: Union[Collision, EnvironmentCollision],
                                 rigidbodies: Rigidbodies, target_id: int, target_mat: str, target_amp: float,
                                 other_id: int, other_mat: str, other_amp: float, resonance: float,
                                 play_audio_data: bool = True) -> dict:
        """
        Create a scrape sound, and return a valid command to play audio data in TDW.
        "target" should usually be the smaller object, which will play the sound.
        "other" should be the larger (stationary) object.

        :param collision: TDW `Collision` or `EnvironmentCollision` output data.
        :param target_amp: The target's amp value.
        :param target_mat: The target's audio material.
        :param other_amp: The other object's amp value.
        :param other_id: The other object's ID.
        :param other_mat: The other object's audio material.
        :param rigidbodies: TDW `Rigidbodies` output data.
        :param target_id: The ID of the object that will play the sound.
        :param play_audio_data: If True, return a `play_audio_data` command. If False, return a `play_point_source_data` command (useful only with Resonance Audio; see Command API).

        :return A `play_audio_data` or `play_point_source_data` command that can be sent to the build via `Controller.communicate()`.
        """

        scrape_key: Tuple[int, int] = (target_id, other_id)

        # Initialize scrape variables; if this is an in=process scrape, these will be replaced bu te stored values.
        summed_master = AudioSegment.silent(duration=0, frame_rate=PyScrape.SAMPLE_RATE)
        scrape_event_count = 0

        # Is this a new scrape?
        if scrape_key in self.summed_masters:
            summed_master = self.summed_masters[scrape_key]
            scrape_event_count = self.scrape_events_count[scrape_key]
        else:
            # No -- add initialized values to dictionaries.
            self.summed_masters[scrape_key] = summed_master
            self.scrape_events_count[scrape_key] = scrape_event_count

        # Get magnitude of velocity of the scraping object.
        vel = rbody.get_velocity(0)
        mag = min(TDWUtils.get_magnitude(TDWUtils.get_vector3(vel[0], vel[1], vel[2])), self.max_vel)

        # Cache the starting velocity.
        if scrape_event_count == 0:
            self.start_velocities[scrape_key] = mag

        # Map magnitude to gain level -- decrease in velocity = rise in negative dB, i.e. decrease in gain.
        db = np.interp(mag ** 2, [0, self.max_vel ** 2], [-80, -12])

        # Get impulse response of the colliding objects. Amp values would normally come from objects.csv.
        # We also get the lowest-frequency IR mode, which we use to set the high-pass filter cutoff below.
        scraping_ir, min_mode_freq = p.get_impulse_response(collision=collision,
                                                            rigidbodies=rigidbodies,
                                                            target_id=target_id,
                                                            target_mat=target_mat,
                                                            other_id=other_id,
                                                            other_mat=other_mat,
                                                            other_amp=other_amp,
                                                            target_amp=target_amp,
                                                            resonance=resonance)

        #   Load the surface texture as a 1D vector
        #   Create surface texture of desired length
        #   Calculate first and second derivatives by first principles
        #   Apply non-linearity on the second derivative
        #   Apply a variable Gaussian average
        #   Calculate the horizontal and vertical forces
        #   Convolve the force with the impulse response
        dsdx = (PyScrape.SCRAPE_SURFACE[1:] - PyScrape.SCRAPE_SURFACE[0:-1]) / PyScrape.M_PER_PIXEL
        d2sdx2 = (dsdx[1:] - dsdx[0:-1]) / PyScrape.M_PER_PIXEL

        dist = mag / 1000
        num_pts = np.floor(dist / PyScrape.M_PER_PIXEL)
        num_pts = int(num_pts)
        if num_pts == 0:
            num_pts = 1
        # No scrape.
        if num_pts == 1:
            self._end_scrape(scrape_key)
            return {"$type": "do_nothing"}

        # interpolate the surface slopes and curvatures based on the velocity magnitude
        final_ind = self.prev_ind + num_pts

        if final_ind > len(PyScrape.SCRAPE_SURFACE) - 100:
            self.prev_ind = 0
            final_ind = num_pts

        vect1 = np.linspace(0, 1, num_pts)
        vect2 = np.linspace(0, 1, 4010)

        slope_int = np.interp(vect2, vect1, dsdx[self.prev_ind:final_ind])
        curve_int = np.interp(vect2, vect1, d2sdx2[self.prev_ind:final_ind])

        self.prev_ind = final_ind

        curve_int_tan = np.tanh(curve_int / 1000)

        d2_section = gaussian_filter1d(curve_int_tan, 10)

        vert_force = d2_section
        hor_force = slope_int

        t_force = vert_force / max(np.abs(vert_force)) + 0.2 * hor_force[:len(vert_force)]

        noise_seg1 = AudioSegment(t_force.tobytes(),
                                  frame_rate=PyScrape.SAMPLE_RATE,
                                  sample_width=PyScrape.WIDTH,
                                  channels=PyScrape.CHANNELS)
        # Normalize gain.
        noise_seg1.apply_gain(PyScrape.TARGET_DBFS)

        # Fade head and tail.
        noise_seg_fade = noise_seg1.fade_in(4).fade_out(4)
        # Convolve the band-pass filtered sound with the impulse response.
        conv = fftconvolve(scraping_ir, noise_seg_fade.get_array_of_samples())

        # Again, we need this as an AudioSegment for overlaying with the previous frame's segment.
        # Convert to 16-bit integers for Unity, normalizing to make sure to minimize loss of precision from truncating floating values.
        normalized_noise_ints_conv = PyScrape._normalize_16bit_int(conv)
        noise_seg_conv = AudioSegment(normalized_noise_ints_conv.tobytes(),
                                      frame_rate=PyScrape.SAMPLE_RATE,
                                      sample_width=PyScrape.WIDTH,
                                      channels=PyScrape.CHANNELS)

        # Gain-adjust the convolved segment using db value computed earlier.
        noise_seg_conv = noise_seg_conv.apply_gain(db)
        if scrape_event_count == 0:
            # First time through -- append 50 ms of silence to the end of the current segment and make that "master".
            summed_master = noise_seg_conv + PyScrape.SILENCE_50MS
        elif scrape_event_count == 1:
            # Second time through -- append 50 ms silence to start of current segment and overlay onto "master".
            summed_master = summed_master.overlay(PyScrape.SILENCE_50MS + noise_seg_conv)
            # summed_master = noise_seg_conv
        else:
            # Pad the end of master with 50 ms of silence, the start of the current segment with (n * 50ms) of silence, and overlay.
            padded_current = (PyScrape.SILENCE_50MS * scrape_event_count) + noise_seg_conv
            summed_master = summed_master + PyScrape.SILENCE_50MS
            # summed_master = noise_seg_conv
            summed_master = summed_master.overlay(padded_current)

        # Extract 100ms "chunk" of sound to send over to Unity
        start_idx = 100 * scrape_event_count
        temp = summed_master[-(len(summed_master) - start_idx):]
        unity_chunk = temp[:100]
        # Update stored summed waveform
        self.summed_masters[scrape_key] = summed_master

        # Update scrape event count.
        scrape_event_count += 1
        self.scrape_events_count[scrape_key] = scrape_event_count
        return {"$type": "play_audio_data" if play_audio_data else "play_point_source_data",
                "id": target_id,
                "num_frames": len(unity_chunk.raw_data),
                "num_channels": PyScrape.CHANNELS,
                "frame_rate": PyScrape.SAMPLE_RATE,
                "wav_data": base64.b64encode(unity_chunk.raw_data).decode(),
                "y_pos_offset": 0}

    @staticmethod
    def _normalize_16bit_int(arr: np.array) -> np.array:
        """
        Convert numpy float array to normalized 16-bit integers.

        :param arr: Numpy float data to convert.

        :return: The converted numpy array.
        """

        normalized_floats = PyScrape._normalize_floats(arr)

        return (normalized_floats * 32767).astype(np.int16)

    @staticmethod
    def _normalize_floats(arr: np.array) -> np.array:
        """
        Normalize numpy array of float audio data.

        :param arr: Numpy float data to normalize.

        :return The normalized array.
        """

        if np.all(arr == 0):
            return arr
        else:
            return arr / np.abs(arr).max()

    def _end_scrape(self, scrape_key: Tuple[int, int]) -> None:
        """
        Clean up after a given scrape event has ended.
        """

        if scrape_key in self.scrape_events_count:
            del self.scrape_events_count[scrape_key]
        if scrape_key in self.summed_masters:
            del self.summed_masters[scrape_key]
        if scrape_key in self.start_velocities:
            del self.start_velocities[scrape_key]
