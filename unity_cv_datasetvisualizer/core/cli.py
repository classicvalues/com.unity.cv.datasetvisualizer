import argparse
import os
import streamlit.bootstrap as bootstrap
from streamlit import config as _config
from pathlib import Path
import sys


def entry():
    main(sys.argv[1:])


def preview(dataset_path):
    """Previews the dataset in a streamlit app."""
    preview_py_file_path = Path(os.path.dirname(__file__)) / "Preview.py"

    config = {
        "theme.primaryColor": "#7792E3",
        "theme.backgroundColor": "#273346",
        "theme.secondaryBackgroundColor": "#B9F1C0",
        "theme.textColor": "#FFFFFF",
        "theme.font": "sans serif"
    }

    for config_key in config.keys():
        _config.set_option(config_key, config[config_key], where_defined="unity_override")

    bootstrap.run(str(preview_py_file_path), "", [dataset_path], {})


def main(arg):
    cli = argparse.ArgumentParser(description="Visualize annotations of synthetic datasets generated using Unity's Perception package.")
    cli.add_argument("-d", "--data", type=str, help='Path to root of dataset', default=None)
    cli.add_argument("-s", "--skip-dataset", help='Run visualizer without selecting a dataset', action='store_true')
    args = cli.parse_args(arg)

    data_folder = args.data or None

    if args.skip_dataset:
        preview(None)
        return

    if data_folder is None:
        cli.print_help()
        return

    final_data_path = Path(data_folder).resolve()
    if not os.path.isdir(final_data_path):
        print("The provided dataset folder does not exist!")
        return

    preview(final_data_path)


if __name__ == "__main__":
    entry()
