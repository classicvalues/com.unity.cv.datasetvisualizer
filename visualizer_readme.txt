==== Unity Computer Vision Dataset Visualizer ====

This Python based tool allows you to visualize datasets created using Unity Computer Vision tools.

=== Requirements === 

- Windows 10 or OSX

- Chrome, Firefox, or Safari 14 and newer (Older versions of Safari are not supported)

- Python 3.7 or 3.8. Note that this application is not compatible with Python 3.9.

- We recommend using a virtual environment to install and run the app. One way to achieve this is using Conda.

=== Installation ===

== Step 1 == 

We first need to create a virtual environment (skip to step 2 if you are setting up a virtual environment using other methods). Install Conda if you do not already have it installed on your computer. We recommend Miniconda.

Once Conda is installed:
- On Mac OS, open a new terminal window.
- On Windows, you will need to open either Anaconda Prompt or Anaconda Powershell Prompt. These can be found in the Start menu.

We will now create a virtual environment named "dv_env" using Conda, and activate it using the commands:

"conda create -n dv_env python=3.7"
"conda activate dv_env"

== Step 2 ==

Navigate to the folder named "Unity_CV_DatasetVisualizer" and run:

"pip install -e ."

Note: On Windows, if you get an error about the system not being able to create a process when running the install command, make sure you have the latest version of Conda installed. Then create a new environment with a new name, and try the install command again.

=== Running the visualizer ===

Run the command:

"datasetvisualizer"

This command may take a few seconds to execute. Once it is done, your browser will automatically open to http://localhost:8501/ and display the application. If that does not happen, open a new browser tab and manually navigate to that address.

Once in the application, you will be prompted to select a dataset folder. Click Change Dataset at the left side of the screen and then select the root folder of your Unity Computer Vision dataset.


=== Known issues ===

- The tool cannot open a dataset that has no labeler data (bounding boxes, semantic segmentation, etc.)
- On Windows: a warning appears when launching the app (This can be ignored)
