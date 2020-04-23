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
  RVC_DATA_TRG_DIR=${RVC_DATA_SRC_DIR}/
else
  RVC_DATA_TRG_DIR=${RVC_JOINED_TRG_DIR}/
fi

#check if oid has already been converted 
if [ ! -f "$RVC_DATA_SRC_DIR/oid/annotations/openimages_v6_val_bbox.json" ]; then
  echo "Converting OID to COCO format..."
  if [ ! -d $RVC_OBJ_DET_SCRIPT_DIR/openimages2coco ]; then
  # getting defined version of openimages2coco repo
    git -C $RVC_OBJ_DET_SCRIPT_DIR clone https://github.com/bethgelab/openimages2coco.git 
    git -C $RVC_OBJ_DET_SCRIPT_DIR/openimages2coco checkout aebb4d128007f04579d18e32c49c3de0013834be
  fi
  
  #remapping OID format to COCO
  python $RVC_OBJ_DET_SCRIPT_DIR/openimages2coco/convert.py --path $RVC_DATA_SRC_DIR/oid/
fi

echo "Joining dataset from ${RVC_DATA_SRC_DIR} to ${RVC_DATA_TRG_DIR}"
mkdir -p ${RVC_DATA_TRG_DIR}


python $RVC_OBJ_DET_SCRIPT_DIR/remap_boxable.py --input $RVC_DATA_SRC_DIR/coco/annotations/instances_val2017.json \
                        --mapping $RVC_OBJ_DET_SCRIPT_DIR/obj_det_mapping.csv \
                        --mapping_row coco_boxable_name \
                        --image_root_rel $RVC_DATA_SRC_DIR/coco/images \
                        --void_id 0 \
                        --reduce_size \
                        --output $RVC_DATA_TRG_DIR/joined_boxable_val.json

python $RVC_OBJ_DET_SCRIPT_DIR/remap_boxable.py --input $RVC_DATA_SRC_DIR/coco/annotations/instances_train2017.json \
                        --mapping $RVC_OBJ_DET_SCRIPT_DIR/obj_det_mapping.csv \
                        --mapping_row coco_boxable_name \
                        --image_root_rel $RVC_DATA_SRC_DIR/coco/images \
                        --void_id 0 \
                        --reduce_size \
                        --output $RVC_DATA_TRG_DIR/joined_boxable_train.json

python $RVC_OBJ_DET_SCRIPT_DIR/remap_boxable.py --input $RVC_DATA_SRC_DIR/objects365/objects365v2_val_0422.json \
                        --mapping $RVC_OBJ_DET_SCRIPT_DIR/obj_det_mapping.csv \
                        --mapping_row obj365_boxable_name \
                        --image_root_rel $RVC_DATA_SRC_DIR/objects365/
                        --void_id 0 \
                        --do_merging \
                        --reduce_size \
                        --output $RVC_DATA_TRG_DIR/joined_boxable_val.json

python $RVC_OBJ_DET_SCRIPT_DIR/remap_boxable.py --input $RVC_DATA_SRC_DIR/objects365/objects365v2_train_0422.json \
                        --mapping $RVC_OBJ_DET_SCRIPT_DIR/obj_det_mapping.csv \
                        --mapping_row obj365_boxable_name \
                        --image_root_rel $RVC_DATA_SRC_DIR/objects365/
                        --void_id 0 \
                        --do_merging \
                        --reduce_size \
                        --output $RVC_DATA_TRG_DIR/joined_boxable_train.json

python $RVC_OBJ_DET_SCRIPT_DIR/remap_boxable.py --input $RVC_DATA_SRC_DIR/oid/annotations/openimages_v6_val_bbox.json \
                        --mapping $RVC_OBJ_DET_SCRIPT_DIR/obj_det_mapping.csv \
                        --mapping_row oid_boxable_leaf \
                        --image_root_rel $RVC_DATA_SRC_DIR/oid/val/ \
                        --void_id 0 \
                        --do_merging \
                        --reduce_size \
                        --output $RVC_DATA_TRG_DIR/joined_boxable_val.json

python $RVC_OBJ_DET_SCRIPT_DIR/remap_boxable.py --input $RVC_DATA_SRC_DIR/oid/annotations/openimages_v6_train_bbox.json \
                        --mapping $RVC_OBJ_DET_SCRIPT_DIR/obj_det_mapping.csv \
                        --mapping_row oid_boxable_leaf \
                        --image_root_rel "$RVC_DATA_SRC_DIR/oid/train_{file_name[0]}/" \
                        --void_id 0 \
                        --do_merging \
                        --reduce_size \
                        --output $RVC_DATA_TRG_DIR/joined_boxable_train.json

python $RVC_OBJ_DET_SCRIPT_DIR/remap_boxable.py --input $RVC_DATA_SRC_DIR/oid/annotations/openimages_v6_test_bbox.json \
                        --mapping $RVC_OBJ_DET_SCRIPT_DIR/obj_det_mapping.csv \
                        --mapping_row oid_boxable_leaf \
                        --image_root_rel $RVC_DATA_SRC_DIR/oid/test/ \
                        --void_id 0 \
                        --reduce_size \
                        --output $RVC_DATA_TRG_DIR/joined_boxable_test.json

python $RVC_OBJ_DET_SCRIPT_DIR/remap_boxable.py --input $RVC_DATA_SRC_DIR/mvs/panoptic/coco/validation.json \
                        --mapping $RVC_OBJ_DET_SCRIPT_DIR/obj_det_mapping.csv \
                        --mapping_row mvs_boxable_name \
                        --image_root_rel $RVC_DATA_SRC_DIR/mvs/validation/images \
                        --void_id 0 \
                        --do_merging \
                        --reduce_size \
                        --output $RVC_DATA_TRG_DIR/joined_boxable_val.json

python $RVC_OBJ_DET_SCRIPT_DIR/remap_boxable.py --input $RVC_DATA_SRC_DIR/mvs/panoptic/coco/training.json \
                        --mapping $RVC_OBJ_DET_SCRIPT_DIR/obj_det_mapping.csv \
                        --mapping_row mvs_boxable_name \
                        --image_root_rel $RVC_DATA_SRC_DIR/mvs/training/images  \
                        --void_id 0 \
                        --do_merging \
                        --reduce_size \
                        --output $RVC_DATA_TRG_DIR/joined_boxable_train.json



RVC_DATA_TRG_DIR=
RVC_DATA_SRC_DIR=
RVC_OBJ_DET_SCRIPT_DIR=

echo "Finished remapping."

