import glob
import json
from typing import List, Tuple, Dict

import streamlit as st
from datasetinsights.datasets.unity_perception import AnnotationDefinitions, MetricDefinitions
from datasetinsights.datasets.unity_perception.captures import Captures

from helpers.ui import AppState
from .SoloDataset import BOUNDING_BOX_TYPE, BOUNDING_BOX_3D_TYPE, KEYPOINT_TYPE, SEMANTIC_SEGMENTATION_TYPE, \
    INSTANCE_SEGMENTATION_TYPE
from .SoloDataset import SoloDataset


def create_sidebar_entry(label, annotator_dic, available_labelers, label_type, labelers):
    states = {}

    for l in available_labelers:
        if l['type'] != label_type:
            continue
        states['name'] = l['name']
        states['state'] = True

    if len(states) > 0:
        labelers[label_type] = st.sidebar.checkbox(label) and st.session_state[f'{label_type}_existed_last_time']
        st.session_state[f'{label_type}_existed_last_time'] = True

        annotator_list = annotator_dic[label_type]
        if len(annotator_list) == 1:
            annotator = annotator_list[0]
            annotator.state = labelers[label_type]
        if labelers[label_type] and st.session_state[f'{label_type}_existed_last_time'] and len(annotator_list) > 1:
            c1, c2 = st.sidebar.columns(2)

            for annotator in annotator_list:
                annotator.state = c2.checkbox(annotator.name, value=True)
                st.session_state[f'{annotator.name}_existed_last_time'] = True
    else:
        st.session_state[f'{label_type}_existed_last_time'] = False


def create_sidebar_labeler_menu(available_labelers: List[str], annotator_dic) -> Dict[str, bool]:
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

    bbox_count = 0
    semantic_count = 0
    instance_count = 0
    bbox3d_count = 0
    keypoints_count = 0

    for labeler in available_labelers:
        if labeler['type'] == BOUNDING_BOX_TYPE:
            bbox_count = bbox_count + 1
        if labeler['type'] == BOUNDING_BOX_3D_TYPE:
            bbox3d_count = bbox3d_count + 1
        if labeler['type'] == KEYPOINT_TYPE:
            keypoints_count = keypoints_count + 1
        if labeler['type'] == INSTANCE_SEGMENTATION_TYPE:
            instance_count = instance_count + 1
        if labeler['type'] == SEMANTIC_SEGMENTATION_TYPE:
            semantic_count = semantic_count + 1

    create_sidebar_entry("2D Bounding Boxes", annotator_dic, available_labelers,
                         BOUNDING_BOX_TYPE, labelers)
    create_sidebar_entry("3D Bounding Boxes", annotator_dic, available_labelers,
                         BOUNDING_BOX_3D_TYPE, labelers)
    create_sidebar_entry("Keypoints", annotator_dic, available_labelers,
                         KEYPOINT_TYPE, labelers)
    if instance_count > 0 or semantic_count > 0:
        if st.sidebar.checkbox('Segmentation', False) and st.session_state.semantic_existed_last_time:
            semantic_seg_list = annotator_dic.get(SEMANTIC_SEGMENTATION_TYPE, [])
            instance_seg_list = annotator_dic.get(INSTANCE_SEGMENTATION_TYPE, [])
            segmentation_list = semantic_seg_list + instance_seg_list
            segmentation_names = [seg.name for seg in segmentation_list if seg is not None]

            semantic_seg_names = [seg.name for seg in semantic_seg_list]
            instance_seg_names = [seg.name for seg in instance_seg_list]
            selected_segmentation = st.sidebar.radio("Selected Segmentation Id", segmentation_names)
            for annotator_segmentation in segmentation_list:
                if annotator_segmentation.name == selected_segmentation:
                    annotator_segmentation.state = True
                    st.session_state[f'{annotator_segmentation.name}_existed_last_time'] = True

            if selected_segmentation in semantic_seg_names:
                labelers[SEMANTIC_SEGMENTATION_TYPE] = True
            elif selected_segmentation in instance_seg_names:
                labelers[INSTANCE_SEGMENTATION_TYPE] = True
        st.session_state.semantic_existed_last_time = True

    if st.session_state.previous_labelers != labelers:
        st.session_state.labelers_changed = True
    else:
        st.session_state.labelers_changed = False
    st.session_state.previous_labelers = labelers

    return labelers


def preview_dataset(data_root):
    ds = SoloDataset(data_root)

    # This should probably never occur anyway as we check for validity before
    if not ds.dataset_valid:
        st.error(f"The provided folder does not seem to contain a valid SOLO dataset: {data_root}")
        return

    dataset_len = ds.metadata["totalFrames"]
    with st.sidebar:
        AppState.display_horizontal_rule()
        AppState.display_number_frames(dataset_len)
        AppState.display_horizontal_rule()

    available_labelers = ds.get_available_labelers()
    annotator_dic = ds.get_annotator_dictionary()
    labelers = create_sidebar_labeler_menu(available_labelers, annotator_dic)

    # zoom_image is negative if the application isn't in zoom mode
    index = int(AppState.get_zoom_image())
    if index >= 0:
        zoom(index, 0, ds, labelers, annotator_dic)
    else:
        num_rows = 5
        grid_view(num_rows, ds, labelers, annotator_dic)


