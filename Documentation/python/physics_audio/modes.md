# Modes

`from tdw.physics_audio.modes import Modes`

Resonant mode properties: Frequencies, powers, and times.

***

## Fields

- `frequencies` A numpy array of mode frequencies in Hz.

- `powers` A numpy array of mode onset powers in dB re 1.

- `decay_times` A numpy array of mode decay times i.e. the time in ms it takes for each mode to decay 60dB from its onset power.

***

## Functions

#### \_\_init\_\_

**`Modes(frequencies, powers, decay_times)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| frequencies |  np.array |  | A numpy array of mode frequencies in Hz. |
| powers |  np.array |  | A numpy array of mode onset powers in dB re 1. |
| decay_times |  np.array |  | A numpy array of mode decay times i.e. the time in ms it takes for each mode to decay 60dB from its onset power. |

#### sum_modes

**`self.sum_modes()`**

**`self.sum_modes(fs=44100, resonance=1.0)`**

Create mode time-series from mode properties and sum them together.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| fs |  int  | 44100 | The framerate. |
| resonance |  float  | 1.0 | The object resonance. |

_Returns:_  A synthesized sound.

#### mode_add

**`Modes.mode_add(a, b)`**

_(Static)_

Add together numpy arrays of different lengths by zero-padding the shorter.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| a |  np.array |  | The first array. |
| b |  np.array |  | The second array. |

_Returns:_  The summed modes.

