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
#TODO: Scannet

#convert oid gt
$RVC_OBJ_DET_SCRIPT_DIR/../objdet/convert_oid_coco.sh

python $RVC_OBJ_DET_SCRIPT_DIR/../common/remap_coco.py --input $RVC_DATA_SRC_DIR/coco/annotations/instances_val2017.json \
                        --mapping $RVC_OBJ_DET_SCRIPT_DIR/inst_mapping.csv \
                        --mapping_row coco_inst_name \
                        --image_root_rel $RVC_DATA_SRC_DIR/coco/images \
                        --void_id 0 \
                        --output $RVC_DATA_TRG_DIR/coco_inst.rvc_val.json

python $RVC_OBJ_DET_SCRIPT_DIR/../common/remap_coco.py --input $RVC_DATA_SRC_DIR/coco/annotations/instances_train2017.json \
                        --mapping $RVC_OBJ_DET_SCRIPT_DIR/inst_mapping.csv \
                        --mapping_row coco_inst_name \
                        --image_root_rel $RVC_DATA_SRC_DIR/coco/images \
                        --void_id 0 \
                        --output $RVC_DATA_TRG_DIR/coco_inst.rvc_train.json

python $RVC_OBJ_DET_SCRIPT_DIR/../common/remap_coco.py --input $RVC_DATA_SRC_DIR/oid/annotations/openimages_v6_val_bbox.json \
                        --mapping $RVC_OBJ_DET_SCRIPT_DIR/inst_mapping.csv \
                        --mapping_row oid_boxable_leaf \
                        --image_root_rel $RVC_DATA_SRC_DIR/oid/val/ \
                        --void_id 0 \
                        --reduce_boxable \
                        --output $RVC_DATA_TRG_DIR/oid_inst.rvc_val.json

python $RVC_OBJ_DET_SCRIPT_DIR/../common/remap_coco.py --input $RVC_DATA_SRC_DIR/oid/annotations/openimages_v6_train_bbox.json \
                        --mapping $RVC_OBJ_DET_SCRIPT_DIR/inst_mapping.csv \
                        --mapping_row oid_boxable_leaf \
                        --image_root_rel "$RVC_DATA_SRC_DIR/oid/train_{file_name[0]}/" \
                        --void_id 0 \
                        --reduce_boxable \
                        --output $RVC_DATA_TRG_DIR/oid_inst.rvc_train.json

python $RVC_OBJ_DET_SCRIPT_DIR/../common/remap_coco.py --input $RVC_DATA_SRC_DIR/mvs/validation/panoptic/panoptic_2018.json \
                        --mapping $RVC_OBJ_DET_SCRIPT_DIR/inst_mapping.csv \
                        --mapping_row mvs_inst_name \
                        --image_root_rel $RVC_DATA_SRC_DIR/mvs/validation/images \
                        --annotation_root_rel $RVC_DATA_SRC_DIR/mvs/validation/panoptic \
                        --void_id 0 \
                        --output $RVC_DATA_TRG_DIR/mvs_inst.rvc_val.json

python $RVC_OBJ_DET_SCRIPT_DIR/../common/remap_coco.py --input $RVC_DATA_SRC_DIR/mvs/training/panoptic/panoptic_2018.json  \
                        --mapping $RVC_OBJ_DET_SCRIPT_DIR/inst_mapping.csv \
                        --mapping_row mvs_inst_name \
                        --image_root_rel $RVC_DATA_SRC_DIR/mvs/training/images  \
                        --annotation_root_rel $RVC_DATA_SRC_DIR/mvs/training/panoptic \
                        --void_id 0 \
                        --output $RVC_DATA_TRG_DIR/mvs_inst.rvc_train.json

#Creates random split for train/val (currently no specific split supplied)
python $RVC_OBJ_DET_SCRIPT_DIR/../common/rvc_split_coco.py --input $RVC_DATA_SRC_DIR/wilddash/panoptic.json --split "80;20" --output $RVC_DATA_SRC_DIR/wilddash/instances.json

python $RVC_OBJ_DET_SCRIPT_DIR/../common/remap_coco.py --input $RVC_DATA_SRC_DIR/wilddash/instances_0.json \
                        --mapping $RVC_OBJ_DET_SCRIPT_DIR/inst_mapping.csv \
                        --mapping_row wilddash_inst_name \
                        --image_root_rel $RVC_DATA_SRC_DIR/wilddash/images \
                        --annotation_root_rel $RVC_DATA_SRC_DIR/wilddash/panoptic \
                        --void_id 0 \
                        --output $RVC_DATA_TRG_DIR/wd2_inst.rvc_train.json

python $RVC_OBJ_DET_SCRIPT_DIR/../common/remap_coco.py --input $RVC_DATA_SRC_DIR/wilddash/instances_1.json \
                        --mapping $RVC_OBJ_DET_SCRIPT_DIR/inst_mapping.csv \
                        --mapping_row wilddash_inst_name \
                        --image_root_rel $RVC_DATA_SRC_DIR/wilddash/images \
                        --annotation_root_rel $RVC_DATA_SRC_DIR/wilddash/panoptic \
                        --void_id 0 \
                        --output $RVC_DATA_TRG_DIR/wd2_inst.rvc_val.json
                        
python $RVC_OBJ_DET_SCRIPT_DIR/../common/remap_coco.py --input $RVC_DATA_SRC_DIR/cityscapes/panoptic/cityscapes_panoptic_val.json \
                        --mapping $RVC_OBJ_DET_SCRIPT_DIR/inst_mapping.csv \
                        --mapping_row cityscapes_inst_name \
                        --image_root_rel $RVC_DATA_SRC_DIR/cityscapes/leftImg8bit_sequence/val/{frame_name_su[0]}/ \
                        --annotation_root_rel $RVC_DATA_SRC_DIR/cityscapes/panoptic/cityscapes_panoptic_val/ \
                        --void_id 0 \
                        --output $RVC_DATA_TRG_DIR/cs_inst.rvc_train.json

python $RVC_OBJ_DET_SCRIPT_DIR/../common/remap_coco.py --input $RVC_DATA_SRC_DIR/cityscapes/panoptic/cityscapes_panoptic_train.json \
                        --mapping $RVC_OBJ_DET_SCRIPT_DIR/inst_mapping.csv \
                        --mapping_row cityscapes_inst_name \
                        --image_root_rel $RVC_DATA_SRC_DIR/cityscapes/leftImg8bit_sequence/train/{frame_name_su[0]}/ \
                        --annotation_root_rel $RVC_DATA_SRC_DIR/cityscapes/panoptic/cityscapes_panoptic_train/ \
                        --void_id 0 \
                        --output $RVC_DATA_TRG_DIR/cs_inst.rvc_val.json
                        
pushd $RVC_DATA_TRG_DIR
python $RVC_OBJ_DET_SCRIPT_DIR/../common/join_coco.py --join "coco_inst.rvc_val.json;oid.rvc_train.json;wd2_inst.rvc_val.json;cs_inst.rvc_train.json;mvs_inst.rvc_val.json" \
       --output joined_val_inst.json
python $RVC_OBJ_DET_SCRIPT_DIR/../common/join_coco.py --join "coco_inst.rvc_train.json;oid.rvc_train.json;wd2_inst.rvc_train.json;cs_inst.rvc_val.json;mvs_inst.rvc_train.json" \
       --output joined_train_inst.json
popd

RVC_DATA_TRG_DIR=
RVC_DATA_SRC_DIR=
RVC_OBJ_DET_SCRIPT_DIR=

echo "Finished remapping."

