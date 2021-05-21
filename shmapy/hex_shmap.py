import math
from numpy.core import numeric
import pandas as pd
import numpy as np
import copy
from logzero import logger
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.patches as mpatches
from shmapy.input import (
    _read_user_input,
    _read_coordinate_file,
    _extract_coordinates,
)


default_hex_args = {
    "size": 10,
    "line_color": "#ffffff",
    "line_width": 1,
    "radius": 1,
    "category_labels": None,
    "excluded_color": "lightgrey",
    "colormap": "viridis",
}

default_text_args = {
    "size": 10,
    "text_color": "white",
    "numeric_labels": None,
    "numeric_labels_custom": None,
}

default_missing_args = {"missing_text_color": "grey", "missing_text_fill": "white"}


def _set_x(coord, height):
    x = [
        coord - height,
        coord - height,
        coord - height,
        coord,
        coord + height,
        coord + height,
        coord + height,
    ]
    return x


def _set_y(coord, radius):

    ytop = [
        coord,
        coord + radius / 2,
        coord + radius / 2,
        coord + radius,
        coord + radius / 2,
        coord + radius / 2,
        coord,
    ]

    ybottom = [
        coord,
        coord - radius / 2,
        coord - radius / 2,
        coord - radius,
        coord - radius / 2,
        coord - radius / 2,
        coord,
    ]
    return ytop, ybottom


def _handle_categories(
    value_list: list,
    fill_color: list,
    chart_type: str,
    category_labels: list = None,
    missing_fill_color: str = "white",
) -> list:
    """
    Internal function for handling categories.
    Takes a list of categories, fill_color, and corresponding category labels 
    and returns a mapping from the value to the category label. If no category labels
    are supplied, 

    Parameters
    ----------
    value_list : list
        [description]
    fill_color : list
        [description]
    chart_type : str
        [description]
    category_labels : list, optional
        [description], by default None
    missing_fill_color : str, optional
        [description], by default "white"

    Returns
    -------
    list
        [description]
    """
    if chart_type != "categorical":
        return value_list, category_labels

    if category_labels:
        assert len(fill_color) == len(category_labels)
        # fill_color = fill_color[: len(category_labels)]
        # value_to_override_category = {
        #     val: c for val, c in zip(value_list.unique(), category_labels)
        # }
        # value_list = value_list.apply(lambda row: value_to_override_category[row])

        # Create a dictionary to map a category to a fill
        color_mapper = dict(zip(category_labels, fill_color))
        # Add an entry for missing values
        color_mapper[np.nan] = missing_fill_color
        return [color_mapper[i] for i in value_list], set(color_mapper.keys())

    else:
        # If no order is supplied we'll just do things in order
        assert len(fill_color) >= len(set(value_list))
        fill_color = fill_color[: len(set(value_list))]
        non_na_value_list = [i for i in value_list if i is not None]
        color_mapper = dict(zip(set(non_na_value_list), fill_color))
        color_mapper[np.nan] = missing_fill_color
        return [color_mapper[i] for i in value_list], set(color_mapper.keys())


def _compute_state_text_color(p, text_color, missing_text_color):
    if isinstance(p, list):
        return text_color
    return missing_text_color if pd.isna(p) else text_color


def _handle_numeric_labels(
    l, p, i, numeric_labels=None, custom_label=None, bold_state=True
):
    state_label = l
    if bold_state:
        state_label = r"$\bf{" + state_label + "}$"

    if custom_label is not None:
        # numeric labels can be a string called 'all'
        # if it’s all, it adds the percent fill label on the chart for every state
        # if it’s a list, it adds the % label for each state on the list
        # else it just labels the state
        # Applies to vbar and choropleth Unsure about applying to categories right now..
        l = (
            state_label + f"\n{custom_label[i]}"
            if not pd.isna(custom_label[i])
            else state_label
        )
    elif numeric_labels:
        pval = "" if pd.isna(p) else f"\n{str(round(p*100))}%"
        if type(numeric_labels) == str:
            if numeric_labels.lower() == "all":
                l = state_label + pval
        elif len(numeric_labels) >= 1 and l in numeric_labels:
            l = state_label + pval
    return l


