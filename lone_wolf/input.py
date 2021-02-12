import pandas as pd
import warnings

def _read_user_input(user_input):
    """
    Accepts dataframe, numpy array dictionary or path to a csv or xlsx file
    Outputs file type converted to pandas dataframe
    """
    # Will delete this once we make all test cases
    # does the input have all 50 states?
    # assert type(user_input) == 'kevin'
    try: 
        if isinstance(user_input, str):
            # this sounds like a path
            if user_input[-4:] == '.csv':
                values = pd.read_csv(user_input)
            elif user_input[-5:-1] == '.xlsx':
                values = pd.read_excel(user_input)
        elif isinstance(user_input, pd.core.frame.DataFrame):
            values = user_input
        elif isinstance(user_input, dict):
             # is it a dictionary 
            values = pd.DataFrame(user_input)
    except ValueError:
       
        pass
    # except:
    #     # Numpy!
    # except:
    #     # is it a file
    values.columns = ['state', 'value']
    values['value'] = values.value.astype(float)
    input_validator(values)
    # I think returning a dataframe is better!
    return values

def _read_coordinate_file():
    # Reads built in state coordinates file
    return pd.read_csv('lone_wolf/static/state_coordinates.csv')

def input_validator(values):
    try:
        assert len(values) == 50 or len(values) == 51
        # make sure abbreviations were converted
        assert all([len(state) == 2 for state in values["state"]])
    except AssertionError:
        warnings.warn("""Expected input should only include 50 or 51 states. 
        Map will have missing hexagons """)
    return values

def state_to_abbreviation(values):
    """Always convert to state abbreviations"""
    # TODO hard code the state abbreviation mapping
    coords = pd.read_csv('lone_wolf/static/state_coordinates.csv')
    state_to_abbrev = dict(zip(coords[["State", "Abbreviation"]]))
    return state_to_abbrev

