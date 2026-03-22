# WWU

**Which Way Up?** — Pack more boxes into less space.

WWU finds the optimal orientation for storing a box in a given storage space, maximising how many fit. Just pass in your box size and storage dimensions, and WWU tells you which way to turn it.

No dependencies. No config. One function call.

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

## Installation

```
pip install wwu
```

## Tests

```
pytest
```
