#!/bin/sh

# Downloads the COCO dataset with boxable GT. (7GB of input images and 0.24GB of annotations)
# Based on https://github.com/mseg-dataset/mseg-api/blob/master/download_scripts/mseg_download_cocopanoptic.sh

# By using this script, you agree to all terms
# and conditions set forth by the creators of the
# COCO Stuff, MS COCO, and COCO Boxable datasets.

# ----------- Directory Setup -----------------------
# Destination directory for MSeg
RVC_COCO_SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
# All data is downloaded to subfolders of RVC_DATA_DIR; if this is not defined: use this script's dir
if [ -z "${RVC_DATA_DIR}" ]; then
  RVC_COCO_TRG_DIR=${RVC_OBJ365_SCRIPT_DIR}/../datasets/coco
else
  RVC_COCO_TRG_DIR=${RVC_DATA_DIR}/coco
fi

$RVC_COCO_SCRIPT_DIR/../objdet/download_coco_boxable.sh
# Get the annotations; 0.9GB for panoptic
COCOP_ANNOT_PANO_URL="http://images.cocodataset.org/annotations/panoptic_annotations_trainval2017.zip"
wget --no-check-certificate --continue $COCOP_ANNOT_PANO_URL -P ${RVC_DOWNL_SEM_TRG_DIR}/coco

echo "COCO panoptic dataset downloaded."
