import glob
import os.path
from pathlib import Path
from typing import List, Optional

from datasetvisualizer.core.formats.perception.LegacyDataset import (
    LegacyDataset as PerceptionDataset,
)
from datasetvisualizer.core.formats.solo.SoloDataset import SoloDataset

DATASET_TYPE_SOLO = "SOLO"
DATASET_TYPE_LEGACY = "LEGACY"


def get_dataset_format(dataset_path: str) -> Optional[str]:
    if SoloDataset.is_solo_dataset(dataset_path):
        return DATASET_TYPE_SOLO
    elif PerceptionDataset.is_folder_valid_dataset(dataset_path):
        return DATASET_TYPE_LEGACY
    else:
        return None


def is_ucvd_dataset(dataset_dir: str) -> Optional[List[str]]:
    if dataset_dir is None or not os.path.exists(dataset_dir):
        return None

    dataset_base_path = Path(dataset_dir).resolve()
    if not dataset_base_path.exists():
        return None

    ps = os.path.sep
    glob_pattern = f"{dataset_base_path}{ps}urn_app_*{ps}instance_*{ps}attempt_*{ps}"
    glob_pattern_2 = f"{dataset_base_path}{ps}instance_*{ps}attempt_*{ps}"

    instances = []
    for instance_path in glob.glob(glob_pattern):
        instances.append(instance_path)

    for instance_path in glob.glob(glob_pattern_2):
        instances.append(instance_path)

    if len(instances) > 0:
        return instances
    else:
        return None
