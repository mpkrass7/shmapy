import pandas as pd
import numpy as np
import warnings
import ast
from logzero import logger
from pathlib import Path
from pandas.errors import ParserError


project_directory = Path(__file__).parent


def _read_coordinate_file():
    # Reads built in state coordinates file
    return pd.read_csv(project_directory.joinpath("static", "state_coordinates.csv"))


def _extract_coordinates(coords):
    """
    Extract Coordinates from base file
    """

    coord = coords[["X", "Y"]].values
    labels = coords.Abbreviation
    hcoord = [c[0] for c in coord]
    vcoord = [c[1] for c in coord]
    return labels, hcoord, vcoord


def read_user_coordinates(df):
    # Read in of X, Y, label coordinates for hexagons
    df.columns = ["X", "Y", "Abbreviation"]

    l, h, v = _extract_coordinates(df)

    return l, h, v


def state_to_abbreviation(values):
    """Always convert to state abbreviations"""
    coords = _read_coordinate_file()
    state_to_abbrev = dict(zip(coords["State"], coords["Abbreviation"]))
    values["state"] = values["state"].apply(
        lambda row: state_to_abbrev[row] if row in state_to_abbrev else row
    )

    return values


def state_validator(values):
    try:
        assert len(values) == 50 or len(values) == 51
        # make sure abbreviations were converted
        assert all([len(state) == 2 for state in values["state"]])
    except AssertionError:
        warnings.warn(
            """
        Expected input should only include 50 or 51 states. 
        Map will have missing hexagons
         """
        )


def rescale_data(values):

    # if the values aren't lists, we rescale each value to be between 0 and 1 with min and max set by the whole dataset.
    # if there are list values, that means the user wants a stacked bar chart, and each list is set to sum to 1 in hexmapify.
    # actually I do not think this should be part of the input validation.

    if sum([type(i) == list for i in values.value]) == 0:
        values["_original"] = values["value"].copy()
        try:
            assert max(values.value) <= 1 and min(values.value) >= 0
        except AssertionError:
            warnings.warn(
                """
                Expected values are between 0 and 1. 
                Rescaling values so that max is 1 and min is 0
                """
            )
            # Scale values to be between 0 1
            values["value"] = np.interp(
                values.value, (values.value.min(), values.value.max()), (0.0, 1.0)
            )

    return values


def _read_user_input(user_input, chart_type="vbar") -> pd.DataFrame:
    """
    Accepts dataframe, numpy array dictionary or path to a csv or xlsx file
    Outputs file type converted to pandas dataframe
    """
    # Will delete this once we make all test cases
    # does the input have all 50 states?

    if isinstance(user_input, pd.core.frame.DataFrame):
        values = user_input
    else:
        try:
            values = pd.read_csv(user_input)
            assert len(values.columns) > 1
        except (ParserError, AssertionError):
            values = pd.read_csv(user_input, sep="\t")
            assert len(values.columns) > 1
        except (ParserError, AssertionError):
            values = pd.read_excel(user_input)
            assert len(values.columns) > 1
        except (ParserError, AssertionError):
            values = pd.DataFrame(user_input)
        # except:
        #     raise "Help! I can't find the data and don't want to be here"
    values = values.rename(
        columns={values.columns[0]: "state", values.columns[1]: "value"}
    )
    # users can input either a single float between 0-1 or a list of numerical values
    # ast.literal_eval is picky about which datatypes it evals so we convert to string first
    # so that the value can become either number or list

    values["value"] = values.value.astype(str)
    try:
        values["value"] = values.value.apply(ast.literal_eval)
    except ValueError:
        assert chart_type == "categorical"
        assert len(set(values.value)) <= 50

    # convert to state abbreviations
    values = state_to_abbreviation(values)
    # validate the input

    state_validator(values)

    if chart_type == "categorical":
        return values
    else:
        return rescale_data(values)

