# LerpableFloat

`from tdw.lerp.lerpable_float import LerpableFloat`

A float that can be linearly interpolated between minimum and maximum values.

***

## Fields

- `value` The current value.

- `is_at_target` If True, `self.value` is at its target (the minimum if increasing, the maximum if decreasing).

***

## Functions

#### \_\_init\_\_

\_\_init\_\_

**`LerpableFloat(value)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| value |  T |  | The initial value. |

#### update

**`self.update()`**

Interpolate. If we're done interpolating, stop.

This will set `self.value` to a value between the minimum and maximum.

#### set_target

**`self.set_target(target, dt)`**

Set a new target for `self.value`.

One end of the line between a and b will be `self.value` and the other will be `target`.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| target |  T |  | The target value. |
| dt |  float |  | The *true* value delta per `update()` call. For example, if this is a position and you want move the position by 0.1 meters per `update()` call, then this value should be 0.1. |

#### get_dt

**`self.get_dt()`**

_Returns:_  The signed change in value.