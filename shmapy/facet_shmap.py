import itertools
from pathlib import Path

from logzero import logger
import matplotlib.pyplot as plt
import pandas as pd

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
    state_plotting_function,
    facet_col="state",
    figsize=(16, 12),
    layout_args=None,
    subplot_args=None,
    show_figure=True,
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
        # No, I'm not changing the name derp, I like it
        state_plotting_function(derp, df_temp, **fwargs)

    #     derp.title.set_backgroundcolor('lightgray')
    f.tight_layout(pad=0.05)

    for row in range(max(us_coordinates.row) + 1):
        for col in range(max(us_coordinates.col) + 1):
            if (row, col) not in valid_coords:
                ax[row, col].remove()

    if show_figure:
        plt.show()
    if out_path:
        f.savefig(
            out_path, bbox_inches="tight",
        )
    return


def facet_plot_coordinates(
    df,
    plotting_function,
    facet_col="state",
    row_id="row",
    column_id="column",
    figsize=(16, 12),
    show_figure=True,
    out_path=None,
    **fwargs
) -> None:
    """
    Make a plot faceted by a specified column with placement determined by the user supplied row id and column id 

    :param df: User provided dataframe. Must contain a columns 'row' and 'column' or else be supplied by the user
    :type input_df: DataFrame
    :param plotting_function: User provided function that takes an axis subplot and a single facet of the data frame an an argument to build a plot. See example notebook
    :type plotting_function: sunction
    :param facet_col: User provided column to split charts on. Defaults to 'state'
    :type facet_col: string'
    :param row_id: User provided column to place subplot vertically. Defaults to 'row'
    :type row_id: string'
    :param column_id: User provided column to place subplot horizontally. Defaults to 'column'
    :type column_id: string
    :param figsize: Matplotlib size of figure, defaults to (16, 12)
    :type figsize: tuple, optional
    :param show_figure: Argument to render dataframe. Defaults to True
    :type show_figure: bool, optional
    :param out_path: Location to save image, defaults to None
    :type out_path: string, optional

    :return: None
    :rtype: None
    """
    df_plot = df.copy()
    valid_coords = list(set(map(tuple, df[[row_id, column_id]].values)))
    # logger.info(df_coordinates.head())
    # Four axes, returned as a 2-d array
    row_max, column_max = df[row_id].max() + 1, df[column_id].max() + 1
    f, ax = plt.subplots(row_max, column_max, figsize=figsize)
    df_plot["row_col"] = list(map(tuple, df_plot[[row_id, column_id]].values))

    for row_col in valid_coords:
        df_temp = df_plot.loc[df_plot.row_col == row_col]
        state_cd = df_plot.loc[df_plot.index == row_col, facet_col]
        row, col = row_col
        derp = ax[row, col]

        # derp should take in a plotting function of some kind
        # No, I'm not changing the name derp, I like it
        plotting_function(derp, df_temp, **fwargs)

    #     derp.title.set_backgroundcolor('lightgray')
    f.tight_layout(pad=0.05)

    [
        ax[row, col].remove()
        for row, col in list(itertools.product(range(row_max), range(column_max)))
        if (row, col) not in valid_coords
    ]

    if show_figure:
        plt.show()
    if out_path:
        f.savefig(
            out_path, bbox_inches="tight",
        )
    return
