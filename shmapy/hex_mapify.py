import math
from numpy.core import numeric
import pandas as pd
import numpy as np
import copy
from logzero import logger
import matplotlib.pyplot as plt
from shmapy.input import (
    _read_user_input,
    _read_coordinate_file,
    _extract_coordinates,
)


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


def _handle_categories(value_list, fill_color, categorical_order=None) -> list:
    if categorical_order:
        assert len(fill_color) >= len(categorical_order)
        fill_color = fill_color[: len(categorical_order)]
        color_mapper = dict(zip(categorical_order, fill_color))

    else:
        # If no order is supplied we'll just do things in order
        assert len(fill_color) >= len(set(value_list))
        fill_color = fill_color[: len(set(value_list))]
        color_mapper = dict(zip(set(value_list), fill_color))
    return [color_mapper[i] for i in value_list]


def _create_hex(
    ax,
    coord,
    radius,
    pct,
    # color=["#1d3557","#e63946"],
    fill_color=["#ef476f", "#ffd166", "#06d6a0", "#118ab2"],
    line_color="#ffffff",
    line_width=1,
    chart_type="vbar",
    colormap="viridis",
    categorical_order=None,
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

    # check if pct is a list of values or a single number
    # if it's a length-one list convert it to the value

    if type(pct) == list:
        if len(pct) == 1:
            pct = pct[0]
    assert chart_type in ["vbar", "choropleth", "categorical"]

    if chart_type == "vbar":

        if type(pct) == float:
            """
            if type pct==float, and chart_type=='vbar', the user presumably submitted
            single values between 0 and 1 intending to create a stacked bar chart "progress bar"
            with two values, aka original flavor lone-wolf.
            """
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
                    coord[1]
                    + (radius / (2 * height)) * (height - xoffset)
                    + radius / 2,
                    coord[1] + radius,
                    coord[1]
                    + (radius / (2 * height)) * (height - xoffset)
                    + radius / 2,
                    coord[1] + radius / 2,
                    coord[1],
                ]

                ybottom = [
                    coord[1],
                    coord[1] - radius / 2,
                    coord[1]
                    - ((radius / (2 * height)) * (height - xoffset) + radius / 2),
                    coord[1] - radius,
                    coord[1]
                    - ((radius / (2 * height)) * (height - xoffset) + radius / 2),
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
                ax.plot(x, ytop, color=line_color, linewidth=1)
                ax.plot(x, ybottom, color=line_color, linewidth=1)

    elif chart_type == "choropleth":
        height = np.sqrt(3) / 2 * radius

        x = _set_x(coord[0], height)
        ytop, ybottom = _set_y(coord[1], radius)

        cmap = plt.get_cmap(colormap)
        # see for reference https://matplotlib.org/stable/gallery/lines_bars_and_markers/fill_between_demo.html
        ax.fill_between(x, ytop, ybottom, facecolor=cmap(pct))
        ax.plot(x, ytop, color=line_color, linewidth=line_width)
        ax.plot(x, ybottom, color=line_color, linewidth=line_width)

    else:
        height = np.sqrt(3) / 2 * radius
        x = _set_x(coord[0], height)
        ytop, ybottom = _set_y(coord[1], radius)

        ax.fill_between(x, ytop, ybottom, facecolor=pct)
        ax.plot(x, ytop, color=line_color, linewidth=line_width)
        ax.plot(x, ybottom, color=line_color, linewidth=line_width)
        # assert 2 + 2 == 5

    return ax


def plot_hex(
    # Data
    hcoord,
    vcoord,
    labels,
    pct,
    # chart type
    chart_type="vbar",
    excluded_color="grey",
    # Hex/coloring
    radius=1,
    fill_color=["#ef476f", "#ffd166", "#06d6a0", "#118ab2"],
    line_color="#ffffff",
    line_width=1,
    colormap="viridis",
    # Text Sizing/Coloring
    size=10,
    text_color="#ffffff",
    # Options to save a figure or show figure
    # TODO add this argument to the README
    numeric_labels=None,
    numeric_labels_custom=None,  # let's have this be the location of the custom labels in the df
    # TODO: Remove excluded states as an argument and remap to throw in missing states
    excluded_states=None,
    categorical_order=None,
    out_path=None,
    show_figure=True,
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
    """
    fig, ax = plt.subplots(**kwargs)
    i = 0

    if chart_type == "categorical":
        pct = _handle_categories(
            pct, fill_color=fill_color, categorical_order=categorical_order
        )

    for x, y, p, l in zip(hcoord, vcoord, pct, labels):

        try:
            assert type(excluded_states) == list and l in excluded_states
            temp_color = np.repeat(excluded_color, len(fill_color))
            temp_text_color = "black"
        except:
            temp_color = fill_color
            temp_text_color = text_color
        _create_hex(
            ax,
            [x, y],
            radius=radius,
            pct=p,
            fill_color=temp_color,
            line_color=line_color,
            line_width=line_width,
            chart_type=chart_type,
            colormap=colormap,
            categorical_order=categorical_order,
        )

        l_new = l
        if numeric_labels:
            # numeric labels can be a string called 'all'
            # if it’s all, it adds the percent fill label on the chart for every state
            # if it’s a list, it adds the % label for each state on the list
            # else it just labels the state
            if type(numeric_labels) == str:
                if numeric_labels.lower() == "all":
                    l_new = l + f"\n {str(round(p*100))}%"
            elif len(numeric_labels) >= 1:
                if numeric_labels_custom[i] and l in numeric_labels:
                    l_new = l + f"\n {numeric_labels_custom[i]}"
                else:
                    l_new = l + f"\n {str(round(p*100))}%"

        if numeric_labels_custom is not None:
            l_new = l + "\n" + numeric_labels_custom[i]

        ax.text(
            x,
            y,
            l_new,
            ha="center",
            va="center",
            size=size,
            fontweight="bold",
            color=temp_text_color,
        )
        i += 1

    plt.axis("off")
    if out_path:
        plt.savefig(out_path, bbox_inches="tight", dpi=300)
    if show_figure:
        plt.show()


def us_plot_hex(
    input_df,
    chart_type="vbar",
    excluded_color="grey",
    radius=1,
    size=10,
    fill_color=["#ef476f", "#ffd166", "#06d6a0", "#118ab2", "black", "white"],
    line_color="#ffffff",
    line_width=1,
    text_color="#ffffff",
    colormap="viridis",
    # figsize=(8, 5),
    show_figure=True,
    out_path=None,
    numeric_labels=None,
    numeric_labels_custom=None,
    excluded_states=None,
    categorical_order=None,
    **kwargs,
):
    """
    Expects user to have dataframe with first column as abbreviated states and second column as values.
    All other columns are truncated
    Returns a hex map of the united states based on the user input

    :param input_df: [User provided dataframe, dictionary, or file location. Function will read first two columns as state and value]
    :type input_df: [type]
    :param out_path: [description], defaults to None
    :type out_path: [type], optional
    :param radius: [description], defaults to 1
    :type radius: int, optional
    :param size: [description], defaults to 10
    :type size: int, optional
    :param fill_color: [description], defaults to "#d90429"
    :type fill_color: str, optional
    :param top_color: [description], defaults to "#000000"
    :type top_color: str, optional
    :param line_color: [description], defaults to "#ffffff"
    :type line_color: str, optional
    :param text_color: [description], defaults to "#ffffff"
    :type text_color: str, optional
    :param figsize: [description], defaults to (8, 5)
    :type figsize: tuple, optional
    :return: [description]
    :rtype: [type]
    """
    coordinate_df = _read_coordinate_file()
    input_df = _read_user_input(input_df, chart_type=chart_type)
    input_df = input_df.rename(
        columns={input_df.columns[0]: "state", input_df.columns[1]: "pct"}
    )

    dataset = coordinate_df.merge(input_df, left_on="Abbreviation", right_on="state")
    l, h, v = _extract_coordinates(dataset)

    if numeric_labels_custom:
        custom_labels = dataset[numeric_labels_custom]
    else:
        custom_labels = None

    return plot_hex(
        h,
        v,
        l,
        dataset.pct,
        chart_type=chart_type,
        radius=radius,
        size=size,
        fill_color=fill_color,
        line_color=line_color,
        line_width=line_width,
        text_color=text_color,
        # figsize=figsize,
        colormap=colormap,
        out_path=out_path,
        show_figure=show_figure,
        numeric_labels=numeric_labels,
        numeric_labels_custom=custom_labels,
        excluded_color=excluded_color,
        excluded_states=excluded_states,
        categorical_order=categorical_order,
        **kwargs,
    )
