# Robust Vision Challenge 2020 - Object Detection Devkit #

## Dataset Download ##

We provide a devkit to download, extract, and convert the challenge datasets into a unified format.
This is done by first specifying the target root directory for all RVC datasets using a environment variabdownload_sem_segm.sh
 ``` export RVC_DATA_DIR=/path/to/rvc_dataroot  ```

Now you can execute the download script download_obj_det.sh which will download and extract most of the RVC datasets.

You need to manually register and download the follow dataset:

Mapillary Vistas Boxable Version (Research Edition):
https://www.mapillary.com/dataset/vistas

You will receive an Email with download instructions. Extract the content of the received file TODO into the folder ${RVC_DATA_DIR}/mvs.

### Dataset remapping ###

RVC does not not force you to remap the datasets in a certain way. We do provide a "best-effort" mapping, which can be a good starting point. This mapping will contain overlapping classes and some dataset entries might miss relevant labels (as they were annotated using different policies). To create the best effort combined and remapped dataset, execute the script remap_obj_det.sh

## Dataset Format / Training ##

TODO

## Result Submission ##

TODO
