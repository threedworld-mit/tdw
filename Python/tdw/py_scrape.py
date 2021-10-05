from pydub import AudioSegment
from tdw.output_data import Rigidbodies, Collision, EnvironmentCollision
import numpy as np
from tdw.tdw_utils import TDWUtils
from scipy.signal import butter, lfilter, fftconvolve, unit_impulse, sosfilt, firwin
from scipy.ndimage import gaussian_filter1d
import base64
from tdw.py_impact import PyImpact
from typing import Dict, Union


class PyScrape:
    """
    Generate scraping sounds from physics data.

    Sounds are synthesized as described in: [Traer,Cusimano and McDermott, A PERCEPTUALLY INSPIRED GENERATIVE MODEL OF RIGID-BODY CONTACT SOUNDS, Digital Audio Effects, (DAFx), 2019](http://dafx2019.bcu.ac.uk/papers/DAFx2019_paper_57.pdf)

    For a general guide on impact sounds in TDW, read [this](../misc_frontend/impact_sounds.md).

    Usage:

    ```python
    from tdw.controller import Controller
    from tdw.py_impact import PyImpact

    p = PyScrape()
    c = Controller()
    c.start()

    # Your code here.

    c.communicate(p.get_scrape_sound_command(arg1, arg2, ... ))
    ```
    """

    def smooth(x, window_len=11, window='hanning'):
        """smooth the data using a window with requested size.

        This method is based on the convolution of a scaled window with the signal.
        The signal is prepared by introducing reflected copies of the signal
        (with the window size) in both ends so that transient parts are minimized
        in the begining and end part of the output signal.

        input:
            x: the input signal
            window_len: the dimension of the smoothing window; should be an odd integer
            window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
                flat window will produce a moving average smoothing.

        output:
            the smoothed signal

        example:

        t=linspace(-2,2,0.1)
        x=sin(t)+randn(len(t))*0.1
        y=smooth(x)

        see also:

        numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
        scipy.signal.lfilter

        TODO: the window parameter could be the window itself if an array instead of a string
        NOTE: length(output) != length(input), to correct this: return y[(window_len/2-1):-(window_len/2)] instead of just y.
        """

        # if x.ndim != 1:
        #     raise ValueError, "smooth only accepts 1 dimension arrays."

        # if x.size < window_len:
        #     raise ValueError, "Input vector needs to be bigger than window size."

        print(window_len)
        if window_len < 3:
            return x

        # if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        #     raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"

        s = numpy.r_[x[window_len - 1:0:-1], x, x[-2:-window_len - 1:-1]]
        # print(len(s))
        if window == 'flat':  # moving average
            w = numpy.ones(window_len, 'd')
        else:
            w = eval('numpy.' + window + '(window_len)')

        y = numpy.convolve(w / w.sum(), s, mode='valid')
        return y

    def _butter_bandpass(self, lowcut, highcut, fs, order=5):
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        sos = butter(order, [low, high], btype='band', output='sos')
        return sos

    def _butter_highpass(self, cutoff, fs, order=5):
        nyq = 0.5 * fs
        cutoff = cutoff / nyq
        sos = butter(order, cutoff, btype='high', output='sos')
        return sos

    def butter_bandpass_filter(self, data, lowcut, highcut, fs, order=5):
        """
        Implementation of a Butterworth band-pass filter.From SciPy Cookbook:
        https://scipy-cookbook.readthedocs.io/items/ButterworthBandpass.html
        :param data: Audio data to filter.
        :param lowcut: L filter cutoff.
        :param highcut: High filter cutoff.
        :param fs: Sample rate.
        :param order: Order of the filter.
        """
        sos = self._butter_bandpass(lowcut, highcut, fs, order=order)
        # y = lfilter(b, a, data)
        filtered = sosfilt(sos, data)
        return filtered

    def butter_highpass_filter(self, data, cutoff, fs, order=5):
        """
        Implementation of a Butterworth high-pass filter.
        :param data: Audio data to filter.
        :param lowcut: Filter cutoff.
        :param fs: Sample rate.
        :param order: Order of the filter.
        """
        sos = self._butter_highpass(cutoff, fs, order=order)
        filtered = sosfilt(sos, data)
        return filtered

    def normalize_floats(self, arr):
        """
        Normalize numpy array of float audio data.
        :param arr: Numpy float data to normalize.
        """
        if np.all(arr == 0):
            return arr
        else:
            return arr / np.abs(arr).max()

    def normalize_16bitInt(self, arr):
        """
        Convert numpy float array to normalized 16-bit integers.
        :param arr: Numpy float data to convert.
        """
        normalized_floats = self.normalize_floats(arr)
        return (normalized_floats * 32767).astype(np.int16)

    def nonorm_16bitInt(self, arr):
        """
        Convert numpy float array to normalized 16-bit integers.
        :param arr: Numpy float data to convert.
        """
        normalized_floats = arr / 10000
        return (normalized_floats * 32767).astype(np.int16)

    def __init__(self, max_vel: float = 5.0):
        """
        :param max_vel: Max velocity -- "cap" incoming velocities to this value.
        """
        self.channels = 1
        self.width = 2
        self.samplerate = 44100
        self.buffer_size = 1024  # 512
        self.max_vel = max_vel

        # Create an empty AudioSegment
        self.summed_master_dict: Dict[str, AudioSegment] = dict()

        # keeping a track of previous indices
        self.prev_ind = 0

        # Initialize an empty array; this will hold the impulse response data for later convolution.
        self.scraping_ir = np.empty

        # Starting velocity magnitude of scraping object; use in calculating changing band-pass filter
        self.start_velo_dict: Dict[str, float] = dict()

        # Starting band-pass filter parameters
        # self.initial_lowcut = 300
        # self.initial_highcut = 4000

        # "Average" starting loudness for sound.
        self.target_dBFS = -20.0

        # Initialize the scraping event counter.
        self.scrape_event_count_dict: Dict[str, int] = dict()

        data_surf = np.genfromtxt('test_surf.csv', delimiter=',')

        # rate,data_surf = wavfile.read('test_surf.wav')
        # data_surf = np.append(data_surf,data_surf)
        # data_surf = np.append(data_surf,data_surf)
        # data_surf = np.append(data_surf,data_surf)
        # data_surf = np.append(data_surf,data_surf)
        self.data_surf = np.append(data_surf, data_surf)

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
        # Create dictionary key for this object-to-object scrape
        scrape_key = str(target_id) + "_" + str(other_id)

        # Initialize scrape variables; if this is an in=process scrape, these will be replaced bu te stored values.
        summed_master = AudioSegment.silent(duration=0, frame_rate=self.samplerate)
        scrape_event_count = 0

        # Is this a new scrape?
        if scrape_key in self.summed_master_dict:
            summed_master = self.summed_master_dict[scrape_key]
            scrape_event_count = self.scrape_event_count_dict[scrape_key]
        else:
            # No -- add initialized values to dictionaries.
            self.summed_master_dict[scrape_key] = summed_master
            self.scrape_event_count_dict[scrape_key] = scrape_event_count

        # Get magnitude of velocity of the scraping object.
        vel = rbody.get_velocity(0)
        mag = min(TDWUtils.get_magnitude(TDWUtils.get_vector3(vel[0], vel[1], vel[2])), self.max_vel)
        print(mag)

        # Cache the starting velocity.
        if scrape_event_count == 0:
            self.start_velo_dict[scrape_key] = mag

        # Map magnitude to gain level -- decrease in velocity = rise in negative dB, i.e. decrease in gain.
        db1 = np.interp(mag, [0, self.max_vel], [-80, -12])
        db2 = np.interp(mag ** 2, [0, self.max_vel ** 2], [-80, -12])
        # print(db)

        # We want the filter "window" to change continuously, otherwise we are generating unwanted reverberation.
        # lowcut = (mag / self.start_velo_dict[scrape_key] ) * self.initial_lowcut
        # highcut = (mag / self.start_velo_dict[scrape_key] ) * self.initial_highcut

        # Get impulse response of the colliding objects. Amp values would normally come from objects.csv.
        # We also get the lowest-frequency IR mode, which we use to set the high-pass filter cutoff below.
        self.scraping_ir, min_mode_freq = p.get_impulse_response(collision=collision,
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

        data_surf = self.data_surf

        nm_per_pixel = 1394.068
        m_per_pixel = nm_per_pixel * 10 ** -9
        data_surf = data_surf  # * 0.5* 10**-3
        # print(self.target_dBFS)
        dsdx = (data_surf[1:] - data_surf[0:-1]) / m_per_pixel
        d2sdx2 = (dsdx[1:] - dsdx[0:-1]) / m_per_pixel

        dist = mag / 1000
        num_pts = np.floor(dist / m_per_pixel)
        num_pts = int(num_pts)
        if num_pts == 0:
            num_pts = 1
        # print('dist:',dist)
        # print('numpts:', num_pts)

        # interpolate the surface slopes and curvatures based on the velocity magnitude
        final_ind = self.prev_ind + num_pts

        if final_ind > len(data_surf) - 100:
            self.prev_ind = 0
            final_ind = num_pts

        vect1 = np.linspace(0, 1, num_pts)
        vect2 = np.linspace(0, 1, 4010)
        # print(len(dsdx[self.prev_ind:final_ind]))
        # print(len(vect2))

        slope_int = np.interp(vect2, vect1, dsdx[self.prev_ind:final_ind])
        curve_int = np.interp(vect2, vect1, d2sdx2[self.prev_ind:final_ind])
        # print('curve_int',len(curve_int))

        self.prev_ind = final_ind

        # if self.prev_ind > len(data_surf)-10000:
        #     self.prev_ind = 1

        curve_int_tan = np.tanh(curve_int / 1000)
        # print(curve_int_tan.shape)

        d2_section = gaussian_filter1d(curve_int_tan, 10)
        # d2_section = curve_int_tan

        # final_ind = self.prev_ind + len(normalized_noise_ints) -1

        # vert_force = mag**2 * d2_section
        # hor_force = mag * slope_int

        vert_force = d2_section
        hor_force = slope_int

        t_force = vert_force / max(np.abs(vert_force)) + 0.2 * hor_force[:len(vert_force)]

        noise_seg1 = AudioSegment(t_force.tobytes(),
                                  frame_rate=self.samplerate,
                                  sample_width=self.width,
                                  channels=self.channels)

        # print(t_force.shape)

        #   print(data_surf.shape)

        # Normalize gain.
        noise_seg1.apply_gain(self.target_dBFS)

        # Fade head and tail.
        noise_seg_fade = noise_seg1.fade_in(4).fade_out(4)
        # noise_seg_fade = noise_seg1

        # Convolve the band-pass filtered sound with the impulse response.
        conv = fftconvolve(self.scraping_ir, noise_seg_fade.get_array_of_samples())
        # conv = fftconvolve(self.scraping_ir, noise_seg_fade.raw_data)

        # conv  = self.butter_bandpass_filter(conv, 10, 15000, self.samplerate, order=6)

        # print('conv:' ,len(conv))

        # Again, we need this as an AudioSegment for overlaying with the previous frame's segment.
        # Convert to 16-bit integers for Unity, normalizing to make sure to minimize loss of precision from truncating floating values.
        normalized_noise_ints_conv = self.normalize_16bitInt(conv)
        noise_seg_conv = AudioSegment(normalized_noise_ints_conv.tobytes(),
                                      frame_rate=self.samplerate,
                                      sample_width=self.width,
                                      channels=self.channels)

        # Gain-adjust the convolved segment using db value computed earlier.
        noise_seg_conv = noise_seg_conv.apply_gain(db2)
        # noise_seg_conv = normalized_noise_ints_conv
        # 20 ms chunk of silence, to be appended to convolved audio segments.
        silence_50ms = AudioSegment.silent(duration=50, frame_rate=self.samplerate)

        if scrape_event_count == 0:
            # First time through -- append 50 ms of silence to the end of the current segment and make that "master".
            summed_master = noise_seg_conv + silence_50ms
        elif scrape_event_count == 1:
            # Second time through -- append 50 ms silence to start of current segment and overlay onto "master".
            summed_master = summed_master.overlay(silence_50ms + noise_seg_conv)
            # summed_master = noise_seg_conv
        else:
            # Pad the end of master with 50 ms of silence, the start of the current segment with (n * 50ms) of silence, and overlay.
            padded_current = (silence_50ms * scrape_event_count) + noise_seg_conv
            summed_master = summed_master + silence_50ms
            # summed_master = noise_seg_conv
            summed_master = summed_master.overlay(padded_current)

        # Extract 100ms "chunk" of sound to send over to Unity
        start_idx = 100 * scrape_event_count
        temp = summed_master[-(len(summed_master) - start_idx):]
        unity_chunk = temp[:100]
        # print(len(unity_chunk.raw_data))
        # Update stored summed waveform
        self.summed_master_dict[scrape_key] = summed_master

        # Update scrape event count.
        scrape_event_count += 1
        self.scrape_event_count_dict[scrape_key] = scrape_event_count

        # Convert to base64 for transfer to Unity.
        b64_data = base64.b64encode(unity_chunk.raw_data).decode()
        # b64_data = base64.b64encode(unity_chunk).decode()

        return {"$type": "play_audio_data" if play_audio_data else "play_point_source_data",
                "id": target_id,
                "num_frames": len(unity_chunk.raw_data),
                "num_channels": self.channels,
                "frame_rate": self.samplerate,
                "wav_data": b64_data,
                "y_pos_offset": 0}

        # return {"$type": "play_audio_data" if play_audio_data else "play_point_source_data",
        #         "id": target_id,
        #         "num_frames": len(unity_chunk),
        #         "num_channels": self.channels,
        #         "frame_rate": self.samplerate,
        #         "wav_data": b64_data,
        #         "y_pos_offset": 0}

    def end_scrape(self, target_id: int, other_id: int):
        """
        Clean up after a given scrape event has ended.
        """
        scrape_key = str(target_id) + "_" + str(other_id)
        del self.scrape_event_count_dict[scrape_key]
        del self.summed_master_dict[scrape_key]
        del self.start_velo_dict[scrape_key]


