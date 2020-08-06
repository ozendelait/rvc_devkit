#!/bin/sh
# Converts GT from Scannet into COCO format
# requires python

RVC_SEGM_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
# All data is downloaded to subfolders of RVC_DATA_DIR; if this is not defined: use the root dir + /datasets
if [ -z "${RVC_DATA_DIR}" ]; then
  RVC_DATA_SRC_DIR=${RVC_OBJ_DET_SCRIPT_DIR}/../datasets/scannet
else
  RVC_DATA_SRC_DIR=${RVC_DATA_DIR}/scannet
fi

if [ -z "${RVC_JOINED_TRG_DIR}" ]; then
  RVC_DATA_TRG_DIR=${RVC_DATA_SRC_DIR}/
else
  RVC_DATA_TRG_DIR=${RVC_JOINED_TRG_DIR}/
fi
#check if scannet has already been converted 
if [ ! -f "$RVC_DATA_SRC_DIR/oid/annotations/openimages_challenge_2019_train_panoptic.json" ]; then
  echo "Converting Scannet to COCO format..."
  RVC_SCANNET_CONV_SCRIPT_DIR=${RVC_SEGM_SCRIPT_DIR}/conv_scannet
  if [ ! -d $RVC_SCANNET_CONV_SCRIPT_DIR ]; then
  # getting defined version of Scannet convert2panoptic.py script
    mkdir -p $RVC_SCANNET_CONV_SCRIPT_DIR
    wget --no-check-certificate --continue https://raw.githubusercontent.com/ScanNet/ScanNet/2c2f8003e6f4eb122dc96bcb2e072f9813fc73ab/BenchmarkScripts/convert2panoptic.py -P $RVC_SCANNET_CONV_SCRIPT_DIR
  fi
  
  #remapping Scannet format to COCO
  pushd $RVC_SCANNET_CONV_SCRIPT_DIR
    python convert2panoptic.py --dataset-folder ${RVC_DATA_SRC_DIR}/scannet_frames_25k/ --output-folder ${RVC_DATA_TRG_DIR}
  popd
  RVC_SCANNET_CONV_SCRIPT_DIR=
fi

RVC_DATA_TRG_DIR=
RVC_DATA_SRC_DIR=
RVC_SEGM_SCRIPT_DIR=

echo "Finished converting."
