import pytest
from wwu import Box


@pytest.fixture(scope="class")
def box() -> Box:
    return Box(10, 10, 20)
