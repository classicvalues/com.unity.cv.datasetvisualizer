import os

import streamlit as st
from PIL import Image

from formats.common import is_ucvd_dataset, get_dataset_format, DATASET_TYPE_SOLO, DATASET_TYPE_LEGACY
from formats.perception.LegacyPreview import preview_dataset as legacy_preview_dataset
from formats.solo.SoloPreview import preview_dataset as solo_preview_dataset
from helpers.ui import AppState, Components


def preview_app(args):
    AppState.create_default_state(dataset_dir=args["data"])
    base_dataset_dir = AppState.get_base_dataset_directory()

    # Top-level wrapper for UCVD
    instance_list = is_ucvd_dataset(base_dataset_dir)
    chosen_instance = 0 if instance_list is None else min(AppState.get_selected_instance(), len(instance_list))
    selected_dataset_dir = base_dataset_dir if instance_list is None else instance_list[chosen_instance]
    AppState.set_selected_dataset_directory(selected_dataset_dir)

    dataset_type = get_dataset_format(selected_dataset_dir)

    with st.sidebar:
        # Add logo
        st.write(AppState.get_docs_path("unity_logo.png", as_str=True))
        st.image(AppState.get_docs_path("unity_logo.png", as_str=True))

        # Display select dataset menu
        left_dt, right_dt = st.columns(2)
        with left_dt:
            st.markdown("## Active Dataset")

        with right_dt:
            if dataset_type is not None:
                Components.badge(dataset_type)

        if base_dataset_dir is None:
            st.warning("No dataset selected yet.")
        else:
            Components.scrollable_text(base_dataset_dir, label="Dataset")

        # Show controls for changing instances when we have a UCVD dataset
        if instance_list is not None and len(instance_list) > 1:
            new_instance = st.number_input("Instance", 0, len(instance_list) - 1)
            if new_instance != chosen_instance:
                AppState.set_selected_instance(new_instance)
                st.experimental_rerun()
                return

        _, r_d = st.columns(2)
        with r_d:
            if st.button("Select Dataset"):
                AppState.show_select_folder_dialog()
                return

    if base_dataset_dir is None or selected_dataset_dir is None:
        Components.draw_homepage()
        return

    if dataset_type is None:
        st.sidebar.error(f"**Invalid Dataset:** Could not parse dataset from the selected directory..")
    elif dataset_type == DATASET_TYPE_SOLO:
        solo_preview_dataset(selected_dataset_dir)
    elif dataset_type == DATASET_TYPE_LEGACY:
        legacy_preview_dataset(selected_dataset_dir)


if __name__ == "__main__":
    favicon = Image.open(AppState.get_docs_path("favicon.ico", as_str=True))
    st.set_page_config(
        page_title="Unity Dataset Visualizer",
        layout="wide", page_icon=favicon,
        initial_sidebar_state="expanded",
        menu_items={
            "About": "https://github.com/Unity-Technologies/com.unity.cv.datasetvisualizer",
            "Report a Bug": "https://github.com/Unity-Technologies/com.unity.cv.datasetvisualizer/issues/new",
            "Get Help": "https://github.com/Unity-Technologies/com.unity.cv.datasetvisualizer/issues?q=is%3Aissue+is%3Aopen+sort%3Aupdated-desc"
        }
    )

    with open(os.path.join(os.path.dirname(__file__), 'Global.css')) as css_file:
        css_file_str = css_file.read()

        st.markdown(f"<style>{css_file_str}</style>", unsafe_allow_html=True)

    # TODO: Support --data --> data again
    preview_app({"data": None})
