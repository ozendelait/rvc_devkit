#!/bin/sh
# Remaps individual boxable ground truth of RVC datasets into a joint dataset
# requires git and python3 and pycocotools which can be installed via:
# pip install pycocotools
# (use gitbash for MS Windows)

RVC_OBJ_DET_SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
# All data is downloaded to subfolders of RVC_DATA_DIR; if this is not defined: use the root dir + /datasets
if [ -z "${RVC_DATA_DIR}" ]; then
  RVC_DATA_SRC_DIR=${RVC_OBJ_DET_SCRIPT_DIR}/../datasets/
else
  RVC_DATA_SRC_DIR=${RVC_DATA_DIR}/
fi

if [ -z "${RVC_JOINED_TRG_DIR}" ]; then
  RVC_DATA_TRG_DIR=${RVC_DATA_SRC_DIR}/joined_boxable
else
  RVC_DATA_TRG_DIR=${RVC_JOINED_TRG_DIR}/
fi

if [ ! -d $RVC_OBJ_DET_SCRIPT_DIR/openimages2coco ]; then
  git -C $RVC_OBJ_DET_SCRIPT_DIR clone https://github.com/bethgelab/openimages2coco.git 
fi
#update repo (master currently under development; will fix a tag later)
git -C $RVC_OBJ_DET_SCRIPT_DIR/openimages2coco pull origin

echo "Joining dataset from ${RVC_DATA_SRC_DIR} to ${RVC_DATA_TRG_DIR}"
mkdir -p ${RVC_DATA_TRG_DIR}

#TODO execute remapping

RVC_DATA_TRG_DIR=
RVC_DATA_SRC_DIR=
RVC_OBJ_DET_SCRIPT_DIR=

echo "Finished remapping."

