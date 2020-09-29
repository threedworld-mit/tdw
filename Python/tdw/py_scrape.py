from pydub import AudioSegment
from pydub.playback import play
from pydub.generators import WhiteNoise
from tdw.output_data import OutputData, Rigidbodies, Collision, EnvironmentCollision
import numpy as np
from tdw.tdw_utils import TDWUtils
from scipy.signal import butter, lfilter, fftconvolve, unit_impulse, sosfilt, firwin
import base64
from tdw.py_impact import PyImpact
from typing import Dict, Union


class PyScrape:
    """
    """

    def butter_bandpass(self, lowcut, highcut, fs, order=5):
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        sos = butter(order, [low, high], btype='band', output='sos')
        return sos

    def butter_bandpass_filter(self, data, lowcut, highcut, fs, order=5):
        """
        Implementation of a Butterworth band-pass filter.From SciPy Cookbook:
        https://scipy-cookbook.readthedocs.io/items/ButterworthBandpass.html
        """
        sos = self.butter_bandpass(lowcut, highcut, fs, order=order)
        #y = lfilter(b, a, data)
        filtered = sosfilt(sos, data)
        return filtered

    def normalize_floats(self, arr):
        return arr / np.abs(arr).max()

    def normalize_16bitInt(self, arr):
        # Convert numpy float array to normalized 16-bit integers
        normalized_floats = self.normalize_floats(arr)
        return (normalized_floats * 32767).astype(np.int16)


    def __init__(self):

        self.channels = 1
        self.width = 2
        self.samplerate = 44100
        self.buffer_size = 1024

        # Create an empty AudioSegment
        self.summed_master_dict: Dict[str, AudioSegment] = dict()
        
        # Initialize an empty array; this will hold the impulse response data for later convolution.
        self.scraping_ir = np.empty
    
        # Starting velocity magnitude of scraping object; use in calculating changing band-pass filter
        self.start_velo_dict: Dict[str, float] = dict()  

        # Starting band-pass filter parameters
        self.initial_lowcut = 2000
        self.initial_highcut = 16000

        # "Average" starting loudness for sound.
        self.target_dBFS = -40.0

        # Initialize the scraping event counter.
        self.scrape_event_count_dict: Dict[str, int] = dict()


    def get_scrape_sound_command(self, p: PyImpact, rbody, collision: Union[Collision, EnvironmentCollision], rigidbodies: Rigidbodies, target_id: int, target_mat: str, target_amp: float, other_id: int, other_mat: str, other_amp: float, resonance: float, play_audio_data: bool = True) -> dict:
    
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
        mag = TDWUtils.get_magnitude(TDWUtils.get_vector3(vel[0], vel[1], vel[2]))

        # Cache the starting velocity.
        if scrape_event_count == 0:
            self.start_velo_dict[scrape_key] = mag

        # Map magnitude to gain level -- decrease in velocity = rise in negative dB, i.e. decrease in gain.
        db = np.interp(mag, [0, self.start_velo_dict[scrape_key]], [-120, -6])
        #print(db)

        # We want the filter "window" to change continuously, otherwise we are generating unwanted reverberation.
        lowcut = (mag / self.start_velo_dict[scrape_key] ) * self.initial_lowcut 
        highcut = (mag / self.start_velo_dict[scrape_key] ) * self.initial_highcut

        # Get impulse response of the colliding objects. Amp values would normally come from objects.csv.
        self.scraping_ir, min_mode_freq = p.get_impulse_response(collision=collision,
                                                                 rigidbodies=rigidbodies,
                                                                 target_id=target_id,
                                                                 target_mat=target_mat,
                                                                 other_id=other_id,
                                                                 other_mat=other_mat,
                                                                 other_amp=other_amp,
                                                                 target_amp=target_amp,
                                                                 resonance=resonance)

        # Generate the chunk of band-pass filtered noise
        noise1 = WhiteNoise().to_audio_segment(duration=100)
        bp_noise = self.butter_bandpass_filter(noise1.get_array_of_samples(), max(lowcut, 598), max(highcut, 4782), self.samplerate, order=6)

        # Apply second filter that gets rid of all sound less than the frequency of the lowest IR mode.
        b = firwin(101, cutoff=min_mode_freq, fs=self.samplerate, pass_zero=False)
        bp_noise2 = lfilter(b, [1.0], bp_noise)

        # Turn it into an AudioSegment, so we can gain adjust it.
        normalized_noise_ints = bp_noise2.astype(np.int32)
        noise_seg = AudioSegment(normalized_noise_ints.tobytes(), 
                             frame_rate=self.samplerate,
                             sample_width=self.width, 
                             channels=self.channels)

        # Normalize gain.
        noise_seg.apply_gain(self.target_dBFS)


        # Fade head and tail.
        noise_seg_fade = noise_seg.fade_in(10).fade_out(10)

        # Convolve the band-pass filtered sound with the impulse response.
        conv = fftconvolve(self.scraping_ir, noise_seg_fade.get_array_of_samples())

        # Again, we need this as an AudioSegment for overlaying with the previous frame's segment.
        # Convert to 16-bit integers for Unity, normalizing to make sure to minimize loss of precision from truncating floating values.
        normalized_noise_ints_conv = self.normalize_16bitInt(conv)
        noise_seg_conv = AudioSegment(normalized_noise_ints_conv.tobytes(), 
                                  frame_rate=self.samplerate,
                                  sample_width=self.width, 
                                  channels=self.channels)

        # Gain-adjust the convolved segment using db value computed earlier.
        noise_seg_conv = noise_seg_conv.apply_gain(db)

        # 50 ms chunk of silence, to be appended to convolved audio segments.
        silence_50ms = AudioSegment.silent(duration=50, frame_rate=self.samplerate)

        if scrape_event_count == 0:
            # First time through -- append 50 ms of silence to the end of the current segment and make that "master".
            summed_master = noise_seg_conv + silence_50ms
        elif scrape_event_count == 1:
            # Second time through -- append 50 ms silence to start of current segment and overlay onto "master".
            summed_master = summed_master.overlay(silence_50ms + noise_seg_conv)
        else:
            # Pad the end of master with 50 ms of silence, the start of the current segment with (n * 50ms) of silence, and overlay.
            padded_current = (silence_50ms * scrape_event_count) + noise_seg_conv
            summed_master = summed_master + silence_50ms
            summed_master = summed_master.overlay(padded_current)

        # Extract 100ms "chunk" of sound to send over to Unity
        start_idx = 100 * scrape_event_count
        temp = summed_master[-(len(summed_master) - start_idx):]
        unity_chunk = temp[:100]

        # Update stored summed waveform
        self.summed_master_dict[scrape_key] = summed_master

        # Update scrape event count.
        scrape_event_count += 1
        self.scrape_event_count_dict[scrape_key] = scrape_event_count

        # Convert to base64 for transfer to Unity.
        b64_data = base64.b64encode(unity_chunk.raw_data).decode()

        return {"$type": "play_audio_data",
            "id": target_id,
            "num_frames": len(unity_chunk.raw_data),
            "num_channels": self.channels,
            "frame_rate": self.samplerate,
            "wav_data": b64_data,
            "y_pos_offset": 0}

 