def _create_vbar_hex(
    ax,
    coord,
    radius,
    pct,
    # color=["#1d3557","#e63946"],
    fill_color=["#ef476f", "#ffd166", "#06d6a0", "#118ab2"],
    missing_fill_color="white",
    line_color="#ffffff",
    line_width=1,
):
    """[summary]

    Parameters
    ----------
    ax : [type]
        [description]
    coord : [type]
        [description]
    radius : [type]
        [description]
    pct : [type]
        [description]
    fill_color : str, optional
        The fill of the hexagon, bottom is first color in list, second is second color and so on..
    line_color : str, optional
        [description], by default "#ffffff"

    Returns
    -------
    [type]
        [description]
    """

    if type(pct) == float:
        """
        if type pct==float, and chart_type=='vbar', the user presumably submitted
        single values between 0 and 1 intending to create a stacked bar chart "progress bar"
        with two values, aka original flavor lone-wolf.
        """

        if np.isnan(pct):
            # if pct is nan just do what we do for a choropleth
            height = np.sqrt(3) / 2 * radius
            x = _set_x(coord[0], height)
            ytop, ybottom = _set_y(coord[1], radius)
            ax.fill_between(x, ytop, ybottom, facecolor=missing_fill_color)
            ax.plot(x, ytop, color=line_color, linewidth=line_width)
            ax.plot(x, ybottom, color=line_color, linewidth=line_width)
            return

        area_pct = pct
        # user inputs the percent of area they want colored so we need to translate that into a percent height
        if area_pct < 1 / 6:
            height_for_area_calc = radius * np.sqrt(area_pct * (3 / 2))
            pct = height_for_area_calc / (radius * 2)

        elif (area_pct >= 1 / 6) and (area_pct <= 5 / 6):
            height_for_area_calc = (
                2 * radius * ((3 / 4) * area_pct - (1 / 8)) + radius / 2
            )
            pct = height_for_area_calc / (radius * 2)

        else:
            height_for_area_calc = 2 * radius - (
                np.sqrt((1 - area_pct) * (3 / 2)) * radius
            )
            pct = height_for_area_calc / (radius * 2)

        height = np.sqrt(3) / 2 * radius

        if pct >= 0.25 and pct <= 0.75:
            xoffset = height
        elif pct < 0.25:

            xoffset = math.tan(math.radians(60)) * 2 * radius * pct
        else:
            xoffset = math.tan(math.radians(60)) * 2 * radius * (1 - pct)

        x = [
            coord[0] - height,
            coord[0] - height,
            coord[0] - xoffset,
            coord[0],
            coord[0] + xoffset,
            coord[0] + height,
            coord[0] + height,
        ]

        ytop = [
            coord[1],
            coord[1] + radius / 2,
            coord[1] + (radius / (2 * height)) * (height - xoffset) + radius / 2,
            coord[1] + radius,
            coord[1] + (radius / (2 * height)) * (height - xoffset) + radius / 2,
            coord[1] + radius / 2,
            coord[1],
        ]

        ybottom = [
            coord[1],
            coord[1] - radius / 2,
            coord[1] - ((radius / (2 * height)) * (height - xoffset) + radius / 2),
            coord[1] - radius,
            coord[1] - ((radius / (2 * height)) * (height - xoffset) + radius / 2),
            coord[1] - radius / 2,
            coord[1],
        ]

        if pct < 0.25:
            ymiddle = [
                ybottom[0],
                ybottom[1],
                ybottom[2],
                ybottom[2],
                ybottom[2],
                ybottom[1],
                ybottom[0],
            ]

        elif pct >= 0.25 and pct <= 0.5:
            ymiddle = [
                coord[1] - (radius - (2 * radius * pct)),
                coord[1] - (radius - (2 * radius * pct)),
                coord[1] - (radius - (2 * radius * pct)),
                coord[1] - (radius - (2 * radius * pct)),
                coord[1] - (radius - (2 * radius * pct)),
                coord[1] - (radius - (2 * radius * pct)),
                coord[1] - (radius - (2 * radius * pct)),
            ]
        elif pct > 0.5 and pct <= 0.75:
            ymiddle = [
                coord[1] + (2 * radius * pct - radius),
                coord[1] + (2 * radius * pct - radius),
                coord[1] + (2 * radius * pct - radius),
                coord[1] + (2 * radius * pct - radius),
                coord[1] + (2 * radius * pct - radius),
                coord[1] + (2 * radius * pct - radius),
                coord[1] + (2 * radius * pct - radius),
            ]
        else:
            ymiddle = [
                ytop[0],
                ytop[1],
                ytop[2],
                ytop[2],
                ytop[2],
                ytop[1],
                ytop[0],
            ]

        ax.fill_between(x, ybottom, ymiddle, facecolor=fill_color[0])
        ax.fill_between(x, ymiddle, ytop, facecolor=fill_color[1])
        ax.plot(x, ytop, color=line_color, linewidth=line_width)
        ax.plot(x, ybottom, color=line_color, linewidth=line_width)

        return ax

    elif type(pct) == list:
        """
        if chart_type==vbar and type(pct)==list, we assume the list is a list of values
        that should all add up to 100% for a stacked bar chart
        """
        # normalize the values so they sum to 100
        normalized_pct = [p / sum(pct) for p in pct]
        # define height of each bar (as overlapping bars of increasing height, each starting at 0).
        cumul_pct = []
        for i in range(len(normalized_pct[0:-1])):
            cumul_pct.append(sum(normalized_pct[0 : i + 1]))
        cumul_pct.append(1.0)  # avoiding rounding errors here
        # We draw the bars over each other as if it was a 2-part vbar, tallest one first.
        cumul_pct.reverse()
        list(fill_color).reverse()
        for n, p in enumerate(cumul_pct):

            area_pct = p
            # user inputs the percent of area they want colored so we need to translate that into a percent height
            if area_pct < 1 / 6:
                height_for_area_calc = radius * np.sqrt(area_pct * (3 / 2))
                p = height_for_area_calc / (radius * 2)

            elif (area_pct >= 1 / 6) and (area_pct <= 5 / 6):
                height_for_area_calc = (
                    2 * radius * ((3 / 4) * area_pct - (1 / 8)) + radius / 2
                )
                p = height_for_area_calc / (radius * 2)

            else:
                height_for_area_calc = 2 * radius - (
                    np.sqrt((1 - area_pct) * (3 / 2)) * radius
                )
                p = height_for_area_calc / (radius * 2)

            height = np.sqrt(3) / 2 * radius

            if p >= 0.25 and p <= 0.75:
                xoffset = height
            elif p < 0.25:

                xoffset = math.tan(math.radians(60)) * 2 * radius * p
            else:
                xoffset = math.tan(math.radians(60)) * 2 * radius * (1 - p)

            x = [
                coord[0] - height,
                coord[0] - height,
                coord[0] - xoffset,
                coord[0],
                coord[0] + xoffset,
                coord[0] + height,
                coord[0] + height,
            ]

            ytop = [
                coord[1],
                coord[1] + radius / 2,
                coord[1] + (radius / (2 * height)) * (height - xoffset) + radius / 2,
                coord[1] + radius,
                coord[1] + (radius / (2 * height)) * (height - xoffset) + radius / 2,
                coord[1] + radius / 2,
                coord[1],
            ]

            ybottom = [
                coord[1],
                coord[1] - radius / 2,
                coord[1] - ((radius / (2 * height)) * (height - xoffset) + radius / 2),
                coord[1] - radius,
                coord[1] - ((radius / (2 * height)) * (height - xoffset) + radius / 2),
                coord[1] - radius / 2,
                coord[1],
            ]

            if p < 0.25:
                ymiddle = [
                    ybottom[0],
                    ybottom[1],
                    ybottom[2],
                    ybottom[2],
                    ybottom[2],
                    ybottom[1],
                    ybottom[0],
                ]

            elif p >= 0.25 and p <= 0.5:
                ymiddle = [
                    coord[1] - (radius - (2 * radius * p)),
                    coord[1] - (radius - (2 * radius * p)),
                    coord[1] - (radius - (2 * radius * p)),
                    coord[1] - (radius - (2 * radius * p)),
                    coord[1] - (radius - (2 * radius * p)),
                    coord[1] - (radius - (2 * radius * p)),
                    coord[1] - (radius - (2 * radius * p)),
                ]
            elif p > 0.5 and p <= 0.75:
                ymiddle = [
                    coord[1] + (2 * radius * p - radius),
                    coord[1] + (2 * radius * p - radius),
                    coord[1] + (2 * radius * p - radius),
                    coord[1] + (2 * radius * p - radius),
                    coord[1] + (2 * radius * p - radius),
                    coord[1] + (2 * radius * p - radius),
                    coord[1] + (2 * radius * p - radius),
                ]
            else:
                ymiddle = [
                    ytop[0],
                    ytop[1],
                    ytop[2],
                    ytop[2],
                    ytop[2],
                    ytop[1],
                    ytop[0],
                ]

            ax.fill_between(x, ybottom, ymiddle, facecolor=fill_color[n])
            # ax.fill_between(x, ymiddle, ytop, facecolor=color[1])
            ax.plot(x, ytop, color=line_color, linewidth=line_width)
            ax.plot(x, ybottom, color=line_color, linewidth=line_width)
        return ax


