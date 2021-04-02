import pytest
import pandas as pd

from lone_wolf.input import (
    _read_user_input,
    _read_coordinate_file,
    _extract_coordinates,
    read_user_coordinates,
    state_to_abbreviation,
)


@pytest.mark.parametrize(
    "filename",
    [
        "tests/data/demo_input1.csv",
        "tests/data/demo_input2.csv",
        "tests/data/demo_input3.csv",
        "tests/data/demo_input4.csv",
    ],
)
def test_read_user_input(filename):

    assert isinstance(_read_user_input(filename), pd.core.frame.DataFrame)
