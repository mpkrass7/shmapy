import pandas as pd
import numpy as np
import warnings


def _read_user_input(user_input):
    """
    Accepts dataframe, numpy array dictionary or path to a csv or xlsx file
    Outputs file type converted to pandas dataframe
    """
    # Will delete this once we make all test cases
    # does the input have all 50 states?
    # assert type(user_input) == 'kevin'
    if isinstance(user_input, pd.core.frame.DataFrame):
        values = user_input
    else:
        try:
            values = pd.read_csv(user_input)
            assert len(values.columns) > 1
        except (pd.parser.CParserError, AssertionError):
            values = pd.read_csv(user_input, sep="\t")
            assert len(values.columns) > 1
        except (pd.parser.CParserError, AssertionError):
            values = pd.read_excel(user_input)
            assert len(values.columns) > 1
        except (pd.parser.CParserError, AssertionError):
            values = pd.DataFrame(user_input)
        except:
            raise "Help! I can't find the data and don't want to be here"

    values = values.iloc[:, :2]
    values.columns = ["state", "value"]

    values["value"] = values.value.astype(float)
    input_validator(values)
    # I think returning a dataframe is better!
    return values


def _read_coordinate_file():
    # Reads built in state coordinates file
    return pd.read_csv("lone_wolf/static/state_coordinates.csv")


def input_validator(values):
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


def state_to_abbreviation(values):
    """Always convert to state abbreviations"""
    # TODO hard code the state abbreviation mapping
    coords = pd.read_csv("lone_wolf/static/state_coordinates.csv")
    state_to_abbrev = dict(zip(coords[["State", "Abbreviation"]]))
    return state_to_abbrev