def _create_choropleth_hex(
    fig,
    ax,
    coord,
    radius,
    pct,
    line_color="#ffffff",
    line_width=1,
    colormap="viridis",
    choropleth_axis_label=None,
    missing_fill_color="white",
):

    height = np.sqrt(3) / 2 * radius

    x = _set_x(coord[0], height)
    ytop, ybottom = _set_y(coord[1], radius)

    cmap = plt.get_cmap(colormap)
    # see for reference https://matplotlib.org/stable/gallery/lines_bars_and_markers/fill_between_demo.html
    if np.isnan(pct):
        artist = ax.fill_between(x, ytop, ybottom, facecolor=missing_fill_color)
    else:
        artist = ax.fill_between(x, ytop, ybottom, facecolor=cmap(pct))
    ax.plot(x, ytop, color=line_color, linewidth=line_width)
    ax.plot(x, ybottom, color=line_color, linewidth=line_width)
    return ax, artist


def _create_categorical_hex(
    ax, coord, radius, pct, line_color="#ffffff", line_width=1,
):

    height = np.sqrt(3) / 2 * radius
    x = _set_x(coord[0], height)
    ytop, ybottom = _set_y(coord[1], radius)

    ax.fill_between(x, ytop, ybottom, facecolor=pct)
    ax.plot(x, ytop, color=line_color, linewidth=line_width)
    ax.plot(x, ybottom, color=line_color, linewidth=line_width)
    return ax


