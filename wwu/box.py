from dataclasses import dataclass, field
from fractions import Fraction
from itertools import permutations
from math import isfinite, prod
from typing import Any, NamedTuple

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


@dataclass(frozen=True, repr=False, eq=False)
class Box:
    """A box with height, width, and depth that can be oriented optimally for storage.

    Boxes are immutable. Two boxes are equal, and hash alike, when their
    dimensions have the same exact measurements (see "How It Works" in the
    README). For the same storage, equal boxes choose the same orientation
    index and box count. The returned ``Orientation.dimensions`` keep each
    box's own values, so ``Box(10**23, 1, 1)`` reports the int ``10**23``
    and the equal ``Box(1e23, 1, 1)`` reports the float ``1e23``. As with
    dataclass equality, only boxes of exactly the same type are compared, so a
    ``Box`` never equals an instance of a subclass.

    Unpickling and copying validate the dimensions for ``Box`` and for subclasses
    that do not define their own ``__setstate__``. A dataclass subclass declared
    with ``slots=True`` generates its own ``__setstate__``, which restores fields
    without checking them.

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
    _exact: tuple[Fraction, Fraction, Fraction] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        _validate_dimensions(self.height, self.width, self.depth, label="Box")
        object.__setattr__(self, "_exact", tuple(map(_measurement, self.dimensions)))

    def __repr__(self) -> str:
        return f"Box({self.height}, {self.width}, {self.depth})"

    def __eq__(self, other: object) -> bool:
        if type(other) is not type(self):
            return NotImplemented
        return self._exact == other._exact

    def __hash__(self) -> int:
        return hash(self._exact)

    def __setstate__(self, state: Any) -> None:
        # The default pickle state is the instance dict, or (dict, slots) when a
        # subclass adds __slots__. Restoring every entry keeps subclass fields.
        state, slot_state = state if isinstance(state, tuple) else (state, None)
        values = {**(state or {}), **(slot_state or {})}
        # wwu 0.0.x pickled a Box as {"dimensions": (height, width, depth)}.
        if "dimensions" in values:
            values["height"], values["width"], values["depth"] = values.pop("dimensions")
        values.pop("_exact", None)  # Recomputed below from the validated dimensions.
        for name, value in values.items():
            object.__setattr__(self, name, value)
        Box.__post_init__(self)

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
        carton = self._exact
        counts = [
            prod(space // carton[axis] for space, axis in zip(storage, axes, strict=True))
            for axes in _AXIS_ORDERS
        ]
        best = max(range(len(counts)), key=counts.__getitem__)  # first index wins ties
        if not counts[best]:
            raise ValueError("Box will not fit in storage.")
        return Orientation(best, tuple(dimensions[axis] for axis in _AXIS_ORDERS[best]), counts[best])
