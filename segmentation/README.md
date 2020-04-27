# Robust Vision Challenge 2020 - Panoptic and Instance Segmentation Devkit #

## Dataset Download ##

We provide a devkit to download, extract, and convert the challenge datasets into a unified format. First specifying the target root directory for all RVC datasets using an environment variable

export RVC_DATA_DIR=/path/to/rvc_dataroot

Some segmentation benchmarks require users to register and to confirm the license terms before granting access to their data.
For the Cityscapes dataset, please register at: https://www.cityscapes-dataset.com 

For the WildDash dataset, please register at: https://www.wilddash.cc (Note: RVC users can already use a alpha version of WildDash v2; see the downloaded readme/license for details).

To use the automatic download script, define these environment variables using 

```
# Copy Cityscapes credentials here
export CITYSCAPES_USERNAME="your_cs_username"
export CITYSCAPES_PASSWORD="your_cs_passwd"
# Copy WildDash credentials here
export WILDDASH_USERNAME="your_wd_username"
export WILDDASH_PASSWORD="your_wd_passwd"
```

Now you can execute the download script ``` download_inst_segm.sh ``` or ``` download_panoptic_segm.sh ``` which will download most of the RVC datasets.

You need to manually register and download the Mapillary Vistas (Research Edition) dataset, and we will base our evaluation on version 1.3 (blurred faces and license plates):
https://www.mapillary.com/dataset/vistas

You will receive an email with download instructions. Save/Move the downloaded zip file into the folder ${RVC_DATA_DIR}/mvs.

After successfully downloading all datasets, execute this script to extract and delete clean up files:  ``` extract_and_cleanup_inst_segm.sh ``` or ```extract_and_cleanup_panoptic_segm.sh ```

### Dataset remapping ###

RVC does not force you to remap the datasets in a certain way. We do provide a "best-effort" mapping, which can be a good starting point. This mapping will contain overlapping classes and some dataset entries might miss relevant labels (as they were annotated using different policies/mixed hierarchical  levels). Combine and remap datasets by executing the script 

 ``` remap_inst_segm.sh ``` or  ``` remap_panoptic_segm.sh ```

## Dataset Format ##

The above step creates a joint training and a separate joint validation json file in COCO Panoptic format:

http://cocodataset.org/#format-data

The "file_name" tag of each image entry and annotation entry has been prepended with the relative path calculated from RVC_DATA_DIR.
These files can directly be used in your training framework.

## Result Submission ##
This repo will be updated as soon as the submission support is ready. See robustvision.net for news.


