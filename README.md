# WWU

[![CI](https://github.com/Um9i/wwu/actions/workflows/ci.yml/badge.svg)](https://github.com/Um9i/wwu/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/wwu.svg)](https://pypi.org/project/wwu/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**Which Way Up?** — Pack more boxes into less space.

WWU finds the optimal orientation for storing a box in a given storage space, maximising how many fit. Just pass in your box size and storage dimensions, and WWU tells you which way to turn it.

On a shelf 100 cm wide and 60 cm deep, with 20 cm of clearance, a 30 × 20 × 20 cm carton fits three across and three deep. Turn every carton a quarter turn and five across by two deep gives **10 cartons instead of 9**.

```python
from wwu import Box

carton = Box(20, 30, 20)  # height, width, depth in cm
layout = carton.best_orientation(20, 100, 60)
print(layout.dimensions)  # (20, 20, 30): 20 cm high, 20 cm across, 30 cm deep
print(layout.box_count)  # 10
```

The calculation compares uniform layouts of identical boxes. Use the usable internal dimensions after allowing for clearance.

## Contents

- [Permutation Index](#permutation-index)
- [Examples](#examples)
- [How It Works](#how-it-works)
- [Limitations](#limitations)
- [Installation](#installation)
- [Upgrading from 0.0.4](#upgrading-from-004)
- [Contributing](#contributing)

## Permutation Index

The returned index (0–5) maps to orientation as follows for a box with dimensions `(H, W, D)`:

| Index | Orientation |
|-------|-------------|
| 0     | (H, W, D)  |
| 1     | (H, D, W)  |
| 2     | (W, H, D)  |
| 3     | (W, D, H)  |
| 4     | (D, H, W)  |
| 5     | (D, W, H)  |

## Examples

```py
from wwu import Box

b = Box(10, 10, 20)  # Create a box with 10 x 10 x 20 dimensions.
b.wwu(10, 10, 20)  # Find the optimal permutation in storage of 10 x 10 x 20
# >>> 0

b.wwu(20, 10, 10)  # Different storage shape picks a different orientation
# >>> 4
```

For more detail, use `best_orientation()` which returns the index, the dimension
ordering, and how many boxes fit:

```py
from wwu import Box

b = Box(10, 10, 20)
result = b.best_orientation(40, 20, 20)
print(result.perm_index)  # Orientation index
print(result.dimensions)  # The dimension ordering used
print(result.box_count)  # Number of boxes that fit
```

Dimensions are validated — zero, negative, or non-numeric values raise an error:

```py
Box(-1, 10, 20)  # ValueError: Box height must be positive
b.wwu(10, 10, "ten")  # TypeError: Storage depth must be a number
```

## How It Works

Use the same unit for all six dimensions. WWU takes integers exactly and interprets
each float as the decimal value shown by Python’s `str()`. For example, three
`0.1` m cartons fit along a `0.3` m shelf. A computed dimension such as
`0.1 + 0.2` is treated as `0.30000000000000004` m and exceeds that shelf.

For each of the 6 permutations of the box's `(height, width, depth)`, WWU computes
how many boxes fit along each storage axis independently (`floor(storage_axis / box_axis)`)
and multiplies them together to get a total box count for that orientation. It returns
the lowest permutation index among the layouts with the highest count. If no
orientation fits even one carton, both `wwu()` and `best_orientation()` raise
`ValueError`.

## Limitations

WWU answers "how many identical boxes fit, axis-aligned, in a grid?" — it is not a
general bin-packing or mixed-carton solver. In particular:

- All boxes are assumed to be the same size (one `Box` per call).
- Boxes are placed on a uniform grid along each axis; it does not try irregular or
  interlocking arrangements that could fit more boxes into leftover space.
- Rotations are limited to the 6 axis-aligned permutations of height/width/depth —
  no diagonal or off-axis placement.

## Installation

WWU 0.1.0 requires Python 3.11 or newer and has no runtime dependencies.

```
python -m pip install wwu
```

## Upgrading from 0.0.4

Version 0.0.4 could undercount cartons when decimal measurements divided evenly.
In 0.1.0, this shelf holds nine cartons in either unit:

```python
from wwu import Box

assert Box(1, 0.1, 0.1).best_orientation(1, 0.3, 0.3).box_count == 9  # metres
assert Box(1000, 100, 100).best_orientation(1000, 300, 300).box_count == 9  # millimetres
```

If you use Python 3.9 or 3.10, upgrade Python before installing WWU 0.1.0.
`Box` instances are now immutable. Create a new box when a carton's dimensions
change. Two plain boxes with the same exact height, width, and depth now compare
equal and share a dictionary key. Existing `Box` instances saved with Python's
`pickle` in 0.0.4 can still be loaded.

## Contributing

```
git clone https://github.com/Um9i/wwu.git
cd wwu
pip install -e ".[test,lint]"

pytest        # run tests
ruff check .  # lint
```
