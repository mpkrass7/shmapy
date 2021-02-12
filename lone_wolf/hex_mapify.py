import math
import pandas as pd
import matplotlib.pyplot as plt
import input

def create_hex(ax, coord, radius, pct, fill_color = '#d90429', top_color = '#000000', line_color = '#ffffff'):
    
    height = (math.sin(math.radians(60))) * radius
    
    if pct >= 0.25 and pct <= 0.75:
        xoffset = height
    elif pct < 0.25:
        
        xoffset = math.tan(math.radians(60)) * 2 * radius * pct
    else:
        xoffset = math.tan(math.radians(60)) * 2 * radius * (1-pct)
        
    x = [coord[0] - height
         , coord[0] - height
         , coord[0] - xoffset
         , coord[0]
         , coord[0] + xoffset
         , coord[0] + height
         , coord[0] + height
        ]

    ytop = [coord[1]
            , coord[1] + radius/2
            , coord[1] + (radius / (2 * height)) * (height-xoffset) + radius/2
            , coord[1] + radius
            , coord[1] + (radius / (2 * height)) * (height-xoffset) + radius/2
            , coord[1] + radius/2
            , coord[1]
           ]

    ybottom = [coord[1]
               , coord[1] - radius/2
               , coord[1] - ((radius / (2 * height)) * (height-xoffset) + radius/2)
               , coord[1] - radius
               , coord[1] - ((radius / (2 * height)) * (height-xoffset) + radius/2)
               , coord[1] - radius/2
               , coord[1]
              ]       
    
    if pct <= 0.5:
        ymiddle = [ybottom[0]
                   , ybottom[1]
                   , ybottom[2]
                   , ybottom[2]
                   , ybottom[2]
                   , ybottom[1]
                   , ybottom[0]
                  ]
    else:
        ymiddle = [ytop[0]
                   , ytop[1]
                   , ytop[2]
                   , ytop[2]
                   , ytop[2]
                   , ytop[1]
                   , ytop[0]
                  ]

    ax.fill_between(x, ybottom, ymiddle, facecolor = fill_color)
    ax.fill_between(x, ymiddle, ytop, facecolor = top_color)
    ax.plot(x, ytop, color = line_color, linewidth = 4)
    ax.plot(x, ybottom, color = line_color, linewidth = 4)

    return ax

def _extract_coordinates(coords):
    """
    Extract Coordinates from base file
    """ 

    coord = coords[['X', 'Y']].values
    labels = coords.Abbreviation
    hcoord = [c[0] for c in coord]
    vcoord = [c[1] for c in coord]
    return labels, hcoord, vcoord

def _build_map(hcoord, vcoord, labels, pct, radius=1, size=20, color='#ffffff', save_figure=False):
    """
    Builds map using extracted coordinates
    """

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect('equal')

    for x, y, p, l in zip(hcoord, vcoord, pct, labels):
        create_hex(ax, [x, y], radius=radius, pct=p)
        ax.text(x, y, l, ha='center', va='center', size=size, color = color)
    if save_figure:
        plt.savefig('./hex_out.png', dpi=300)
    plt.show()


def build_map(input_df, radius=1, size=20, color='#ffffff', save_figure=False):
    """
    expects user to have dataframe with first column as abbreviated states and second column as values. 
    All other columns are truncated
    Returns a hex map on the user input
    """
    coordinate_df = input._read_coordinate_file()
    df_clean = input_df.copy().iloc[:,:2]
    df_clean.columns = ['state', 'pct']

    dataset = coordinate_df.merge(df_clean, left_on = 'Abbreviation', right_on = 'state')[['Abbreviation', 'X', 'Y', 'pct']]
    
    l,h,v = _extract_coordinates(dataset)
    
    return _build_map(h, v, l, dataset.pct.astype(float))

    

value_df = input._read_user_input('lone_wolf/static/demo_input1.csv')

# df1 = input._read_coordinate_file()
# l, h, v = _extract_coordinates(df1)
# _build_map(h, v, l, value_df.value)

build_map(value_df)