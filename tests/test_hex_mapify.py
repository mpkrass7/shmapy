from numpy.core import numeric
import pytest
import pandas as pd

from shmapy.hex_shmap import us_plot_hex

states_to_test = ["CA", "MD", "PA", "TX"]


@pytest.mark.parametrize(
    "filename,chart_type",
    [
        ("tests/data/demo_input1.csv", "vbar"),
        ("tests/data/demo_input2.csv", "choropleth"),
        ("tests/data/demo_input3.csv", "vbar"),
        ("tests/data/demo_input4.csv", "vbar"),
        ("tests/data/demo_input5.csv", "categorical"),
    ],
)
def test_hex_shmap_default(filename, chart_type):
    us_plot_hex(filename, chart_type=chart_type, show_figure=False)
    assert 1 == 1


@pytest.mark.parametrize(
    "filename,numeric_labels,numeric_labels_custom",
    [
        ("tests/data/demo_input1.csv", "all", None),
        ("tests/data/demo_input2.csv", states_to_test, None),
        ("tests/data/demo_input4.csv", None, "fruit"),
    ],
)
def test_hex_vbar_custom(filename, numeric_labels, numeric_labels_custom):
    us_plot_hex(
        filename,
        chart_type="vbar",
        numeric_labels=numeric_labels,
        numeric_labels_custom=numeric_labels_custom,
        show_figure=False,
    )
    assert 1 == 1


@pytest.mark.parametrize(
    "filename,numeric_labels,numeric_labels_custom",
    [
        ("tests/data/demo_input1.csv", "all", None),
        ("tests/data/demo_input2.csv", states_to_test, None),
        ("tests/data/demo_input4.csv", None, "fruit"),
    ],
)
def test_hex_choropleth_custom(filename, numeric_labels, numeric_labels_custom):
    us_plot_hex(
        filename,
        chart_type="choropleth",
        numeric_labels=numeric_labels,
        numeric_labels_custom=numeric_labels_custom,
        show_figure=False,
    )
    assert 1 == 1


@pytest.mark.parametrize(
    "filename,category_labels",
    [
        ("tests/data/demo_input5.csv", None),
        (
            "tests/data/demo_input5.csv",
            ["Apple", "Banana", "Cherry", "Durian", "Elderberry"],
        ),
    ],
)
def test_hex_categorical_custom(filename, category_labels):
    us_plot_hex(
        filename,
        chart_type="categorical",
        category_labels=category_labels,
        show_figure=False,
    )
    assert 1 == 1
