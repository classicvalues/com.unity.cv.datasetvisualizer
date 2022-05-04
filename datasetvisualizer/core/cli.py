import argparse
import os
import sys
from pathlib import Path

import streamlit.bootstrap as bootstrap
from streamlit import config as _config

from datasetvisualizer.helpers import ui


def entry():
    if len(sys.argv) == 0:
        return True
    main(sys.argv[1:])


def preview(dataset_path):
    """Previews the dataset in a streamlit app."""
    preview_py_file_path = Path(os.path.dirname(__file__)) / "Preview.py"

    config = {
        "theme.primaryColor": "#794504",
        "theme.backgroundColor": "#FBFBFB",
        "theme.secondaryBackgroundColor": "#F7F2EE",
        "theme.textColor": "#262629",
        "theme.font": "sans serif",
    }

    for config_key in config.keys():
        _config.set_option(
            config_key, config[config_key], where_defined="unity_override"
        )

    bootstrap.run(str(preview_py_file_path), "", [dataset_path], {})


def main(arg):
    cli = argparse.ArgumentParser(
        description="Visualize annotations of synthetic datasets generated using Unity's Perception package."
    )
    cli.add_argument(
        "-o",
        "--open-folder-selector",
        help="open native folder selection window to select path to the root of a dataset",
        action="store_true",
    )
    cli.add_argument(
        "-s",
        "--skip-dataset",
        help="run visualizer without selecting a dataset through the CLI",
        action="store_true",
    )
    cli.add_argument(
        "-d",
        "--data",
        type=str,
        help="text path to the root of a dataset",
        default=None,
    )
    args = cli.parse_args(arg)

    data_folder = args.data or None

    if args.open_folder_selector:
        path = ui.AppState.show_select_folder_dialog()
        if not os.path.isdir(path):
            print("\tError: The selected dataset folder does not seem to exist.")
            return
        else:
            data_folder = path

    if args.skip_dataset or data_folder is None:
        preview(None)
        return

    final_data_path = Path(data_folder).resolve()
    if not os.path.isdir(final_data_path):
        print("\tError: The provided dataset folder does not seem to exist.")
        return

    preview(final_data_path)


if __name__ == "__main__":
    entry()
