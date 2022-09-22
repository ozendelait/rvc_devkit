# Robust Vision Challenge 2022 - Object Detection Devkit #

The Object detection challenge consists of four datasets:
- [MS COCO](cocodataset.org/)
- [OpenImages](https://storage.googleapis.com/openimages/web/index.html) (OID)
- [Mapillary Vistas](https://www.mapillary.com/dataset/vistas) (MVD)

## Requirements ##
Install additional requirements with:
    ``` pip install -r requirements.txt ```


## Dataset Download ##

We provide a devkit to download, extract, and convert the challenge datasets into a unified format.

1. Specify the target root directory for all RVC datasets with ``` export RVC_DATA_DIR=/path/to/rvc_dataroot  ```

2. Get an authentication token for the Kaggle API as described here: https://www.kaggle.com/docs/api. This is required to download the OpenImages test data from kaggle.

3. Execute the download script ``` bash download_obj_det.sh ``` which will download most of the RVC datasets. The extracted dataset needs ca. 600GB of disk space (COCO: 26GB, OID: 527GB, MVD: 25GB). Please note that up to 50% more disc space is required during the extraction process.

4. To download the Mapillary Vistas (Research Edition) dataset you need to manually register and download at https://www.mapillary.com/dataset/vistas You will receive an email with download instructions. 
Note: RVC2022 uses *MVD v1.2*!
Save/Move the downloaded zip file into the folder RVC_DATA_DIR/mvd.

5. After successfully downloading all datasets, execute ``` bash extract_and_cleanup.sh ``` to extract and delete clean up files.

### Dataset remapping ###

RVC does not force you to remap the datasets in a certain way. We do provide a "best-effort" mapping, which can be a good starting point. This mapping will contain overlapping classes and some dataset entries might miss relevant labels (as they were annotated using different policies/mixed hierarchical  levels). Combine and remap datasets by executing the script 

 ```bash remap_obj_det.sh ```

## Dataset Format / Training ##

The above step creates a joint training and a separate joint validation json file in COCO Object Detection format (only bbox entries, without "segmentation" entries):

http://cocodataset.org/#format-data

The "file_name" tag of each image entry has been prepended with the relative path calculated from RVC_DATA_DIR.
These files can directly be used in your object detector training framework.
We provide a version of [MMDetection](https://github.com/michaelisc/mmdetection_rvc) that was adapted for the challenge at https://github.com/michaelisc/mmdetection_rvc.

## Result Submission ##

The devkit contains code to remap and convert your predictions so they are ready for submission.

1. Fill in the "Register Method to RVC" form here: http://www.robustvision.net/submit.php

2. Run the evaluation for the test set of each dataset individually as specified on http://www.robustvision.net/submit.php .

3. Map predictions back into the embedding space of the respective dataset. For predictions in the coco format we provide a script to map the predicted categories back from the joint embedding space. See details below. 

4. Upload your predictions for the respective test sets of each benchmark:

- COCO : https://codalab.lisn.upsaclay.fr/competitions/6420#participate
- MVD (v1.2): https://codalab.lisn.upsaclay.fr/competitions/7515
- OID : https://www.kaggle.com/competitions/open-images-object-detection-rvc-2022-edition

For COCO and MVD the predictions must be renamed to detections_test2017_METHOD_results.json (COCO) or detections_test_METHOD_results.json (MVD) respectively and compressed into a single .zip file. 
METHOD should be replaced with your method's name.
The json should contain a list of dicts where each dict represent one bbox; e.g. 
 ```{'category_id': 7, 'bbox':[300.122, 700.356, 50.2, 23.1], 'image_id': <specific_to_dataset>, score: 0.7} ```; note that the bbox has x0,y0,w,h style.
For OID the file name does not matter but you have to upload the automatically generated OID style .csv file instead of the COCO style .json.
For MVD, the 'image_id' is expected to be a string of the 22 character image filename without file extension.
For COCO, the 'image_id' is an integer, which is identical to int(<file_name_without_ext>).

## Prediction remapping ## 

To remap the predictions from our joint labelling space use:

 ```bash remap_results.sh -p /path/to/predictions -d DATASET ```
 
 Replace DATASET with the corresponding datasets abbreviation:
 - `mvd` for mapillary vistas
 - `coco` for COCO 
 - `oid` for OpenImages. 


The converted predictions will be saved in the same location as the predictions but the filename fill be changed to FILENAME_remapped_results.json.

Note: this mapping (as the training mapping) is a starting point and does not represent the best approach towards solving the joint label space problem. **You can use any joint label space and method to map between src/trg spaces as long as they conform to the [RVC rules](http://www.robustvision.net/submit.php#rules2020)**.
