# Robust Vision Challenge 2020 - Object Detection Devkit #

## Dataset Download ##

We provide a devkit to download, extract, and convert the challenge datasets into a unified format.
This is done by first specifying the target root directory for all RVC datasets using an environment variable

 ``` export RVC_DATA_DIR=/path/to/rvc_dataroot  ```

Now you can execute the download script ``` download_obj_det.sh ``` which will download and extract most of the RVC datasets.

You need to manually register and download the Mapillary Vistas (Research Edition) dataset:
https://www.mapillary.com/dataset/vistas

You will receive an email with download instructions. Save/Move the downloaded zip file into the folder ${RVC_DATA_DIR}/mvs.

After successfully downloading all datasets, execute this script to extract and delete clean up files:  ``` extract_and_cleanup.sh ``` 

### Dataset remapping ###

RVC does not force you to remap the datasets in a certain way. We do provide a "best-effort" mapping, which can be a good starting point. This mapping will contain overlapping classes and some dataset entries might miss relevant labels (as they were annotated using different policies/mixed hierarchical  levels). Combine and remap datasets by executing the script 

 ``` remap_obj_det.sh ```

## Dataset Format / Training ##

The above step creates a joint training and a separate joint validation json file in COCO Object Detection format (only bbox entries, without "segmentation" entries):

http://cocodataset.org/#format-data

The "file_name" tag of each image entry has been prepended with the relative path calculated from RVC_DATA_DIR.
These files can directly be used in your object detector training framework.

## Result Submission ##

This repo will be updated as soon as the submission support is ready. See robustvision.net for news.
