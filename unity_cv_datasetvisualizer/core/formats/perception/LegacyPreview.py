import json
import os
import re
import subprocess
import sys
import re
from typing import List, Tuple, Optional, Dict
import streamlit as st
import streamlit.components.v1 as components
from datasetinsights.datasets.unity_perception import AnnotationDefinitions, MetricDefinitions
from datasetinsights.datasets.unity_perception.captures import Captures
from helpers import ui, unity_component_library as cc
from helpers.ui import UI
from .LegacyDataset import LegacyDataset


def preview_dataset(data_root):
    # Attempt to read as a normal perception dataset
    ds = LegacyDataset(data_root)

    with st.sidebar:
        UI.display_horizontal_rule()
        UI.display_number_frames(ds.length())
        UI.display_horizontal_rule()

    available_labelers = ds.get_available_labelers()
    labelers = _create_sidebar_labeler_menu(available_labelers)

    # zoom_image is negative if the application isn't in zoom mode
    index = int(st.session_state.zoom_image)
    if index >= 0:
        zoom(index, 0, ds, labelers)
    else:
        num_rows = 5
        grid_view(num_rows, ds, labelers)


def _create_sidebar_labeler_menu(available_labelers: List[str]) -> Dict[str, bool]:
    """
    Creates a streamlit sidebar menu that displays checkboxes and radio buttons to select which labelers to display

    :param available_labelers: List of strings representing labelers
    :type available_labelers: List[str]

    :return: Dictionary where keys are the available_labelers and values are bool representing if they have been chosen
    :rtype: Dict[str, bool]
    """

    # Note that here there is use of st.session_state._____existed_last_time this is used to workaround a streamlit bug
    # if this is removed then when user selects dataset with labeler X and turns it on then changes to dataset without
    # it then changes to a dataset with labeler X, labeler X appears as unselected but returns True as a value so acts
    # as if it was selected

    st.sidebar.markdown("### Visualize Labels")
    labelers = {}
    if 'bounding box' in available_labelers:
        labelers['bounding box'] = st.sidebar.checkbox(
            "2D Bounding Boxes") and st.session_state.bbox2d_existed_last_time
        st.session_state.bbox2d_existed_last_time = True
    else:
        st.session_state.bbox2d_existed_last_time = False

    if 'bounding box 3D' in available_labelers:
        labelers['bounding box 3D'] = st.sidebar.checkbox(
            "3D Bounding Boxes") and st.session_state.bbox3d_existed_last_time
        st.session_state.bbox3d_existed_last_time = True
    else:
        st.session_state.bbox3d_existed_last_time = False

    if 'keypoints' in available_labelers:
        labelers['keypoints'] = st.sidebar.checkbox("Keypoints") and st.session_state.keypoints_existed_last_time
        st.session_state.keypoints_existed_last_time = True
    else:
        st.session_state.keypoints_existed_last_time = False

    if 'instance segmentation' in available_labelers and 'semantic segmentation' in available_labelers:
        if st.sidebar.checkbox('Segmentation', False) and st.session_state.semantic_existed_last_time:
            selected_segmentation = st.sidebar.radio("Select the segmentation type:",
                                                     ['Semantic Segmentation', 'Instance Segmentation'],
                                                     index=0)
            if selected_segmentation == 'Semantic Segmentation':
                labelers['semantic segmentation'] = True
            elif selected_segmentation == 'Instance Segmentation':
                labelers['instance segmentation'] = True
        st.session_state.semantic_existed_last_time = True
    elif 'semantic segmentation' in available_labelers:
        labelers['semantic segmentation'] = st.sidebar.checkbox("Semantic Segmentation")
        st.session_state.semantic_existed_last_time = False
    elif 'instance segmentation' in available_labelers:
        labelers['instance segmentation'] = st.sidebar.checkbox("Instance Segmentation")
        st.session_state.semantic_existed_last_time = False
    else:
        st.session_state.semantic_existed_last_time = False
    if st.session_state.previous_labelers != labelers:
        st.session_state.labelers_changed = True
    else:
        st.session_state.labelers_changed = False
    st.session_state.previous_labelers = labelers
    return labelers


def create_grid_view_controls(num_rows: int, dataset_size: int) -> Tuple[int, int]:
    """ Creates the controls for grid view

    :param num_rows: number of rows to display
    :type num_rows: int
    :param dataset_size: The size of the dataset
    :type dataset_size: int
    :return: Returns the number of columns and the index at which the grid must start
    :rtype: Tuple[int, int]
    """
    left, mid, right = st.columns([1 / 3, 1 / 3, 1 / 3])

    with left:
        new_start_at = st.number_input(
            label="Start at Frame Number", value=int(st.session_state.start_at),
            min_value=0, max_value=dataset_size - 1
        )
        if not new_start_at == st.session_state.start_at and not st.session_state.just_opened_grid:
            st.session_state.start_at = new_start_at

        st.session_state.just_opened_grid = False
        start_at = int(st.session_state.start_at)

    with right:
        num_cols = st.number_input(label="Frames Per Row: ", min_value=1, max_value=5,
                                   value=int(st.session_state.num_cols))
        if not num_cols == st.session_state.num_cols:
            st.session_state.num_cols = num_cols
            st.experimental_rerun()

    UI.display_horizontal_rule()

    return num_cols, start_at


