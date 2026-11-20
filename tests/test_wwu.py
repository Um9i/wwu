import copy
import dataclasses
import pickle

import pytest

from wwu import Box, Orientation


@dataclasses.dataclass(frozen=True)
class SKUBox(Box):
    sku: str = ""


@dataclasses.dataclass(frozen=True, slots=True)
class SlotSKUBox(Box):
    sku: str = ""


class TestWwu:
    def test_wwu(self, box: Box) -> None:
        assert box.wwu(10, 10, 20) == 0
        assert box.wwu(20, 10, 10) == 4

    def test_with_non_fitting_box(self, box: Box) -> None:
        with pytest.raises(ValueError, match="will not fit"):
            box.wwu(10, 10, 10)

    def test_cube_box(self):
        """All permutations of a cube yield the same count, so index 0 is returned."""
        b = Box(10, 10, 10)
        assert b.wwu(20, 20, 20) == 0

    def test_float_dimensions(self):
        b = Box(2.5, 3.5, 4.0)
        assert b.best_orientation(10, 10, 10).box_count == 16

    def test_exact_fit(self):
        """Box dimensions exactly match storage — fits exactly 1."""
        b = Box(5, 10, 15)
        idx = b.wwu(5, 10, 15)
        orient = b.best_orientation(5, 10, 15)
        assert orient.box_count == 1
        assert idx == orient.perm_index

    def test_large_storage(self):
        b = Box(1, 1, 1)
        orient = b.best_orientation(100, 100, 100)
        assert orient.box_count == 1_000_000

    def test_repr(self):
        b = Box(10, 20, 30)
        assert repr(b) == "Box(10, 20, 30)"

    def test_repr_floats(self):
        b = Box(1.5, 2.5, 3.5)
        assert repr(b) == "Box(1.5, 2.5, 3.5)"

    def test_tie_breaking_returns_first_max(self):
        """Orientations 4 and 5 both fit one box, so the lower index wins."""
        b = Box(5, 5, 10)
        assert b.best_orientation(10, 5, 5) == Orientation(4, (10, 5, 5), 1)

    def test_equality_and_hash(self):
        assert Box(1, 2, 3) == Box(1, 2, 3)
        assert Box(1, 2, 3) != Box(3, 2, 1)
        assert len({Box(1, 2, 3), Box(1, 2, 3)}) == 1

    def test_equal_boxes_give_equal_results(self):
        """int(1e23) and 1e23 are equal Python numbers but different measurements."""
        n = int(1e23)
        exact, rounded = Box(n, 1, 1), Box(1e23, 1, 1)
        assert exact != rounded
        assert exact.best_orientation(n, 1, 1).box_count == 1
        with pytest.raises(ValueError, match="will not fit"):
            rounded.best_orientation(n, 1, 1)

    def test_equal_boxes_choose_same_orientation(self):
        """Equal boxes agree on index and count; dimensions keep each box's own values."""
        a, b = Box(10**23, 1, 1), Box(1e23, 1, 1)
        assert a == b
        ra, rb = a.best_orientation(10**23, 1, 1), b.best_orientation(10**23, 1, 1)
        assert (ra.perm_index, ra.box_count) == (rb.perm_index, rb.box_count) == (0, 1)
        assert ra.dimensions == (10**23, 1, 1)
        assert rb.dimensions == (1e23, 1, 1)

    def test_equality_uses_measurements(self):
        assert Box(1, 2, 3) == Box(1.0, 2.0, 3.0)
        assert hash(Box(1, 2, 3)) == hash(Box(1.0, 2.0, 3.0))
        assert Box(0.1, 1, 1) == Box(0.1, 1, 1)
        assert Box(1, 2, 3) != (1, 2, 3)

    @pytest.mark.parametrize("protocol", range(pickle.HIGHEST_PROTOCOL + 1))
    def test_pickle_round_trip(self, protocol):
        b = Box(0.1, 2, 3)
        restored = pickle.loads(pickle.dumps(b, protocol=protocol))
        assert restored == b
        assert restored.dimensions == (0.1, 2, 3)
        assert restored.best_orientation(0.3, 2, 3).box_count == 3

    @pytest.mark.parametrize("slots", [False, True])
    @pytest.mark.parametrize("clone", [copy.copy, copy.deepcopy, lambda b: pickle.loads(pickle.dumps(b))])
    def test_subclass_fields_survive_copy_and_pickle(self, clone, slots):
        restored = clone((SlotSKUBox if slots else SKUBox)(1, 2, 0.1, sku="A-1"))
        assert restored.sku == "A-1"
        assert restored.dimensions == (1, 2, 0.1)
        assert restored.best_orientation(1, 2, 0.3).box_count == 3

    def test_unpickle_rejects_invalid_legacy_state(self):
        data = pickle.dumps(Box(10, 10, 20), protocol=2).replace(b"K\x14", b"K\x00")
        with pytest.raises(ValueError, match="must be positive"):
            pickle.loads(data)

    @pytest.mark.parametrize(
        "data",
        [
            # pickle.dumps(Box(10, 10, 20), protocol=2) under wwu 0.0.4
            b"\x80\x02cwwu.box\nBox\nq\x00)\x81q\x01}q\x02X\n\x00\x00\x00dimensionsq\x03K\nK\nK\x14\x87q\x04sb.",
            # pickle.dumps(Box(10, 10, 20), protocol=5) under wwu 0.0.4
            b"\x80\x05\x95/\x00\x00\x00\x00\x00\x00\x00\x8c\x07wwu.box\x94\x8c\x03Box\x94\x93\x94)\x81\x94}"
            b"\x94\x8c\ndimensions\x94K\nK\nK\x14\x87\x94sb.",
        ],
    )
    def test_unpickle_0_0_4_box(self, data):
        b = pickle.loads(data)
        assert b == Box(10, 10, 20)
        assert b.dimensions == (10, 10, 20)
        assert b.wwu(20, 10, 10) == 4

    def test_immutable(self):
        b = Box(1, 2, 3)
        with pytest.raises(dataclasses.FrozenInstanceError):
            b.height = 0  # type: ignore[misc]

    def test_dimensions(self):
        b = Box(width=2, depth=3, height=1)
        assert b.dimensions == (1, 2, 3)


