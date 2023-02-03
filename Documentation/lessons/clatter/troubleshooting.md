##### Clatter

# Troubleshooting Clatter

The document is a non-exhaustive list of common problems in Clatter and how to fix them.

## Sounds are too "plinky"

This is a general problem with Clatter that we intend to correct by recording larger objects. In the meantime, you can adjust the size bucket values and fake masses of objects. You can also try increasing the resonance of the non-moving object.

## Non-rigid impact materials don't sound as good

This is a known problem that we will fix.

## Impact sounds are distorted

Try setting `dsp_buffer_size` in the constructor to 1024 instead of the default 256.

## There are extra impact sounds

Usually, this is because roll sounds are being interpreted as impacts. Try setting `roll_substitute` in the `Clatter` constructor to `"scrape"` or `"none"`.

You could also try increasing `min_time_between_impacts` in the `Clatter` constructor, or any of the other parameters that directly affect impacts.

## There are missing impact sounds

Try adjusting any of these constructor parameters:

- `area_new_collision`
- `scrape_angle`
- `impact_area_ratio`
- `roll_angular_speed`
- `min_time_between_impacts`
- `roll_substitute`

## Scrape sounds are too loud

You can fix this in several ways:

- Choose a different scrape material.
- Set `scrape_amp` in the `Clatter` constructor to a lower value.
- Set `scrape_speed` in the `Clatter` constructor to a lower value.

***

**This is the last document in the "Clatter" tutorial.**

[Return to the README](../../../README.md)

***

Example controllers:

- [reset_clatter.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/clatter/reset_clatter.py) A minimal example of how to reset Clatter.

Python API:

- [`ResonanceAudioInitializer`](../../python/add_ons/resonance_audio_intializer.md)
- [`Clatter`](../../python/add_ons/clatter.md)