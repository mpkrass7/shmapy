import pytest
import pandas as pd

from shmapy.hex_mapify import us_plot_hex, plot_hex


@pytest.mark.parametrize(
    "filename,chart_type,show_figure",
    [
        ("tests/data/demo_input1.csv", "vbar", "False"),
        ("tests/data/demo_input2.csv", "choropleth", "False"),
        ("tests/data/demo_input3.csv", "vbar", "False"),
        ("tests/data/demo_input4.csv", "vbar", "False"),
        ("tests/data/demo_input5.csv", "categorical", "False"),
    ],
)
def test_read_user_input(filename, chart_type, show_figure):
    us_plot_hex(filename, chart_type=chart_type, show_figure=show_figure)
    assert 1 == 1

