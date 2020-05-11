#!/bin/sh

# Downloads the COCO dataset with boxable GT. (7GB of input images and 0.24GB of annotations)
# Based on https://github.com/mseg-dataset/mseg-api-staging/blob/master/download_scripts/mseg_download_cocopanoptic.sh

# By using this script, you agree to all terms
# and conditions set forth by the creators of the
# KITTI datasets; see http://www.cvlibs.net/datasets/kitti/

RVC_KITTI_SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
# All data is downloaded to subfolders of RVC_DATA_DIR; if this is not defined: use this script's dir
if [ -z "${RVC_DATA_DIR}" ]; then
  RVC_KITTI_TRG_DIR=${RVC_OBJ365_SCRIPT_DIR}/../datasets/kitti
else
  RVC_KITTI_TRG_DIR=${RVC_DATA_DIR}/kitti
fi

# Get KITTI semantic dataset (includes input frames); together with panoptic ~ 0.3GB
KITTI_SEM_URL="https://avg-kitti.s3.eu-central-1.amazonaws.com/data_semantics.zip"
# Get KITTI annotations; 0.001GB for panoptic
KITTI_ANNOT_PANO_URL="https://avg-kitti.s3.eu-central-1.amazonaws.com/data_panoptic.zip"
wget --no-check-certificate --continue $KITTI_SEM_URL -P ${RVC_KITTI_TRG_DIR}
wget --no-check-certificate --continue $KITTI_ANNOT_PANO_URL -P ${RVC_KITTI_TRG_DIR}


echo "KITTI panoptic dataset downloaded."
RVC_KITTI_TRG_DIR=
RVC_KITTI_SCRIPT_DIR=