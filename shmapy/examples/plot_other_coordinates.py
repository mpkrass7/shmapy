import numpy as np
import string
from shmapy.hex_mapify import plot_vbar_hex

# Generate hexagons next to each other
coord = [
    [0, 0, 0],
    [0, 1, -1],
    [-1, 1, 0],
    [-1, 0, 1],
    [0, -1, 1],
    [1, -1, 0],
    [1, 0, -1],
]
# Horizontal cartesian coords
hcoord = [c[0] for c in coord]

# Vertical cartersian coords
vcoord = [2.0 * np.sin(np.radians(60)) * (c[1] - c[2]) / 3.0 for c in coord]

# Random 2 letter abbreviations
unique_labels = [
    "".join(np.random.choice(list(string.ascii_uppercase), size=2))
    for _ in range(len(hcoord))
]
value = np.random.random(len(hcoord))

# Run supporting plotting function
plot_vbar_hex(
    hcoord,
    vcoord,
    unique_labels,
    value,
    radius=0.5,
    # numeric_labels=numeric_labels,
    figsize=(5, 5),
)
