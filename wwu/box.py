from itertools import permutations
from math import floor
from typing import NamedTuple


class Orientation(NamedTuple):
    perm_index: int
    dimensions: tuple[float, ...]
    box_count: int


def _validate_dimensions(height: object, width: object, depth: object, label: str = "Dimensions") -> None:
    for name, val in [("height", height), ("width", width), ("depth", depth)]:
        if not isinstance(val, (int, float)):
            raise TypeError(f"{label} {name} must be a number, got {type(val).__name__}")
        if val <= 0:
            raise ValueError(f"{label} {name} must be positive, got {val}")


class Box:
    """A box with height, width, and depth that can be oriented optimally for storage."""

    def __init__(self, height: float, width: float, depth: float):
        """Create a box with the given dimensions.

        Args:
            height: The height of the box (must be positive).
            width: The width of the box (must be positive).
            depth: The depth of the box (must be positive).

        Raises:
            ValueError: If any dimension is zero or negative.
            TypeError: If any dimension is not a number.
        """
        _validate_dimensions(height, width, depth, label="Box")
        self.dimensions = (height, width, depth)

    def __repr__(self) -> str:
        return f"Box({self.dimensions[0]}, {self.dimensions[1]}, {self.dimensions[2]})"

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
        _validate_dimensions(height, width, depth, label="Storage")
        perms: list[int] = []
        for perm in permutations(self.dimensions):
            # We want floored values here because boxes are solid objects.
            perms.append(
                floor(height / perm[0])
                * floor(width / perm[1])
                * floor(depth / perm[2])
            )
        if max(perms) > 0:
            return perms.index(max(perms))
        raise ValueError("Box will not fit in storage.")

    def best_orientation(self, height: float, width: float, depth: float) -> Orientation:
        """Find the optimal orientation with full details.

        Like ``wwu()``, but returns a named tuple with the orientation index,
        the resulting dimension ordering, and how many boxes fit.

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
        perms_list = list(permutations(self.dimensions))
        counts: list[int] = []
        for perm in perms_list:
            counts.append(
                floor(height / perm[0])
                * floor(width / perm[1])
                * floor(depth / perm[2])
            )
        best = max(counts)
        if best > 0:
            idx = counts.index(best)
            return Orientation(perm_index=idx, dimensions=perms_list[idx], box_count=best)
        raise ValueError("Box will not fit in storage.")
