# WWU

[![CI](https://github.com/Um9i/wwu/actions/workflows/ci.yml/badge.svg)](https://github.com/Um9i/wwu/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/wwu.svg)](https://pypi.org/project/wwu/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**Which Way Up?** — Pack more boxes into less space.

WWU finds the optimal orientation for storing a box in a given storage space, maximising how many fit. Just pass in your box size and storage dimensions, and WWU tells you which way to turn it.

No dependencies. No config. One function call.

## Contents

- [Permutation Index](#permutation-index)
- [Examples](#examples)
- [How It Works](#how-it-works)
- [Limitations](#limitations)
- [Installation](#installation)
- [Requirements](#requirements)
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
b.wwu(10, 10, 20)    # Find the optimal permutation in storage of 10 x 10 x 20
# >>> 0

b.wwu(20, 10, 10)    # Different storage shape picks a different orientation
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
print(result.box_count)   # Number of boxes that fit
```

Dimensions are validated — zero, negative, or non-numeric values raise an error:

```py
Box(-1, 10, 20)       # ValueError: Box height must be positive
b.wwu(10, 10, "ten")  # TypeError: Storage depth must be a number
```

## How It Works

For each of the 6 permutations of the box's `(height, width, depth)`, WWU computes
how many boxes fit along each storage axis independently (`floor(storage_axis / box_axis)`)
and multiplies them together to get a total box count for that orientation. It returns
whichever permutation yields the highest count.

## Limitations

WWU answers "how many identical boxes fit, axis-aligned, in a grid?" — it is not a
general bin-packing or mixed-carton solver. In particular:

- All boxes are assumed to be the same size (one `Box` per call).
- Boxes are placed on a uniform grid along each axis; it does not try irregular or
  interlocking arrangements that could fit more boxes into leftover space.
- Rotations are limited to the 6 axis-aligned permutations of height/width/depth —
  no diagonal or off-axis placement.

## Installation

```
pip install wwu
```

## Requirements

Python 3.9+. No runtime dependencies.

## Contributing

```
git clone https://github.com/Um9i/wwu.git
cd wwu
pip install -e ".[test,lint]"

pytest        # run tests
ruff check .  # lint
```
