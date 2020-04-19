#!/bin/sh
# Remaps individual boxable ground truth of RVC datasets into a joint dataset
# requires git, python and pycocotools which can be installed via:
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

#remapping OID format to COCO
python $RVC_OBJ_DET_SCRIPT_DIR/openimages2coco/convert.py --path $RVC_DATA_SRC_DIR/oid/

echo "Joining dataset from ${RVC_DATA_SRC_DIR} to ${RVC_DATA_TRG_DIR}"
mkdir -p ${RVC_DATA_TRG_DIR}

python $RVC_OBJ_DET_SCRIPT_DIR/remap_boxable.py --input $RVC_DATA_SRC_DIR/coco/annotations/instances_val2017.json \
                        --mapping $RVC_OBJ_DET_SCRIPT_DIR/obj_det_mapping.csv \
                        --mapping_row coco_boxable_name \
                        --image_root ../coco/images \
                        --void_id 0 \
                        --output $RVC_DATA_TRG_DIR/joined_boxable_val.json

python $RVC_OBJ_DET_SCRIPT_DIR/remap_boxable.py --input $RVC_DATA_SRC_DIR/coco/annotations/instances_train2017.json \
                        --mapping $RVC_OBJ_DET_SCRIPT_DIR/obj_det_mapping.csv \
                        --mapping_row coco_boxable_name \
                        --image_root ../coco/images \
                        --void_id 0 \
                        --output $RVC_DATA_TRG_DIR/joined_boxable_train.json

python $RVC_OBJ_DET_SCRIPT_DIR/remap_boxable.py --input $RVC_DATA_SRC_DIR/oid/openimages_v6_val_bbox.json \
                        --mapping $RVC_OBJ_DET_SCRIPT_DIR/obj_det_mapping.csv \
                        --mapping_row oid_boxable_leaf \
                        --image_root ../oid/ \
                        --void_id 0 \
                        --do_merging
                        --output $RVC_DATA_TRG_DIR/joined_boxable_val.json

python $RVC_OBJ_DET_SCRIPT_DIR/remap_boxable.py --input $RVC_DATA_SRC_DIR/oid/openimages_v6_train_bbox.json \
                        --mapping $RVC_OBJ_DET_SCRIPT_DIR/obj_det_mapping.csv \
                        --mapping_row oid_boxable_leaf \
                        --image_root ../oid/ \
                        --void_id 0 \
                        --do_merging
                        --output $RVC_DATA_TRG_DIR/joined_boxable_train.json

python $RVC_OBJ_DET_SCRIPT_DIR/remap_boxable.py --input $RVC_DATA_SRC_DIR/oid/openimages_v6_test_bbox.json \
                        --mapping $RVC_OBJ_DET_SCRIPT_DIR/obj_det_mapping.csv \
                        --mapping_row oid_boxable_leaf \
                        --image_root ../oid/ \
                        --void_id 0 \
                        --output $RVC_DATA_TRG_DIR/joined_boxable_test.json

#TODO execute remapping for Obj365
#TODO execute remapping for MVS



RVC_DATA_TRG_DIR=
RVC_DATA_SRC_DIR=
RVC_OBJ_DET_SCRIPT_DIR=

echo "Finished remapping."

