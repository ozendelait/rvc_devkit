#!/bin/sh

# Downloads the KITTI dataset with panoptic GT. (~0.5GB of input images and annotations)
# Based on https://github.com/mseg-dataset/mseg-api/blob/master/download_scripts/mseg_download_cocopanoptic.sh

# By using this script, you agree to all terms
# and conditions set forth by the creators of the
# KITTI datasets; see http://www.cvlibs.net/datasets/kitti/

RVC_KITTI_TRG_DIR=$1

# Get KITTI semantic dataset (includes input frames); together with panoptic ~ 0.3GB
KITTI_SEM_URL="https://avg-kitti.s3.eu-central-1.amazonaws.com/data_semantics.zip"
# Get KITTI annotations; 0.001GB for panoptic
KITTI_ANNOT_PANO_URL="https://avg-kitti.s3.eu-central-1.amazonaws.com/data_panoptic.zip"
wget --no-check-certificate --continue $KITTI_SEM_URL -P ${RVC_KITTI_TRG_DIR}
wget --no-check-certificate --continue $KITTI_ANNOT_PANO_URL -P ${RVC_KITTI_TRG_DIR}


echo "KITTI panoptic dataset downloaded."
RVC_KITTI_TRG_DIR=
