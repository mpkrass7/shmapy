import pandas as pd
from logzero import logger
from pathlib import Path
import matplotlib.pyplot as plt

project_directory = Path(__file__).parent


def get_state_coordinates() -> pd.DataFrame:
    # Reads built in state coordinates file
    coords = pd.read_csv(project_directory.joinpath("static", "facet_geo_states.csv"))
    coords.index = [x for x in zip(coords.row, coords.col)]
    return coords


def merge_coordinates(df, coordinates, merge_column) -> pd.DataFrame:
    return coordinates.merge(df, left_on="code", right_on=merge_column, how="left")


def facet_plot_us(
    df,
    function,
    facet_col="state",
    figsize=(16, 12),
    layout_args=None,
    subplot_args=None,
    out_path=None,
    **fwargs
) -> None:
    us_coordinates = get_state_coordinates()

    df_coordinates = merge_coordinates(df, us_coordinates, facet_col)

    valid_coords = list(map(tuple, us_coordinates[["row", "col"]].values))
    # logger.info(df_coordinates.head())
    # Four axes, returned as a 2-d array
    f, ax = plt.subplots(
        max(us_coordinates.row) + 1, max(us_coordinates.col) + 1, figsize=figsize
    )
    df_coordinates["row_col"] = list(map(tuple, df_coordinates[["row", "col"]].values))

    for row_col in valid_coords:
        df_temp = df_coordinates.loc[df_coordinates.row_col == row_col]
        state_cd = us_coordinates.loc[us_coordinates.index == row_col, "code"]
        row, col = row_col
        derp = ax[row, col]

        # derp should take in a plotting function of some kind
        function(derp, df_temp, **fwargs)

    #     derp.title.set_backgroundcolor('lightgray')
    f.tight_layout(pad=0.05)

    for row in range(max(us_coordinates.row) + 1):
        for col in range(max(us_coordinates.col) + 1):
            if (row, col) not in valid_coords:
                ax[row, col].remove()

    plt.show()
    if out_path:
        plt.savefig(out_path)
    return

