import fire
from lone_wolf.hex_mapify import plot_hex


def main():
    fire.Fire(
        {
            "plot-hex": plot_hex,
        }
    )


if __name__ == "__main__":
    main()