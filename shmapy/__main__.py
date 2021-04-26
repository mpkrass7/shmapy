import fire
from shmapy.hex_shmap import us_plot_hex


def main():
    fire.Fire(
        {"plot-hex": us_plot_hex,}
    )

