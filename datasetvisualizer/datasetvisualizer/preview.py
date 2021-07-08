import argparse
import json
import os
import sys
import time
import subprocess
from typing import List, Tuple

import streamlit as st
from pandas import Series

import SessionState
import PIL.Image as Image
import streamlit.components.v1 as components

from datasetinsights_master.datasetinsights.datasets.unity_perception import AnnotationDefinitions, MetricDefinitions
from datasetinsights_master.datasetinsights.datasets.unity_perception.captures import Captures
import visualization.visualizers as v

st.set_page_config(layout="wide")  # This needs to be the first streamlit command
import helpers.custom_components_setup as cc


def list_datasets(path) -> List:
    """
    Lists the datasets in a diretory.
    :param path: path to a directory that contains dataset folders
    :type str:
    :return: list of dataset directories
    :rtype: List
    """
    datasets = []
    for item in os.listdir(path):
        path_to_item = os.path.join(path, item)
        if os.path.isdir(path_to_item) and item != "Unity" and item != ".streamlit":
            ann_def, _, _ = load_perception_dataset(path_to_item)
            if ann_def is not None:
                date = os.path.getctime(path_to_item)
                datasets.append((date, item))

    datasets.sort(reverse=True)
    for idx, (date, item) in enumerate(datasets):
        datasets[idx] = (time.ctime(date)[4:], item)

    if len(datasets) == 0:
        st.error("Seems like the folder you selected does not contain any datasets")
    return datasets


@st.cache(show_spinner=True, allow_output_mutation=True)
def load_perception_dataset(data_root: str) -> Tuple:
    try:
        ann_def = AnnotationDefinitions(data_root)
        metric_def = MetricDefinitions(data_root)
        cap = Captures(data_root)
        return ann_def, metric_def, cap
    except Exception:
        return None, None, None


def preview_dataset(base_dataset_dir: str):
    """
    Adds streamlit components to the app to construct the dataset preview.

    :param base_dataset_dir: The directory that contains the perceptions datasets.
    :type str:
    """

    session_state = SessionState.get(image='-1', start_at='0', num_cols='3', current_page='main',
                                     curr_dir=base_dataset_dir)
    base_dataset_dir = session_state.curr_dir

    # st.sidebar.markdown("# Select Project")
    # if st.sidebar.button("Change project folder"):
    #     folder_select(session_state)

    if session_state.current_page == 'main':
        # st.sidebar.markdown("# Select Dataset")
        # datasets = list_datasets(base_dataset_dir)
        # if len(datasets) == 0:
        #     return
        # datasets_names = [ctime + " " + item for ctime, item in datasets]

        # dataset_name = st.sidebar.selectbox(
        #     "Please select a dataset...", datasets_names
        # )
        st.sidebar.markdown("# Select Dataset")
        if st.sidebar.button("Change Dataset"):
            folder_select(session_state)

        dataset_name = base_dataset_dir
        st.sidebar.markdown("## Current dataset:")
        st.sidebar.write(os.path.abspath(dataset_name))

        # for ctime, item in datasets:
        #     if dataset_name.startswith(ctime):
        #         dataset_name = item
        #         break

        if dataset_name is not None:
            data_root = os.path.abspath(dataset_name)
            #data_root = os.path.join(base_dataset_dir, dataset_name)
            ann_def, metric_def, cap = load_perception_dataset(data_root)
            if ann_def is None:
                st.markdown("# Please select a valid dataset folder:")
                if st.button("Select dataset folder"):
                    folder_select(session_state)
                return

            st.sidebar.markdown("# Visualize Labelers")

            available_labelers = [a["name"] for a in ann_def.table.to_dict('records')]

            labelers = {}
            if 'bounding box' in available_labelers:
                labelers['bounding box'] = st.sidebar.checkbox("Bounding Boxes 2D", key="bb2d")
            if 'bounding box 3D' in available_labelers:
                labelers['bounding box 3D'] = st.sidebar.checkbox("Bounding Boxes 3D", key="bb2d")
            if 'keypoints' in available_labelers:
                labelers['keypoints'] = st.sidebar.checkbox("Key Points", key="kp")
            if 'instance segmentation' in available_labelers and 'semantic segmentation' in available_labelers:
                if st.sidebar.checkbox('Segmentation'):
                    selected_segmentation = st.sidebar.radio("Select the segmentation type:",
                                                             ['Semantic Segmentation', 'Instance Segmentation'],
                                                             index=0)
                    if selected_segmentation == 'Semantic Segmentation':
                        labelers['semantic segmentation'] = True
                    elif selected_segmentation == 'Instance Segmentation':
                        labelers['instance segmentation'] = True
            elif 'semantic segmentation' in available_labelers:
                labelers['semantic segmentation'] = st.sidebar.checkbox("Semantic Segmentation", key="ss")
            elif 'instance segmentation' in available_labelers:
                labelers['instance segmentation'] = st.sidebar.checkbox("Instance Segmentation", key="is")

            # st.sidebar.markdown("# Filter Captures")
            # st.sidebar.write("Coming soon")

            # st.sidebar.markdown("# Highlight Classes")
            # st.sidebar.write("Coming soon")

            index = int(session_state.image)
            if index >= 0:
                zoom(index, ann_def, metric_def, cap, data_root, session_state, labelers, data_root)
            else:
                num_rows = 5
                grid_view(num_rows, ann_def, metric_def, cap, data_root, session_state, labelers)


