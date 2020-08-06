#!/bin/sh
# Converts GT from MVD into COCO format
# requires python and theses packages:
# pip install numpy
# pip install tqdm
# pip install umsgpack
# pip install pillow
# pip install git+git://github.com/waspinator/pycococreator.git@0.2.0

# if pycocotools ois missing, you may fix this by installing
# sudo apt-get install python<YourVersion>-dev
# pip install Cython
# pip install pycocotools 

RVC_SEGM_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
RVC_MVD_SRC_DIR=${1}
  
#check if MVD has already been converted 
if [ ! -f "$RVC_DATA_SRC_DIR/mvd/panoptic/coco/training.json" ]; then
  echo "Converting MVD training data to COCO panoptic format..."

  if [ ! -d $RVC_SEGM_SCRIPT_DIR/seamseg ]; then
  # getting defined version of seamseg repo
    git -C $RVC_SEGM_SCRIPT_DIR clone https://github.com/mapillary/seamseg.git
    git -C $RVC_SEGM_SCRIPT_DIR/seamseg checkout 2b93918cd8d89e4f55fef1aac8ebec96c849379f
    #git -C $RVC_SEGM_SCRIPT_DIR/seamseg apply $RVC_SEGM_SCRIPT_DIR/seamseg.patch
  fi

  pushd ${RVC_SEGM_SCRIPT_DIR}/seamseg/scripts/data_preparation
    mkdir -p ${RVC_MVD_SRC_DIR}/panoptic
    python prepare_vistas.py ${RVC_MVD_SRC_DIR} ${RVC_MVD_SRC_DIR}/panoptic
  popd
fi


RVC_MVD_SRC_DIR=
RVC_SEGM_SCRIPT_DIR=

echo "Finished converting."
