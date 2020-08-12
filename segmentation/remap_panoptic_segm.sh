#!/bin/bash
# Remaps individual panoptic ground truth of RVC datasets into a joint dataset
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

if [ ! -f "$RVC_DATA_TRG_DIR/coco_pano.rvc_val.json" ]; then
  python3 $RVC_OBJ_DET_SCRIPT_DIR/../common/remap_coco.py --input $RVC_DATA_SRC_DIR/coco/annotations/panoptic_val2017.json \
                        --mapping $RVC_OBJ_DET_SCRIPT_DIR/pano_mapping.csv \
                        --mapping_row coco_pano_name \
                        --image_root_rel $RVC_DATA_SRC_DIR/coco/images \
                        --annotation_root_rel $RVC_DATA_SRC_DIR/coco/annotations/panoptic_val2017/ \
                        --void_id 0 \
                        --output $RVC_DATA_TRG_DIR/coco_pano.rvc_val.json
fi

if [ ! -f "$RVC_DATA_TRG_DIR/coco_pano.rvc_train.json" ]; then
  python3 $RVC_OBJ_DET_SCRIPT_DIR/../common/remap_coco.py --input $RVC_DATA_SRC_DIR/coco/annotations/panoptic_train2017.json \
                        --mapping $RVC_OBJ_DET_SCRIPT_DIR/pano_mapping.csv \
                        --mapping_row coco_pano_name \
                        --image_root_rel $RVC_DATA_SRC_DIR/coco/images \
                        --annotation_root_rel $RVC_DATA_SRC_DIR/coco/annotations/panoptic_train2017/ \
                        --void_id 0 \
                        --output $RVC_DATA_TRG_DIR/coco_pano.rvc_train.json
fi

if [ ! -f "$RVC_DATA_TRG_DIR/mvd_pano.rvc_val.json" ]; then
  python3 $RVC_OBJ_DET_SCRIPT_DIR/../common/remap_coco.py --input $RVC_DATA_SRC_DIR/mvd/validation/panoptic/panoptic_2018.json \
                        --mapping $RVC_OBJ_DET_SCRIPT_DIR/pano_mapping.csv \
                        --mapping_row mvd_pano_name \
                        --image_root_rel $RVC_DATA_SRC_DIR/mvd/validation/images \
                        --annotation_root_rel $RVC_DATA_SRC_DIR/mvd/validation/panoptic \
                        --void_id 0 \
                        --output $RVC_DATA_TRG_DIR/mvd_pano.rvc_val.json
fi

if [ ! -f "$RVC_DATA_TRG_DIR/mvd_pano.rvc_train.json" ]; then
  python3 $RVC_OBJ_DET_SCRIPT_DIR/../common/remap_coco.py --input $RVC_DATA_SRC_DIR/mvd/training/panoptic/panoptic_2018.json  \
                        --mapping $RVC_OBJ_DET_SCRIPT_DIR/pano_mapping.csv \
                        --mapping_row mvd_pano_name \
                        --image_root_rel $RVC_DATA_SRC_DIR/mvd/training/images  \
                        --annotation_root_rel $RVC_DATA_SRC_DIR/mvd/training/panoptic \
                        --void_id 0 \
                        --output $RVC_DATA_TRG_DIR/mvd_pano.rvc_train.json
fi

if [ ! -f "$RVC_DATA_TRG_DIR/viper_pano.rvc_train.json" ]; then
  python3 $RVC_OBJ_DET_SCRIPT_DIR/../common/remap_coco.py --input $RVC_DATA_SRC_DIR/viper/train/pano.json \
                        --mapping $RVC_OBJ_DET_SCRIPT_DIR/pano_mapping.csv \
                        --mapping_row viper_pano_name \
                        --image_root_rel $RVC_DATA_SRC_DIR/viper/train/img/{file_name[0]}{file_name[1]}{file_name[2]} \
                        --annotation_root_rel $RVC_DATA_SRC_DIR/viper/train/pano/{file_name[0]}{file_name[1]}{file_name[2]} \
                        --void_id 0 \
                        --output $RVC_DATA_TRG_DIR/viper_pano.rvc_train.json
fi

if [ ! -f "$RVC_DATA_TRG_DIR/viper_pano.rvc_val.json" ]; then
  python3 $RVC_OBJ_DET_SCRIPT_DIR/../common/remap_coco.py --input $RVC_DATA_SRC_DIR/viper/val/pano.json \
                        --mapping $RVC_OBJ_DET_SCRIPT_DIR/pano_mapping.csv \
                        --mapping_row viper_pano_name \
                        --image_root_rel $RVC_DATA_SRC_DIR/viper/val/img/{file_name[0]}{file_name[1]}{file_name[2]} \
                        --annotation_root_rel $RVC_DATA_SRC_DIR/viper/val/pano/{file_name[0]}{file_name[1]}{file_name[2]} \
                        --void_id 0 \
                        --output $RVC_DATA_TRG_DIR/viper_pano.rvc_val.json