def _create_grid_view_controls(dataset_size: int) -> Tuple[int, int]:
    left, mid, right = st.columns([1 / 3, 1 / 3, 1 / 3])

    with left:
        new_start_at = st.number_input("Start at Sequence Number", 0, dataset_size-1)
        if new_start_at != AppState.get_starting_frame() and not st.session_state.just_opened_grid:
            AppState.set_starting_frame(new_start_at)

        st.session_state.just_opened_grid = False
        start_at = int(AppState.get_starting_frame())

    with right:
        num_cols = st.number_input(label="Sequences Per Row", min_value=1, max_value=10, step=1,
                                   value=int(AppState.get_num_cols()))
        if num_cols != (AppState.get_num_cols()):
            AppState.set_num_cols(num_cols)
            st.experimental_rerun()

    AppState.display_horizontal_rule()

    return num_cols, start_at


def _create_grid_containers(num_rows: int, num_cols: int, start_at: int, dataset_size: int) -> List[any]:
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
    cols = st.columns(int(max(1, num_cols)))
    containers = [None] * (num_cols * num_rows)

    for i in range(start_at, min(start_at + (num_cols * num_rows), dataset_size)):
        container = containers[i - start_at] = cols[(i - (start_at % num_cols)) % num_cols].container()
        # with container:
        #    cc.diver("", f"posp{i}")

        # expand_image = container.button(label="Open", key=f"exp{i}")
        # if expand_image:
        #    UI.set_zoom_image(i)
        #    st.session_state.just_opened_zoom = True
        #    st.experimental_rerun()
    return containers


def grid_view(num_rows: int, ds: SoloDataset, labelers: Dict[str, bool], annotator_dic):
    """ Creates the grid view streamlit components

    :param num_rows: Number of rows
    :type num_rows: int
    :param ds: Current Dataset
    :type ds: SoloDataset
    :param labelers: Dictionary containing keys for the name of every labeler available in the given dataset
                     and the corresponding value is a boolean representing whether or not to display it
    :type labelers: Dict[str, bool]
    """
    dataset_size = ds.length()

    num_cols, start_at = _create_grid_view_controls(dataset_size)

    containers = _create_grid_containers(num_rows, num_cols, start_at, dataset_size)
    view_range = range(start_at, min(start_at + (num_cols * num_rows), dataset_size))

    for i in view_range:
        image = ds.get_solo_image_with_labelers(i, labelers, annotator_dic,
                                                max_size=get_resolution_from_num_cols(num_cols))
        sequence = int(i / ds.solo.steps_per_sequence)
        step = i % ds.solo.steps_per_sequence
        with containers[i - start_at]:
            st.image(image, caption=f"sequence{sequence}.step{step}", use_column_width=True)
            if st.button("Open", key=f"i_{i}"):
                AppState.set_zoom_image(i)
                st.session_state.just_opened_zoom = True
                st.experimental_rerun()


def get_resolution_from_num_cols(num_cols):
    if num_cols == 5:
        return 300
    else:
        return (6 - num_cols) * 200


def zoom(index: int,
         offset: int,
         ds: SoloDataset,
         labelers: Dict[str, bool],
         annotator_dic):
    """ Creates streamlit components for Zoom in view

    :param index: Index of the image
    :type index: int
    :param offset: Is how much the index needs to be offset, this is only needed to
                   handle multiple instances (UCVD datasets)
    :type offset: int
    :param ds: Current Dataset
    :type ds: SoloDataset
    :param labelers: Dictionary containing keys for the name of every labeler available in the given dataset
                     and the corresponding value is a boolean representing whether or not to display it
    :type labelers: Dict[str, bool]
    """
    dataset_size = ds.length()

    st.session_state.start_at = index
    st.session_state.zoom_image = index

    top_header_l, _, top_header_r = st.columns([2/4, 1/4, 1/4])

    with top_header_r:
        if st.button('Back'):
            st.session_state.zoom_image = -1
            st.session_state.just_opened_grid = True
            st.experimental_rerun()

    with top_header_l:
        new_index = st.number_input("Sequence Number", 0, dataset_size - 1, value=index)
        if not new_index == index and not st.session_state.just_opened_zoom and not st.session_state.labelers_changed:
            st.session_state.zoom_image = new_index
            AppState.set_starting_frame(index)
            st.experimental_rerun()

    st.session_state.start_at = index
    st.session_state.zoom_image = index
    st.session_state.just_opened_zoom = False

    index = index - offset

    AppState.display_horizontal_rule()

    frame = st.container()
    step = index % ds.solo.steps_per_sequence
    image = ds.get_solo_image_with_labelers(index, labelers, annotator_dic, max_size=2000)
    path_to_captures = glob.glob(f"{ds.solo.sequence_path}/step{step}.frame_data.json")[0]

    with frame:
        json_file = json.load(open(path_to_captures, "r", encoding="utf8"))
        captures = json_file['captures']
        metrics = json_file['metrics']

        st.markdown(
            f"<p align=\"center\">"
            f"Sequence: {json_file['sequence']} | Step: {json_file['step']} | Frame: {json_file['frame']}"
            f"</p>",
            unsafe_allow_html=True
        )
        st.image(image, use_column_width=True)

        frame.subheader("Frame Data")

        with st.expander("Captures", expanded=False):
            st.json(captures)

        with st.expander("Metrics", expanded=False):
            st.json(metrics)
