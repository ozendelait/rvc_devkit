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


#TODO: cityscapes
#TODO: KITTI
#TODO: VIPER

python $RVC_OBJ_DET_SCRIPT_DIR/../common/remap_coco.py --input $RVC_DATA_SRC_DIR/coco/annotations/instances_val2017.json \
                        --mapping $RVC_OBJ_DET_SCRIPT_DIR/pano_mapping.csv \
                        --mapping_row coco_boxable_name \
                        --image_root_rel $RVC_DATA_SRC_DIR/coco/images \
                        --void_id 255 \
                        --output $RVC_DATA_TRG_DIR/coco_pano.rvc_val.json

python $RVC_OBJ_DET_SCRIPT_DIR/../common/remap_coco.py --input $RVC_DATA_SRC_DIR/coco/annotations/instances_train2017.json \
                        --mapping $RVC_OBJ_DET_SCRIPT_DIR/pano_mapping.csv \
                        --mapping_row coco_boxable_name \
                        --image_root_rel $RVC_DATA_SRC_DIR/coco/images \
                        --void_id 255 \
                        --output $RVC_DATA_TRG_DIR/coco_pano.rvc_train.json

python $RVC_OBJ_DET_SCRIPT_DIR/../common/remap_coco.py --input $RVC_DATA_SRC_DIR/mvs/panoptic/coco/validation.json \
                        --mapping $RVC_OBJ_DET_SCRIPT_DIR/pano_mapping.csv \
                        --mapping_row mvs_boxable_name \
                        --image_root_rel $RVC_DATA_SRC_DIR/mvs/validation/images \
                        --void_id 255 \
                        --output $RVC_DATA_TRG_DIR/mvs_pano.rvc_val.json

python $RVC_OBJ_DET_SCRIPT_DIR/../common/remap_coco.py --input $RVC_DATA_SRC_DIR/mvs/panoptic/coco/training.json \
                        --mapping $RVC_OBJ_DET_SCRIPT_DIR/pano_mapping.csv \
                        --mapping_row mvs_boxable_name \
                        --image_root_rel $RVC_DATA_SRC_DIR/mvs/training/images  \
                        --void_id 255 \
                        --output $RVC_DATA_TRG_DIR/mvs_pano.rvc_train.json

#TODO: add train/val split for WildDash
python $RVC_OBJ_DET_SCRIPT_DIR/../common/remap_coco.py --input $RVC_DATA_SRC_DIR/wilddash/panoptic.json \
                        --mapping $RVC_OBJ_DET_SCRIPT_DIR/pano_mapping.csv \
                        --mapping_row mvs_boxable_name \
                        --image_root_rel $RVC_DATA_SRC_DIR/mvs/validation/images \
                        --void_id 0 \
                        --output $RVC_DATA_TRG_DIR/wd2_pano.rvc_train.json


                        
                        
pushd $RVC_DATA_TRG_DIR
python $RVC_OBJ_DET_SCRIPT_DIR/../common/join_coco.py --join "coco_pano.rvc_val.json;wd2_pano.rvc_val.json;mvs_pano.rvc_val.json" \
       --output joined_val_pano.json
python $RVC_OBJ_DET_SCRIPT_DIR/../common/join_coco.py --join "coco_pano.rvc_train.json;wd2_pano.rvc_train.json;mvs_pano.rvc_train.json" \
       --output joined_train_pano.json
popd

RVC_DATA_TRG_DIR=
RVC_DATA_SRC_DIR=
RVC_OBJ_DET_SCRIPT_DIR=

echo "Finished remapping."

