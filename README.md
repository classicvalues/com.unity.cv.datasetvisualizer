# Unity Computer Vision Dataset Visualizer

This Python based tool allows you to visualize datasets created using Unity Computer Vision tools.

## Requirements

* Windows 10 or OSX

* Python 3.7 or 3.8. Note that this application is not compatible with Python 3.9.

## Installation

We recommend using a virtual enviornment to install and run the app. One way to achieve this is using Conda.

**Step 1:** Create a virtual environment (skip to step 2 if you are setting up a virtual environment using other methods)

* Install Conda if you do not already have it installed on your computer. We recommend [Miniconda](https://docs.conda.io/en/latest/miniconda.html).

* Once Conda is installed: 
  * On Mac OS, open a new terminal window.
  * On Windows, you will need to open either Anaconda Prompt or Anaconda Powershell Prompt. These can be found in the Start menu.

* Create a virtual environment named `dv_env` using Conda, and activate it:

```bash
conda create -n dv_env python=3.7
conda activate dv_env
```
**Step 2:** Install application

Use the following commands to clone this Github repository and install the visualizer.

```bash
git clone https://github.com/Unity-Technologies/com.unity.cv.datasetvisualizer.git
cd com.unity.cv.datasetvisualizer/Unity_CV_DatasetVisualizer
pip install -e .
```

## Running the visualizer

From the same folder where you ran the installation command, run:

```bash
datasetvisualizer
```

This command may take a few seconds to execute. Once it is done, your browser will automatically open to `http://localhost:8501/` and display the application. If that does not happen, open a new browser tab and manually navigate to that address.

Once in the application, you will be prompted to select a dataset folder. Click ***Change Dataset*** at the left side of the screen and then select the root folder of your Unity Computer Vision dataset.

## Known issues

* The tool cannot open a dataset that has no labeler data (bounding boxes, semantic segmentation, etc.)
* On Windows: a warning appears when launching the app (This can be ignored)
