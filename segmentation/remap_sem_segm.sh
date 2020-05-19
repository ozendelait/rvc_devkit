#!/bin/sh
# Remaps individual boxable ground truth of RVC datasets into a joint dataset
# requires git, python and pycocotools which can be installed via:
# pip install pycocotools
# (use gitbash for MS Windows)

RVC_SEM_SEG_SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
# All data is downloaded to subfolders of RVC_DATA_DIR; if this is not defined: use the root dir + /datasets
if [ -z "${RVC_DATA_DIR}" ]; then
  RVC_DATA_SRC_DIR=${RVC_SEM_SEG_SCRIPT_DIR}/../datasets/
else
  RVC_DATA_SRC_DIR=${RVC_DATA_DIR}/
fi

if [ -z "${RVC_JOINED_TRG_DIR}" ]; then
  RVC_DATA_TRG_DIR=${RVC_DATA_SRC_DIR}/rvc_uint8
else
  RVC_DATA_TRG_DIR=${RVC_JOINED_TRG_DIR}/
fi

if [ ! -d $RVC_SEM_SEG_SCRIPT_DIR/mseg-api ]; then
  # getting defined version of mseg repo
  git -C $RVC_SEM_SEG_SCRIPT_DIR clone https://github.com/mseg-dataset/mseg-api.git 
  git -C $RVC_SEM_SEG_SCRIPT_DIR/mseg-api checkout 29f40956abd227aa7d454f05cd8f007de0d12a09
  #git -C $RVC_SEM_SEG_SCRIPT_DIR/openimages2coco apply $RVC_SEM_SEG_SCRIPT_DIR/openimages2coco.patch
fi

mkdir -p ${RVC_DATA_TRG_DIR}

pushd $RVC_SEM_SEG_SCRIPT_DIR/
  python ./mseg-api/mseg/label_preparation/remap_dataset.py --orig_dname ade20k-151 --remapped_dname rvc_uint8 --orig_dataroot ${RVC_DATA_SRC_DIR}/ade20k --remapped_dataroot ${RVC_DATA_TRG_DIR} --mapping_tsv ./ss_mapping_uint8_mseg.tsv
popd

RVC_DATA_TRG_DIR=
RVC_DATA_SRC_DIR=
RVC_SEM_SEG_SCRIPT_DIR=

echo "Finished remapping."