fi

if [ ! -f "$RVC_DATA_SRC_DIR/wilddash/panoptic_0.json" ]; then
#Creates random split for train/val (currently no specific split supplied)
  python3 $RVC_OBJ_DET_SCRIPT_DIR/../common/rvc_split_coco.py --input $RVC_DATA_SRC_DIR/wilddash/panoptic.json --split "80;20"
fi

if [ ! -f "$RVC_DATA_SRC_DIR/wd2_pano.rvc_train.json" ]; then
  python3 $RVC_OBJ_DET_SCRIPT_DIR/../common/remap_coco.py --input $RVC_DATA_SRC_DIR/wilddash/panoptic_0.json \
                        --mapping $RVC_OBJ_DET_SCRIPT_DIR/pano_mapping.csv \
                        --mapping_row wilddash_pano_name \
                        --image_root_rel $RVC_DATA_SRC_DIR/wilddash/images \
                        --annotation_root_rel $RVC_DATA_SRC_DIR/wilddash/panoptic \
                        --void_id 0 \
                        --output $RVC_DATA_TRG_DIR/wd2_pano.rvc_train.json
fi

if [ ! -f "$RVC_DATA_SRC_DIR/wd2_pano.rvc_val.json" ]; then
  python3 $RVC_OBJ_DET_SCRIPT_DIR/../common/remap_coco.py --input $RVC_DATA_SRC_DIR/wilddash/panoptic_1.json \
                        --mapping $RVC_OBJ_DET_SCRIPT_DIR/pano_mapping.csv \
                        --mapping_row wilddash_pano_name \
                        --image_root_rel $RVC_DATA_SRC_DIR/wilddash/images \
                        --annotation_root_rel $RVC_DATA_SRC_DIR/wilddash/panoptic \
                        --void_id 0 \
                        --output $RVC_DATA_TRG_DIR/wd2_pano.rvc_val.json
fi

if [ ! -f "$RVC_DATA_SRC_DIR/cs_pano.rvc_val.json" ]; then
  python3 $RVC_OBJ_DET_SCRIPT_DIR/../common/remap_coco.py --input $RVC_DATA_SRC_DIR/cityscapes/panoptic/cityscapes_panoptic_val.json \
                        --mapping $RVC_OBJ_DET_SCRIPT_DIR/pano_mapping.csv \
                        --mapping_row cityscapes_pano_name \
                        --image_root_rel $RVC_DATA_SRC_DIR/cityscapes/leftImg8bit_sequence/val/{frame_name_su[0]}/ \
                        --annotation_root_rel $RVC_DATA_SRC_DIR/cityscapes/panoptic/cityscapes_panoptic_val/ \
                        --void_id 0 \
                        --output $RVC_DATA_TRG_DIR/cs_pano.rvc_val.json
fi

if [ ! -f "$RVC_DATA_SRC_DIR/cs_pano.rvc_train.json" ]; then
  python3 $RVC_OBJ_DET_SCRIPT_DIR/../common/remap_coco.py --input $RVC_DATA_SRC_DIR/cityscapes/panoptic/cityscapes_panoptic_train.json \
                        --mapping $RVC_OBJ_DET_SCRIPT_DIR/pano_mapping.csv \
                        --mapping_row cityscapes_pano_name \
                        --image_root_rel $RVC_DATA_SRC_DIR/cityscapes/leftImg8bit_sequence/train/{frame_name_su[0]}/ \
                        --annotation_root_rel $RVC_DATA_SRC_DIR/cityscapes/panoptic/cityscapes_panoptic_train/ \
                        --void_id 0 \
                        --output $RVC_DATA_TRG_DIR/cs_pano.rvc_train.json
fi

                        
pushd $RVC_DATA_TRG_DIR
python3 $RVC_OBJ_DET_SCRIPT_DIR/../common/join_coco.py --join "coco_pano.rvc_val.json;wd2_pano.rvc_val.json;viper_pano.rvc_val.json;cs_pano.rvc_val.json;mvd_pano.rvc_val.json" \
       --output joined_val_pano.json
python3 $RVC_OBJ_DET_SCRIPT_DIR/../common/join_coco.py --join "coco_pano.rvc_train.json;wd2_pano.rvc_train.json;viper_pano.rvc_train.json;cs_pano.rvc_train.json;mvd_pano.rvc_train.json" \
       --output joined_train_pano.json
popd

RVC_DATA_TRG_DIR=
RVC_DATA_SRC_DIR=
RVC_OBJ_DET_SCRIPT_DIR=

echo "Finished remapping."