class TestBestOrientation:
    @pytest.mark.parametrize(("height", "side", "shelf"), [(1, 0.1, 0.3), (1000, 100, 300)])
    def test_same_shelf_in_metres_and_millimetres(self, height, side, shelf):
        result = Box(height, side, side).best_orientation(height, shelf, shelf)
        assert result == Orientation(0, (height, side, side), 9)

    def test_carton_just_too_large(self):
        with pytest.raises(ValueError, match="will not fit"):
            Box(1, 1, 0.30000000000000004).best_orientation(1, 1, 0.3)

    def test_published_shelf_example(self):
        assert Box(20, 30, 20).best_orientation(20, 100, 60) == Orientation(1, (20, 20, 30), 10)

    def test_exact_large_integer_count(self):
        capacity = 2**53 + 1
        assert Box(1, 1, 1).best_orientation(1, 1, capacity).box_count == capacity

    def test_returns_orientation(self, box: Box) -> None:
        result = box.best_orientation(10, 10, 20)
        assert isinstance(result, Orientation)
        assert result.perm_index == 0
        assert result.box_count >= 1
        assert len(result.dimensions) == 3

    def test_non_fitting_box(self, box: Box) -> None:
        with pytest.raises(ValueError, match="will not fit"):
            box.best_orientation(10, 10, 10)

    def test_consistent_with_wwu(self, box: Box) -> None:
        idx = box.wwu(20, 10, 10)
        orient = box.best_orientation(20, 10, 10)
        assert idx == orient.perm_index


class TestValidation:
    def test_negative_box_dimension(self):
        with pytest.raises(ValueError, match="must be positive"):
            Box(-1, 10, 20)

    def test_zero_box_dimension(self):
        with pytest.raises(ValueError, match="must be positive"):
            Box(0, 10, 20)

    def test_non_numeric_box_dimension(self):
        with pytest.raises(TypeError, match="must be a number"):
            Box("ten", 10, 20)  # type: ignore[arg-type]

    def test_negative_storage_dimension(self):
        b = Box(10, 10, 20)
        with pytest.raises(ValueError, match="must be positive"):
            b.wwu(-1, 10, 20)

    def test_zero_storage_dimension(self):
        b = Box(10, 10, 20)
        with pytest.raises(ValueError, match="must be positive"):
            b.wwu(10, 0, 20)

    def test_non_numeric_storage_dimension(self):
        b = Box(10, 10, 20)
        with pytest.raises(TypeError, match="must be a number"):
            b.wwu(10, 10, "twenty")  # type: ignore[arg-type]