def get_annotation_def(ann_def, name):
    for idx, a in enumerate(ann_def.table.to_dict('records')):
        if a["name"] == name:
            return a["id"]
    return -1


def get_annotation_index(ann_def, name):
    for idx, a in enumerate(ann_def.table.to_dict('records')):
        if a["name"] == name:
            return idx
    return -1


def get_image_with_labelers(index, ann_def, metric_def, cap, data_root, labelers_to_use, max_size=500):
    captures = cap.filter(def_id=ann_def.table.to_dict('records')[0]["id"])
    capture = captures.loc[index, "filename"]

    filename = os.path.join(data_root, capture)
    image = Image.open(filename)
    if 'semantic segmentation' in labelers_to_use and labelers_to_use['semantic segmentation']:
        semantic_segmentation_definition_id = get_annotation_def(ann_def, 'semantic segmentation')

        seg_captures = cap.filter(def_id=semantic_segmentation_definition_id)
        seg_filename = os.path.join(data_root, seg_captures.loc[index, "annotation.filename"])
        seg = Image.open(seg_filename)

        image = v.draw_image_with_segmentation(
            image, seg
        )

    if 'instance segmentation' in labelers_to_use and labelers_to_use['instance segmentation']:
        instance_segmentation_definition_id = get_annotation_def(ann_def, 'instance segmentation')

        inst_captures = cap.filter(def_id=instance_segmentation_definition_id)
        inst_filename = os.path.join(data_root, inst_captures.loc[index, "annotation.filename"])
        inst = Image.open(inst_filename)

        image = v.draw_image_with_segmentation(
            image, inst
        )

    if 'bounding box' in labelers_to_use and labelers_to_use['bounding box']:
        bounding_box_definition_id = get_annotation_def(ann_def, 'bounding box')
        catalog = v.capture_df(bounding_box_definition_id, data_root)
        label_mappings = v.label_mappings_dict(bounding_box_definition_id, data_root)
        image = v.draw_image_with_boxes(
            image,
            index,
            catalog,
            label_mappings,
        )

    if 'keypoints' in labelers_to_use and labelers_to_use['keypoints']:
        keypoints_definition_id = get_annotation_def(ann_def, 'keypoints')
        kp_captures = cap.filter(def_id=keypoints_definition_id)
        annotations = kp_captures.loc[index, "annotation.values"]
        templates = ann_def.table.to_dict('records')[get_annotation_index(ann_def, 'keypoints')]['spec']
        v.draw_image_with_keypoints(image, annotations, templates)

    if 'bounding box 3D' in labelers_to_use and labelers_to_use['bounding box 3D']:
        bounding_box_3d_definition_id = get_annotation_def(ann_def, 'bounding box 3D')
        box_captures = cap.filter(def_id=bounding_box_3d_definition_id)
        annotations = box_captures.loc[index, "annotation.values"]
        sensor = box_captures.loc[index, "sensor"]
        image = v.draw_image_with_box_3d(image, sensor, annotations, None)
    
    image.thumbnail((max_size,max_size))

    return image


