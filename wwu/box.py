from dataclasses import dataclass
from fractions import Fraction
from itertools import permutations
from math import isfinite, prod
from typing import NamedTuple

# Axis orders for the six orientations, in ``itertools.permutations`` order (indexes 0-5).
_AXIS_ORDERS = tuple(permutations(range(3)))


class Orientation(NamedTuple):
    perm_index: int
    dimensions: tuple[float, float, float]
    box_count: int


def _validate_dimensions(height: object, width: object, depth: object, label: str = "Dimensions") -> None:
    for name, val in (("height", height), ("width", width), ("depth", depth)):
        if isinstance(val, bool) or not isinstance(val, (int, float)):
            raise TypeError(f"{label} {name} must be a number, got {type(val).__name__}")
        if isinstance(val, float) and not isfinite(val):
            raise ValueError(f"{label} {name} must be finite, got {val}")
        if val <= 0:
            raise ValueError(f"{label} {name} must be positive, got {val}")


def _measurement(value: int | float) -> Fraction:
    return Fraction(str(value)) if isinstance(value, float) else Fraction(value)


@dataclass(frozen=True, repr=False)
class Box:
    """A box with height, width, and depth that can be oriented optimally for storage.

    Boxes are immutable and compare equal when their dimensions are equal.

    Args:
        height: The height of the box (must be positive).
        width: The width of the box (must be positive).
        depth: The depth of the box (must be positive).

    Raises:
        ValueError: If any dimension is zero, negative, or not finite.
        TypeError: If any dimension is not a number.
    """

    height: float
    width: float
    depth: float

    def __post_init__(self) -> None:
        _validate_dimensions(self.height, self.width, self.depth, label="Box")

    def __repr__(self) -> str:
        return f"Box({self.height}, {self.width}, {self.depth})"

    @property
    def dimensions(self) -> tuple[float, float, float]:
        """The box's ``(height, width, depth)``."""
        return (self.height, self.width, self.depth)

    def wwu(self, height: float, width: float, depth: float) -> int:
        """Find the optimal orientation index for storing this box.

        Supplied with the storage dimensions, returns the index (0-5) of the
        permutation of box dimensions that maximises the number of boxes fitting
        in the storage space.

        Args:
            height: Storage space height (must be positive).
            width: Storage space width (must be positive).
            depth: Storage space depth (must be positive).

        Returns:
            An integer 0-5 representing the best orientation permutation index.

        Raises:
            ValueError: If the box does not fit in any orientation, or if any
                storage dimension is zero or negative.
            TypeError: If any storage dimension is not a number.
        """
        return self.best_orientation(height, width, depth).perm_index

    def best_orientation(self, height: float, width: float, depth: float) -> Orientation:
        """Find the optimal orientation with full details.

        Like ``wwu()``, but returns a named tuple with the orientation index,
        the resulting dimension ordering, and how many boxes fit. When several
        orientations fit the same number of boxes, the lowest index wins.

        Args:
            height: Storage space height (must be positive).
            width: Storage space width (must be positive).
            depth: Storage space depth (must be positive).

        Returns:
            An ``Orientation(index, dimensions, count)`` named tuple.

        Raises:
            ValueError: If the box does not fit in any orientation.
            TypeError: If any storage dimension is not a number.
        """
        _validate_dimensions(height, width, depth, label="Storage")
        dimensions = self.dimensions
        storage = tuple(map(_measurement, (height, width, depth)))
        carton = tuple(map(_measurement, dimensions))
        counts = [
            prod(space // carton[axis] for space, axis in zip(storage, axes, strict=True))
            for axes in _AXIS_ORDERS
        ]
        best = max(range(len(counts)), key=counts.__getitem__)  # first index wins ties
        if not counts[best]:
            raise ValueError("Box will not fit in storage.")
        return Orientation(best, tuple(dimensions[axis] for axis in _AXIS_ORDERS[best]), counts[best])
