import fire
from lone_wolf.hex_mapify import us_plot_hex


def main():
    fire.Fire(
        {"plot-hex": us_plot_hex,}
    )


if __name__ == "__main__":
    main()
