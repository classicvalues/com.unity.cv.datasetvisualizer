# Unity Computer Vision Dataset Visualizer

This Python based tool allows you to visualize datasets created using Unity Computer Vision tools.

## Requirements

* Windows 10 or OSX
* Chrome, Firefox, or Safari 14 and newer (Older versions of Safari are not supported)
* Python 3.7 or 3.8. Note that this application is not compatible with Python 3.9.

## Running the visualizer

Run the command:

```bash
datasetvisualizer
```

Or if you want to specify a path to a dataset:

```bash
datasetvisualizer --data="<path_to_dataset>"
```

This command may take a few seconds to execute. Once it is done, your browser will automatically open to `http://localhost:8501/` and display the application. If that does not happen, open a new browser tab and manually navigate to that address.

Once in the application, you will be prompted to select a dataset folder. Click ***Change Dataset*** at the left side of the screen and then select the root folder of your Unity Computer Vision dataset.

## Known issues

* The tool cannot open a dataset that has no labeler data (bounding boxes, semantic segmentation, etc.)
* On Windows: a warning appears when launching the app (This can be ignored)
* 3D bounding boxes are not rendered properly when the camera is inside the box.
* Opening a folder that isn't a dataset folder may hang the program (The workaround is: kill the process and start it again)
