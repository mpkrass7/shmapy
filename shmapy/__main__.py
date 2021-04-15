import fire
from shmapy.hex_mapify import us_plot_hex


def main():
    fire.Fire(
        {"plot-hex": us_plot_hex,}
    )