def plot_hex(
    # Data
    hcoord,
    vcoord,
    labels,
    pct,
    chart_type,
    fill_color=["#ef476f", "#ffd166", "#06d6a0", "#118ab2"],
    out_path=None,
    show_figure=True,
    missing_kwargs=default_missing_args,
    hex_kwargs=default_hex_args,
    text_kwargs=default_text_args,
    choropleth_axis_label=None,
    category_labels=None,
    **kwargs,
):
    """
    Plotting function that takes in a set of x coordinates, y coordinates, labels, and values
    to generate a hex map with some level of fill.

    :param hcoord: Horizontal Coordinate of the hexagon
    :type hcoord: numeric
    :param vcoord: Vertical Coordinate of the hexagon
    :type vcoord: numeric
    :param labels: [Labels to go inside the hexagon]
    :type labels: str
    :param pct: value (0-1) that a hexgon will be filled on
    :type pct: float
    :param radius: Radius of hexagon, defaults to 1
    :type radius: int, optional
    :param size: Size of labels, defaults to 10
    :type size: int, optional
    :param fill_color: [description], defaults to "#1d3557"
    :type fill_color: str, optional
    :param top_color: [description], defaults to "#e63946"
    :type top_color: str, optional
    :param line_color: [description], defaults to "#ffffff"
    :type line_color: str, optional
    :param text_color: [description], defaults to "#ffffff"
    :type text_color: str, optional
    :param figsize: [description], defaults to (8, 5)
    :type figsize: tuple, optional
    :param out_path: [description], defaults to None
    :type out_path: [type], optional
    :param choropleth_axis_label: Label for the choropleth colorbar.
    :type choropleth_axis_label: str
    :param category_labels: List of strings that describe the categories of the graph. Used in the legend. Defaults to None.
    :type category_labels: list of strings 
    """
    assert chart_type in ["vbar", "choropleth", "categorical"]

    fig, ax = plt.subplots(**kwargs)
    i = 0
    (line_color, line_width, radius, category_labels, colormap,) = (
        hex_kwargs.get("line_color"),
        hex_kwargs.get("line_width"),
        hex_kwargs.get("radius"),
        hex_kwargs.get("category_labels"),
        hex_kwargs.get("colormap"),
    )

    size, text_color, numeric_labels, numeric_labels_custom = (
        text_kwargs.get("size"),
        text_kwargs.get("text_color"),
        text_kwargs.get("numeric_labels"),
        text_kwargs.get("numeric_labels_custom"),
    )

    missing_text_color, missing_fill_color = (
        missing_kwargs.get("missing_text_color"),
        missing_kwargs.get("missing_fill_color"),
    )

    pct, derived_categories = _handle_categories(
        pct,
        fill_color=fill_color,
        chart_type=chart_type,
        category_labels=category_labels,
        missing_fill_color=missing_fill_color,
    )
    # if category_labels is not set, instantiate an empty set in case
    # the user has categories defined in the input file
    if chart_type == "categorical":
        category_labels = derived_categories

    for x, y, p, l in zip(hcoord, vcoord, pct, labels):
        if chart_type == "vbar":

            _create_vbar_hex(
                ax,
                [x, y],
                radius=radius,
                pct=p,
                fill_color=fill_color,
                missing_fill_color=missing_fill_color,
                line_color=line_color,
                line_width=line_width,
            )

        elif chart_type == "choropleth":
            ax, artist = _create_choropleth_hex(
                fig,
                ax,
                [x, y],
                radius=radius,
                pct=p,
                line_color=line_color,
                line_width=line_width,
                colormap=colormap,
                missing_fill_color=missing_fill_color,
                choropleth_axis_label=choropleth_axis_label,
            )

        else:
            _create_categorical_hex(
                ax,
                [x, y],
                radius=radius,
                pct=p,
                line_color=line_color,
                line_width=line_width,
            )

        l_new = _handle_numeric_labels(l, p, i, numeric_labels, numeric_labels_custom)

        state_text_color = _compute_state_text_color(p, text_color, missing_text_color)

        ax.text(
            x,
            y,
            l_new,
            ha="center",
            va="center",
            size=size,
            family="monospace",
            color=state_text_color,
        )
        i += 1

    plt.axis("off")
    if chart_type == "choropleth" and choropleth_axis_label:
        cax = fig.add_axes([0.85, 0.2, 0.03, 0.25], label=choropleth_axis_label)
        cax.set_xlabel(choropleth_axis_label)
        fig.colorbar(artist, cax=cax, ax=ax)
        ax.axis("off")

    if category_labels:
        # custom legend
        patches = []
        for color, label in zip(fill_color, category_labels):
            patches.append(mpatches.Patch(color=color, label=label))
        ax.legend(handles=patches, frameon=False)
    if out_path:
        plt.savefig(out_path, bbox_inches="tight", dpi=300)
    if show_figure:
        plt.show()


