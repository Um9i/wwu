import pytest
from wwu import Box, Orientation


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
        result = b.wwu(10, 10, 10)
        assert 0 <= result <= 5

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


class TestBestOrientation:
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