def create_grid_containers(num_rows: int, num_cols: int, start_at: int, dataset_size: int) -> List[any]:
    """ Creates the streamlit containers that will hold the images in a grid, this must happen before placing the images
    so that when clicking on "Expand frame" it doesn't need to reload every image before opening in zoom view

    :param num_rows: Number of rows
    :type num_rows: int
    :param num_cols: Number of columns
    :type num_cols: int
    :param start_at: Index at which the grid starts
    :type start_at: int
    :param dataset_size: Size of the dataset
    :type dataset_size: int
    :return: list of the containers in order from left to right, up to down
    :rtype: List[any]
    """
    cols = st.columns(num_cols)
    containers = [None] * (num_cols * num_rows)
    for i in range(start_at, min(start_at + (num_cols * num_rows), dataset_size)):
        containers[i - start_at] = cols[(i - (start_at % num_cols)) % num_cols].container()
        # container.write("Frame #" + str(i))
        with containers[i - start_at]:
            components.html(
                """<p style="margin-top:35px;margin-bottom:0px;font-family:IBM Plex Sans, sans-serif"></p>""",
                height=35)
        expand_image = containers[i - start_at].button(label="Open", key="exp" + str(i))
        if expand_image:
            st.session_state.zoom_image = i
            st.session_state.just_opened_zoom = True
            st.experimental_rerun()
    return containers


def get_resolution_from_num_cols(num_cols):
    if num_cols == 5:
        return 300
    else:
        return (6 - num_cols) * 200


def grid_view(num_rows: int, ds: LegacyDataset, labelers: Dict[str, bool]):
    """ Creates the grid view streamlit components

    :param num_rows: Number of rows
    :type num_rows: int
    :param ds: Current Dataset
    :type ds: LegacyDataset
    :param labelers: Dictionary containing keys for the name of every labeler available in the given dataset
                     and the corresponding value is a boolean representing whether or not to display it
    :type labelers: Dict[str, bool]
    """
    dataset_size = ds.length()

    num_cols, start_at = create_grid_view_controls(num_rows, dataset_size)

    containers = create_grid_containers(num_rows, num_cols, start_at, dataset_size)

    for i in range(start_at, min(start_at + (num_cols * num_rows), dataset_size)):
        image = ds.get_image_with_labelers(i, labelers, max_size=get_resolution_from_num_cols(num_cols))
        this_container = containers[i - start_at]

        with this_container:
            st.image(image, caption=f"RGB_{i}", use_column_width=True)


def zoom(index: int, offset: int, ds: LegacyDataset, labelers: Dict[str, bool]):
    """ Creates streamlit components for Zoom in view

    :param index: Index of the image
    :type index: int
    :param offset: Is how much the index needs to be offset, this is only needed to 
                   handle multiple instances (UCVD datasets)
    :type offset: int
    :param ds: Current Dataset
    :type ds: LegacyDataset
    :param labelers: Dictionary containing keys for the name of every labeler available in the given dataset
                     and the corresponding value is a boolean representing whether or not to display it
    :type labelers: Dict[str, bool]
    """
    dataset_size = ds.length()

    st.session_state.start_at = index
    st.session_state.zoom_image = index

    left, _, right = st.columns([1/3, 1/3, 1/3])

    with left:
        new_index = st.number_input(label="Frame Number", min_value=0, value=index, max_value=(dataset_size + offset))
        if not new_index == index and not UI.get_in_zoom_mode() and not UI.get_labelers_changed():
            UI.set_zoom_image(new_index)
            UI.set_starting_frame(index)
            st.experimental_rerun()

    with right:
        if st.button('< Back'):
            UI.set_zoom_image(-1)
            UI.set_in_grid_mode(True)
            st.experimental_rerun()

    UI.set_starting_frame(index)
    UI.set_zoom_image(index)
    UI.set_in_zoom_mode(False)

    UI.display_horizontal_rule()

    index = index - offset
    image = ds.get_image_with_labelers(index, labelers, max_size=2000)

    captures_dir = None
    for directory in os.walk(ds.data_root):
        name = str(directory[0]).replace('\\', '/').split('/')[-1]
        if name.startswith("Dataset") and \
                "." not in name[1:] and \
                os.path.abspath(ds.data_root) != os.path.abspath(directory[0]):
            captures_dir = os.path.abspath(directory[0])
            break

    path_to_captures = os.path.join(os.path.abspath(captures_dir), "captures_000.json")
    captures_json_file = json.load(open(path_to_captures, "r", encoding="utf8"))
    num_captures_per_file = len(captures_json_file["captures"])
    file_num = index // num_captures_per_file
    postfix = ('000' + str(file_num))
    postfix = postfix[len(postfix) - 3:]
    path_to_captures = os.path.join(os.path.abspath(captures_dir), "captures_" + postfix + ".json")
    captures_json_file = json.load(open(path_to_captures, "r", encoding="utf8"))
    capture = captures_json_file['captures'][index % num_captures_per_file]

    metrics = []
    for i in os.listdir(captures_dir):
        path_to_metrics = os.path.join(captures_dir, i)
        if os.path.isfile(path_to_metrics) and 'metrics_' in i and 'definitions' not in i:
            captures_json_file = json.load(open(path_to_metrics, encoding="utf8"))
            metrics.extend(captures_json_file['metrics'])

    filename_match = re.search("(rgb_\\d+)", capture["filename"])
    rgb_filename = filename_match.group(1) if len(filename_match.groups()) > 0 else f"Image #{index}"

    st.image(image, caption=rgb_filename, use_column_width=True)

    captures_layout = st.expander(label="Captures")
    with captures_layout:
        st.write(capture)

    metrics_layout = st.expander(label="Metrics")
    with metrics_layout:
        for metric in metrics:
            if metric['sequence_id'] == capture['sequence_id'] and metric['step'] == capture['step']:
                for metric_def in ds.get_metrics_records():
                    if metric_def['id'] == metric['metric_definition']:
                        st.markdown(f"#### {metric_def['name']}")
                st.write(metric)

    UI.display_horizontal_rule()
