import math
from numpy.core import numeric
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from lone_wolf.input import (
    _read_user_input,
    _read_coordinate_file,
    _extract_coordinates,
    input_validator,
    state_to_abbreviation,
)


def _create_hex(
    ax,
    coord,
    radius,
    pct,
    #color=["#1d3557","#e63946"],
    color=["#ef476f","#ffd166", "#06d6a0","#118ab2"],
    line_color="#ffffff",
    chart_type='vbar',
    colormap='viridis'
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
        [description], by default "#1d3557"
    top_color : str, optional
        [description], by default "#e63946"
    line_color : str, optional
        [description], by default "#ffffff"

    Returns
    -------
    [type]
        [description]
    """
    #check if pct is a list of values or a single number
    #if it's a length-one list convert it to the value
    
    if type(pct)==list:
        if len(pct)==1:
            pct[0]
        
    if chart_type=='vbar':

        if type(pct)==float:
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
                height_for_area_calc = 2 * radius * ((3 / 4) * area_pct - (1 / 8)) + radius / 2
                pct = height_for_area_calc / (radius * 2)

            else:
                height_for_area_calc = 2 * radius - (np.sqrt((1 - area_pct) * (3 / 2)) * radius)
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
            
            elif pct>=0.25 and pct <=0.5:
                ymiddle = [
                coord[1] - (radius-(2*radius*pct)),
                coord[1] - (radius-(2*radius*pct)),
                coord[1] - (radius-(2*radius*pct)),
                coord[1] - (radius-(2*radius*pct)),
                coord[1] - (radius-(2*radius*pct)),
                coord[1] - (radius-(2*radius*pct)),
                coord[1] - (radius-(2*radius*pct))
                ] 
            elif pct>0.5 and pct <=0.75:
                ymiddle = [
                coord[1] + (2*radius*pct-radius),
                coord[1] + (2*radius*pct-radius),
                coord[1] + (2*radius*pct-radius),
                coord[1] + (2*radius*pct-radius),
                coord[1] + (2*radius*pct-radius),
                coord[1] + (2*radius*pct-radius),
                coord[1] + (2*radius*pct-radius),
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

            ax.fill_between(x, ybottom, ymiddle, facecolor=color[0])
            ax.fill_between(x, ymiddle, ytop, facecolor=color[1])
            ax.plot(x, ytop, color=line_color, linewidth=1)
            ax.plot(x, ybottom, color=line_color, linewidth=1)
            
        elif type(pct)==list:
            """
            if chart_type==vbar and type(pct)==list, we assume the list is a list of values
            that should all add up to 100% for a stacked bar chart
            """
            #normalize the values so they sum to 100
            normalized_pct=[p/sum(pct) for p in pct]
            #define height of each bar (as overlapping bars of increasing height, each starting at 0).
            cumul_pct=[]
            for i in range(len(normalized_pct[0:-1])):
                cumul_pct.append(sum(normalized_pct[0:i+1]))
            cumul_pct.append(1.0) #avoiding rounding errors here
            #We draw the bars over each other as if it was a 2-part vbar, tallest one first.
            cumul_pct.reverse()
            color.reverse()
            print(cumul_pct)
            for n,p in enumerate(cumul_pct):
                  
                area_pct = p
                # user inputs the percent of area they want colored so we need to translate that into a percent height
                if area_pct < 1 / 6:
                    height_for_area_calc = radius * np.sqrt(area_pct * (3 / 2))
                    p = height_for_area_calc / (radius * 2)

                elif (area_pct >= 1 / 6) and (area_pct <= 5 / 6):
                    height_for_area_calc = 2 * radius * ((3 / 4) * area_pct - (1 / 8)) + radius / 2
                    p = height_for_area_calc / (radius * 2)

                else:
                    height_for_area_calc = 2 * radius - (np.sqrt((1 - area_pct) * (3 / 2)) * radius)
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

                elif p>=0.25 and p <=0.5:
                    ymiddle = [
                    coord[1] - (radius-(2*radius*p)),
                    coord[1] - (radius-(2*radius*p)),
                    coord[1] - (radius-(2*radius*p)),
                    coord[1] - (radius-(2*radius*p)),
                    coord[1] - (radius-(2*radius*p)),
                    coord[1] - (radius-(2*radius*p)),
                    coord[1] - (radius-(2*radius*p))
                    ] 
                elif p>0.5 and p <=0.75:
                    ymiddle = [
                    coord[1] + (2*radius*p-radius),
                    coord[1] + (2*radius*p-radius),
                    coord[1] + (2*radius*p-radius),
                    coord[1] + (2*radius*p-radius),
                    coord[1] + (2*radius*p-radius),
                    coord[1] + (2*radius*p-radius),
                    coord[1] + (2*radius*p-radius),
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

                ax.fill_between(x, ybottom, ymiddle, facecolor=color[n])
                #ax.fill_between(x, ymiddle, ytop, facecolor=color[1])
                ax.plot(x, ytop, color=line_color, linewidth=1)
                ax.plot(x, ybottom, color=line_color, linewidth=1)
        
    elif chart_type=='chloropleth':
       
        height = np.sqrt(3) / 2 * radius
        xoffset=height

        x = [
            coord[0] - height,
            coord[0] - height,
            coord[0] - height,
            coord[0],
            coord[0] + height,
            coord[0] + height,
            coord[0] + height,
        ]

        ytop = [
            coord[1],
            coord[1] + radius / 2,
            coord[1] + radius / 2,
            coord[1] + radius,
            coord[1] + radius / 2,
            coord[1] + radius / 2,
            coord[1],
        ]

        ybottom = [
            coord[1],
            coord[1] - radius / 2,
            coord[1] - radius / 2,
            coord[1] - radius,
            coord[1] - radius / 2,
            coord[1] - radius / 2,
            coord[1],
        ]

        cmap=plt.get_cmap(colormap)
        # see for reference https://matplotlib.org/stable/gallery/lines_bars_and_markers/fill_between_demo.html
        ax.fill_between(x, ytop, ybottom, facecolor=cmap(pct))
        ax.plot(x, ytop, color=line_color, linewidth=1)
        ax.plot(x, ybottom, color=line_color, linewidth=1)
       
        
    else:
        print('Chart type options: vbar, chloropleth')

    return ax


def plot_hex(
    # Data
    hcoord,
    vcoord,
    labels,
    pct,
    # TODO add this argument to the README
    numeric_labels=None,
    # fill_booleans=None,
    # Hex/coloring
    radius=1,
    color=["#ef476f","#ffd166", "#06d6a0","#118ab2"],
    line_color="#ffffff",
    colormap='viridis',
    # Text Sizing/Coloring
    size=10,
    text_color="#ffffff",
    #chart type
    chart_type='vbar',
    # Options to save a figure or show figure
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

    for x, y, p, l in zip(hcoord, vcoord, pct, labels):
        _create_hex(
            ax,
            [x, y],
            radius=radius,
            pct=p,
            color=["#ef476f","#ffd166", "#06d6a0","#118ab2"],
            line_color=line_color,
            chart_type=chart_type,
            colormap=colormap
        )
        if numeric_labels and numeric_labels.lower() == "all":
            l_new = l + f"\n {str(round(p*100))}%"
        elif numeric_labels:
            if l in numeric_labels:
                l_new = l + f"\n {str(round(p*100))}%"
            else:
                l_new = l
        else:
            l_new = l
        ax.text(x, y, l_new, ha="center", va="center", size=size, color=text_color)

    plt.axis("off")
    if out_path:
        plt.savefig(out_path, bbox_inches="tight", dpi=300)
    if show_figure:
        plt.show()


def us_plot_hex(
    input_df,
    out_path=None,
    numeric_labels=None,
    radius=1,
    size=10,
    color=["#ef476f","#ffd166", "#06d6a0","#118ab2"],
    line_color="#ffffff",
    text_color="#ffffff",
    # figsize=(8, 5),
    show_figure=True,
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
    input_df = _read_user_input(input_df)
    input_df.columns = ["state", "pct"]

    dataset = coordinate_df.merge(input_df, left_on="Abbreviation", right_on="state")[
        ["Abbreviation", "X", "Y", "pct"]
    ]

    l, h, v = _extract_coordinates(dataset)

    return plot_hex(
        h,
        v,
        l,
        dataset.pct,
        numeric_labels=numeric_labels,
        radius=radius,
        size=size,
        color=color,
        line_color=line_color,
        text_color=text_color,
        # figsize=figsize,
        out_path=out_path,
        show_figure=show_figure,
        **kwargs,
    )
