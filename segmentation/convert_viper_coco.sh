#!/bin/bash
# Converts GT from VIPER into COCO format
# requires python

RVC_SEGM_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
# All data is downloaded to subfolders of RVC_DATA_DIR; if this is not defined: use the root dir + /datasets
if [ -z "${RVC_DATA_DIR}" ]; then
  RVC_DATA_SRC_DIR=${RVC_SEGM_SCRIPT_DIR}/../datasets/
else
  RVC_DATA_SRC_DIR=${RVC_DATA_DIR}/
fi

#check if VIPER has already been converted 
if [ ! -f "$RVC_DATA_SRC_DIR/viper/train/pano.json" ]; then
  echo "Converting VIPER training data to COCO format..."

  pushd ${RVC_SEGM_SCRIPT_DIR}/legacy/
  python3 convert_viper_pano.py ${RVC_DATA_SRC_DIR}/viper train --label_definition ${RVC_SEGM_SCRIPT_DIR}/../common/label_definitions/viper_classes.csv
  popd
fi

if [ ! -f "$RVC_DATA_SRC_DIR/viper/val/pano.json" ]; then
  echo "Converting VIPER validation data to COCO format..."

  pushd ${RVC_SEGM_SCRIPT_DIR}/legacy/
  python3 convert_viper_pano.py ${RVC_DATA_SRC_DIR}/viper val --label_definition ${RVC_SEGM_SCRIPT_DIR}/../common/label_definitions/viper_classes.csv
  popd
fi

RVC_DATA_TRG_DIR=
RVC_DATA_SRC_DIR=
RVC_SEGM_SCRIPT_DIR=

echo "Finished converting."
