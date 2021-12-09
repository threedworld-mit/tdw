import math
import numpy as np


class Modes:
    """
    Resonant mode properties: Frequencies, powers, and times.
    """

    def __init__(self, frequencies: np.array, powers: np.array, decay_times: np.array):
        """
        :param frequencies: A numpy array of mode frequencies in Hz.
        :param powers: A numpy array of mode onset powers in dB re 1.
        :param decay_times: A numpy array of mode decay times i.e. the time in ms it takes for each mode to decay 60dB from its onset power.
        """

        """:field
        A numpy array of mode frequencies in Hz.
        """
        self.frequencies: np.array = frequencies
        """:field
        A numpy array of mode onset powers in dB re 1.
        """
        self.powers: np.array = powers
        """:field
        A numpy array of mode decay times i.e. the time in ms it takes for each mode to decay 60dB from its onset power.
        """
        self.decay_times: np.array = decay_times

    def sum_modes(self, fs: int = 44100, resonance: float = 1.0) -> np.array:
        """
        Create mode time-series from mode properties and sum them together.

        :param fs: The framerate.
        :param resonance: The object resonance.

        :return A synthesized sound.
        """

        synth_sound: np.array = np.empty
        # Scroll through modes.
        for i in range(len(self.frequencies)):
            H_dB = 80 + self.powers[i]
            L_ms = self.decay_times[i] * H_dB / 60
            mLen = math.ceil(L_ms / 1e3 * fs)
            # if mode length is greater than the current time-series we have had make our time series longer
            max_len = mLen
            if mLen > max_len:
                max_len = mLen
            tt = np.arange(0, max_len) / fs
            # synthesize a sinusoid
            mode = np.cos(2 * math.pi * self.frequencies[i] * tt)
            mode = mode * (10 ** (self.powers[i] / 20))
            dcy = tt * (60 / (self.decay_times[i] * resonance / 1e3))
            env = 10 ** (-dcy / 20)
            mode = mode * env
            if i == 0:
                synth_sound = mode
            else:
                synth_sound = Modes.mode_add(synth_sound, mode)
        return synth_sound

    @staticmethod
    def mode_add(a: np.array, b: np.array) -> np.array:
        """
        Add together numpy arrays of different lengths by zero-padding the shorter.

        :param a: The first array.
        :param b: The second array.

        :return The summed modes.
        """

        if len(a) < len(b):
            c = b.copy()
            c[:len(a)] += a
        else:
            c = a.copy()
            c[:len(b)] += b
        return c
