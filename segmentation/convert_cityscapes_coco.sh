#!/bin/bash
# Converts GT from cityscapes into COCO format
# requires git, python
# (use gitbash for MS Windows)

RVC_SEGM_SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
# All data is downloaded to subfolders of RVC_DATA_DIR; if this is not defined: use the root dir + /datasets
if [ -z "${RVC_DATA_DIR}" ]; then
  RVC_DATA_SRC_DIR=${RVC_SEGM_SCRIPT_DIR}/../datasets/
else
  RVC_DATA_SRC_DIR=${RVC_DATA_DIR}/
fi

if [ -z "${RVC_JOINED_TRG_DIR}" ]; then
  RVC_DATA_TRG_DIR=${RVC_DATA_SRC_DIR}/
else
  RVC_DATA_TRG_DIR=${RVC_JOINED_TRG_DIR}/
fi

#check if cityscapes has already been converted 
if [ ! -f "$RVC_DATA_SRC_DIR/cityscapes/panoptic/cityscapes_panoptic_test.json" ]; then
  echo "Converting Cityscapes to COCO format..."
  if [ ! -d $RVC_SEGM_SCRIPT_DIR/cityscapesScripts ]; then
  # getting defined version of cityscapesScripts repo
    git -C $RVC_SEGM_SCRIPT_DIR clone https://github.com/mcordts/cityscapesScripts.git
    git -C $RVC_SEGM_SCRIPT_DIR/cityscapesScripts checkout ec896c1817db096c402c44a8bafec461ef887b19
  fi
  
  #remap cityscapes format to COCO
  mkdir -p "$RVC_DATA_SRC_DIR/cityscapes/panoptic/"
  PYTHONPATH=$RVC_SEGM_SCRIPT_DIR/cityscapesScripts python3 $RVC_SEGM_SCRIPT_DIR/cityscapesScripts/cityscapesscripts/preparation/createPanopticImgs.py --dataset-folder "$RVC_DATA_SRC_DIR/cityscapes/gtFine/" --output-folder "$RVC_DATA_SRC_DIR/cityscapes/panoptic/"
fi

RVC_DATA_TRG_DIR=
RVC_DATA_SRC_DIR=
RVC_SEGM_SCRIPT_DIR=

echo "Finished remapping."
