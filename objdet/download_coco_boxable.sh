#!/bin/sh

# Downloads the COCO dataset with boxable GT. (25GB of input images and 1GB of annotations)
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

# ----------- Downloading ---------------------------
mkdir -p $RVC_COCO_TRG_DIR
cd $RVC_COCO_TRG_DIR
echo "Downloading COCO boxable dataset..."
# Get the annotations; 0.25GB for boxable 0.9GB for panoptic
COCOP_ANNOT_BOX_URL="http://images.cocodataset.org/annotations/annotations_trainval2017.zip"
wget --no-check-certificate --continue $COCOP_ANNOT_BOX_URL -P ${RVC_COCO_TRG_DIR}

COCOP_ANNOT_TEST_URL="http://images.cocodataset.org/annotations/image_info_test2017.zip"
wget --no-check-certificate --continue $COCOP_ANNOT_TEST_URL -P ${RVC_COCO_TRG_DIR}

# train2017.zip will be 19GB.
TRAIN_IMGS_URL="http://images.cocodataset.org/zips/train2017.zip"
wget --no-check-certificate --continue $TRAIN_IMGS_URL  -P ${RVC_COCO_TRG_DIR}
# val2017.zip will be 1GB.
VAL_IMGS_URL="http://images.cocodataset.org/zips/val2017.zip"
wget --no-check-certificate --continue $VAL_IMGS_URL  -P ${RVC_COCO_TRG_DIR}
# test2017.zip will be 6GB.
TEST_IMGS_URL="http://images.cocodataset.org/zips/test2017.zip"
wget --no-check-certificate --continue $TEST_IMGS_URL  -P ${RVC_COCO_TRG_DIR}

echo "COCO boxable dataset downloaded."
