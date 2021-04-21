import pytest
import pandas as pd

from shmapy.input import (
    _read_user_input,
    _read_coordinate_file,
    _extract_coordinates,
    read_user_coordinates,
    state_to_abbreviation,
)


@pytest.mark.parametrize(
    "filename,chart_type",
    [
        ("tests/data/demo_input1.csv", "vbar"),
        ("tests/data/demo_input2.csv", "vbar"),
        ("tests/data/demo_input3.csv", "vbar"),
        ("tests/data/demo_input4.csv", "vbar"),
        ("tests/data/demo_input5.csv", "categorical"),
    ],
)
def test_read_user_input(filename, chart_type):

    assert isinstance(
        _read_user_input(filename, chart_type=chart_type), pd.core.frame.DataFrame
    )