def us_plot_hex(
    input_df,
    chart_type="vbar",
    radius=1,
    size=10,
    fill_color=["#ef476f", "#ffd166", "#06d6a0", "#118ab2", "black", "white"],
    category_labels=None,
    line_color="#ffffff",
    line_width=1,
    text_color="#ffffff",
    colormap="viridis",
    numeric_labels=None,
    numeric_labels_custom=None,
    missing_text_color="grey",
    missing_fill_color="white",
    show_figure=True,
    out_path=None,
    choropleth_axis_label=None,
    **kwargs,
):
    """
    Expects user to have dataframe with first column as abbreviated states and second column as values.
    All other columns are truncated
    Returns a hex map of the united states based on the user input

    :param input_df: User provided dataframe, dictionary, or file location. Function will read first two columns as state and value
    :type input_df: [type]
    :param out_path: Location to save image, defaults to None
    :type out_path: [type], optional
    :param radius: size of hexagon, defaults to 1
    :type radius: int, optional
    :param size: size of text, defaults to 10
    :type size: int, optional
    :param fill_color: list of colors to fill the hex map with. Not used in choropleth map
    :type fill_color: str, optional
    :param category_labels: List of strings that describe the categories of the graph. Used in the legend.
    Note that the order input for the categories should match the order input for fill colors to map them properly.
    If no category labels are specified, the mapping will be determined alphabetically
    :type category_labels: list of strings 
    :param line_color: The outline of the hexagons. Black usually looks pretty good, defaults to "#ffffff"
    :type line_color: str, optional
    :param text_color: [description], defaults to "#ffffff"
    :type text_color: str, optional
    :param figsize: Matplotlib size of figure, defaults to (8, 5)
    :type figsize: tuple, optional
    :param choropleth_axis_label: Label for the choropleth colorbar.
    :type choropleth_axis_label: str
    :return: [description]
    :rtype: [type]
    """
    coordinate_df = _read_coordinate_file()
    input_df = _read_user_input(input_df, chart_type=chart_type)
    input_df = input_df.rename(
        columns={
            input_df.columns[0]: "state",
            input_df.columns[1]: "pct",
            # input_df.columns[2]: "value",
        }
    )

    dataset = coordinate_df.merge(
        input_df, how="left", left_on="Abbreviation", right_on="state"
    )
    l, h, v = _extract_coordinates(dataset)

    if numeric_labels_custom:
        custom_labels = dataset[numeric_labels_custom].fillna(np.nan)
    else:
        custom_labels = None

    hex_args = {
        "line_color": line_color,
        "line_width": line_width,
        "radius": radius,
        "category_labels": category_labels,
        "colormap": colormap,
    }

    text_args = {
        "size": size,
        "text_color": text_color,
        "numeric_labels": numeric_labels,
        "numeric_labels_custom": custom_labels,
    }

    missing_kwargs = {
        "missing_text_color": missing_text_color,
        "missing_fill_color": missing_fill_color,
    }

    return plot_hex(
        h,
        v,
        l,
        dataset.pct,
        chart_type=chart_type,
        fill_color=fill_color,
        out_path=out_path,
        show_figure=show_figure,
        missing_kwargs=missing_kwargs,
        hex_kwargs=hex_args,
        text_kwargs=text_args,
        choropleth_axis_label=choropleth_axis_label,
        category_labels=category_labels,
        **kwargs,
    )

