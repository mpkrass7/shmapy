import pytest

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from shmapy.facet_shmap import facet_plot_us, get_state_coordinates


@pytest.mark.parametrize("message,show_figure", [("Hi", False)])
def test_facet_shmap(message, show_figure):
    print(message)
    # Define a function to make a scatter_plot
    def scatter_a_state(ax, df):

        state_name = list(df.state)[0]

        ax.scatter(df.x, df.y, color=df.color)
        ax.set_title(state_name, loc="center", size=12, y=0.95)
        ax.get_xaxis().set_ticks([])
        ax.get_yaxis().set_ticks([])
        return

    states = pd.DataFrame(np.repeat(list(get_state_coordinates()["code"]), 20)).rename(
        columns={0: "state"}
    )
    states["x"] = np.random.random(states.shape[0])
    states["y"] = np.random.random(states.shape[0]) + (1 * states.index)
    states["color"] = np.random.choice(
        ["#ef476f", "#ffd166", "#06d6a0", "#118ab2"], states.shape[0]
    )

    facet_plot_us(states, scatter_a_state, facet_col="state", show_figure=show_figure)