def folder_select(session_state):
    output = subprocess.run(
        [sys.executable, os.path.join(os.path.dirname(os.path.realpath(__file__)), "helpers/folder_explorer.py")],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    stdout = str(os.path.abspath(str(output.stdout).split("\'")[1]))
    if stdout[-4:] == "\\r\\n":
        stdout = stdout[:-4]
    elif stdout[-2:] == '\\n':
        stdout = stdout[:-2]
    proj_root = stdout.replace("\\", "/") + "/"

    session_state.curr_dir = proj_root
    st.experimental_rerun()


def grid_view(num_rows, ann_def, metric_def, cap, data_root, session_state, labelers):
    header = st.beta_columns([2 / 3, 1 / 3])

    num_cols = header[1].slider(label="Frames per row: ", min_value=1, max_value=5, step=1,
                                value=int(session_state.num_cols))
    if not num_cols == session_state.num_cols:
        session_state.num_cols = num_cols
        st.experimental_rerun()

    with header[0]:
        start_at = cc.item_selector(int(session_state.start_at), num_cols * num_rows,
                                    len(cap.captures.to_dict('records')))
        session_state.start_at = start_at

    components.html("""<hr style="height:2px;border:none;color:#AAA;background-color:#AAA;" /> """, height=10)

    cols = st.beta_columns(num_cols)
    containers = [None]*(num_cols*num_rows)
    for i in range(start_at, min(start_at + (num_cols * num_rows), len(cap.captures.to_dict('records')))):
        containers[i - start_at] = cols[(i - (start_at % num_cols)) % num_cols].beta_container()
        # container.write("Frame #" + str(i))
        with containers[i - start_at]:
            components.html(
                """<p style="margin-top:35px;margin-bottom:0px;font-family:IBM Plex Sans, sans-serif"></p>""",
                height=35)
        expand_image = containers[i - start_at].button(label="Expand Frame", key="exp" + str(i))
        if expand_image:
            session_state.image = i
            st.experimental_rerun()


    for i in range(start_at, min(start_at + (num_cols * num_rows), len(cap.captures.to_dict('records')))):
        image = get_image_with_labelers(i, ann_def, metric_def, cap, data_root, labelers)
        containers[i - start_at].image(image, caption=str(i), use_column_width=True)


def zoom(index, ann_def, metric_def, cap, data_root, session_state, labelers, dataset_path):
    header = st.beta_columns([0.2, 0.6, 0.2])

    if header[0].button('< Back to Grid view'):
        session_state.image = -1
        st.experimental_rerun()

    with header[1]:
        new_index = cc.item_selector_zoom(index, len(cap.captures.to_dict('records')))
        if not new_index == index:
            session_state.image = new_index
            st.experimental_rerun()

    image = get_image_with_labelers(index, ann_def, metric_def, cap, data_root, labelers, max_size=1000)

    layout = st.beta_columns([0.7, 0.3])
    layout[0].image(image, use_column_width=True)
    layout[1].title("JSON metadata")

    captures_dir = None
    for directory in os.walk(dataset_path):
        name = str(directory[0]).replace('\\', '/').split('/')[-1]
        if name.startswith("Dataset") and "." not in name[1:]:
            captures_dir = directory[0]
            break
    # TODO Change 150 to whatever the number really is in the metadata
    first = cap.captures.loc[0, "filename"]
    if not isinstance(first, str):
        first = first.tolist()[0]

    offset = int(first[-5])

    file_num = index // (150 - offset)
    postfix = ('000' + str(file_num))
    postfix = postfix[len(postfix) - 3:]
    path_to_captures = os.path.join(os.path.abspath(captures_dir), "captures_" + postfix + ".json")
    with layout[1]:
        json_file = json.load(open(path_to_captures, "r"))
        st.write(json_file["captures"][index % (150 - offset)])


def preview_app(args):
    """
    Starts the dataset preview app.

    :param args: Arguments for the app, such as dataset
    :type args: Namespace
    """
    if args.data is not None:
        preview_dataset(args.data)
    else:
        ValueError("Please use a valid path")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("data", type=str)
    args = parser.parse_args()

    # remove the default zoom in button for images
    st.markdown('<style>button.css-9eqr5v{display: none}</style>', unsafe_allow_html=True)
    preview_app(args)
