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

# Convert OID gt
$RVC_OBJ_DET_SCRIPT_DIR/convert_oid_coco.sh

# Remap COCO
if [ ! -f "$RVC_DATA_TRG_DIR/coco_boxable.rvc_test.json" ]; then
    python3 $RVC_OBJ_DET_SCRIPT_DIR/../common/remap_coco.py --input $RVC_DATA_SRC_DIR/coco/annotations/image_info_test2017.json \
                            --mapping $RVC_OBJ_DET_SCRIPT_DIR/obj_det_mapping.csv \
                            --mapping_row coco_boxable_name \
                            --image_root_rel $RVC_DATA_SRC_DIR/coco/images/test2017 \
                            --void_id 0 \
                            --reduce_boxable \
                            --output $RVC_DATA_TRG_DIR/coco_boxable.rvc_test.json
fi

if [ ! -f "$RVC_DATA_TRG_DIR/coco_boxable.rvc_val.json" ]; then
    python3 $RVC_OBJ_DET_SCRIPT_DIR/../common/remap_coco.py --input $RVC_DATA_SRC_DIR/coco/annotations/instances_val2017.json \
                            --mapping $RVC_OBJ_DET_SCRIPT_DIR/obj_det_mapping.csv \
                            --mapping_row coco_boxable_name \
                            --image_root_rel $RVC_DATA_SRC_DIR/coco/images/val2017 \
                            --void_id 0 \
                            --reduce_boxable \
                            --output $RVC_DATA_TRG_DIR/coco_boxable.rvc_val.json
fi

if [ ! -f "$RVC_DATA_TRG_DIR/coco_boxable.rvc_train.json" ]; then
    python3 $RVC_OBJ_DET_SCRIPT_DIR/../common/remap_coco.py --input $RVC_DATA_SRC_DIR/coco/annotations/instances_train2017.json \
                            --mapping $RVC_OBJ_DET_SCRIPT_DIR/obj_det_mapping.csv \
                            --mapping_row coco_boxable_name \
                            --image_root_rel $RVC_DATA_SRC_DIR/coco/images/train2017 \
                            --void_id 0 \
                            --reduce_boxable \
                            --output $RVC_DATA_TRG_DIR/coco_boxable.rvc_train.json
fi

#if [ ! -f "$RVC_DATA_TRG_DIR/obj365_boxable.rvc_val.json" ]; then
#    python3 $RVC_OBJ_DET_SCRIPT_DIR/../common/remap_coco.py --input $RVC_DATA_SRC_DIR/objects365/objects365v2_val_0422.json \
#                            --mapping #$RVC_OBJ_DET_SCRIPT_DIR/obj_det_mapping.csv \
#                            --mapping_row obj365_boxable_name \
#                            --image_root_rel #$RVC_DATA_SRC_DIR/objects365/ \
#                            --reduce_boxable \
#                            --output #$RVC_DATA_TRG_DIR/obj365_boxable.rvc_val.json
#fi

#if [ ! -f "$RVC_DATA_TRG_DIR/obj365_boxable.rvc_train.json" ]; then
#    python3 $RVC_OBJ_DET_SCRIPT_DIR/../common/remap_coco.py --input $RVC_DATA_SRC_DIR/objects365/objects365v2_train_0422.json \
#                            --mapping $RVC_OBJ_DET_SCRIPT_DIR/obj_det_mapping.csv \
#                            --mapping_row obj365_boxable_name \
#                            --image_root_rel $RVC_DATA_SRC_DIR/objects365/ \
#                            --void_id 0 \
#                            --reduce_boxable \
#                            --output $RVC_DATA_TRG_DIR/obj365_boxable.rvc_train.json
#fi

# Remap OID
if [ ! -f "$RVC_DATA_TRG_DIR/oid_boxable.rvc_val.json" ]; then
    python3 $RVC_OBJ_DET_SCRIPT_DIR/../common/remap_coco.py --input $RVC_DATA_SRC_DIR/oid/annotations/openimages_challenge_2019_val_bbox.json \
                            --mapping $RVC_OBJ_DET_SCRIPT_DIR/obj_det_mapping.csv \
                            --mapping_row oid_boxable_leaf \
                            --image_root_rel $RVC_DATA_SRC_DIR/oid/validation/ \
                            --void_id 0 \
                            --reduce_boxable \
                            --output $RVC_DATA_TRG_DIR/oid_boxable.rvc_val.json
fi

if [ ! -f "$RVC_DATA_TRG_DIR/oid_boxable.rvc_train.json" ]; then
    python3 $RVC_OBJ_DET_SCRIPT_DIR/../common/remap_coco.py --input $RVC_DATA_SRC_DIR/oid/annotations/openimages_challenge_2019_train_bbox.json \
                            --mapping $RVC_OBJ_DET_SCRIPT_DIR/obj_det_mapping.csv \
                            --mapping_row oid_boxable_leaf \
                            --image_root_rel "$RVC_DATA_SRC_DIR/oid/train_{file_name[0]}/" \
                            --void_id 0 \
                            --reduce_boxable \
                            --output $RVC_DATA_TRG_DIR/oid_boxable.rvc_train.json
fi

if [ ! -f "$RVC_DATA_TRG_DIR/oid_boxable.rvc_test.json" ]; then
    python3 $RVC_OBJ_DET_SCRIPT_DIR/../common/create_test_image_info_coco.py --image_root_rel $RVC_DATA_SRC_DIR/oid/test \
                            --annotations_val $RVC_DATA_TRG_DIR/oid_boxable.rvc_val.json \
                            --output $RVC_DATA_TRG_DIR/oid_boxable.rvc_test.json
fi


# Remap MVD
if [ ! -f "$RVC_DATA_SRC_DIR/mvd/annotations/boxes_val_2018.json" ]; then
    python3 $RVC_OBJ_DET_SCRIPT_DIR/../common/convert_coco_panoptic_bbox.py --input $RVC_DATA_SRC_DIR/mvd/validation/panoptic/panoptic_2018.json \
                            --output $RVC_DATA_SRC_DIR/mvd/annotations/boxes_val_2018.json
fi

if [ ! -f "$RVC_DATA_TRG_DIR/mvd_boxable.rvc_val.json" ]; then
    python3 $RVC_OBJ_DET_SCRIPT_DIR/../common/remap_coco.py --input $RVC_DATA_SRC_DIR/mvd/annotations/boxes_val_2018.json \
                            --mapping $RVC_OBJ_DET_SCRIPT_DIR/obj_det_mapping.csv \
                            --mapping_row mvd_boxable_name \
                            --image_root_rel $RVC_DATA_SRC_DIR/mvd/validation/images \
                            --void_id 0 \
                            --reduce_boxable \
                            --output $RVC_DATA_TRG_DIR/mvd_boxable.rvc_val.json
fi

if [ ! -f "$RVC_DATA_SRC_DIR/mvd/annotations/boxes_train_2018.json" ]; then
    python3 $RVC_OBJ_DET_SCRIPT_DIR/../common/convert_coco_panoptic_bbox.py --input $RVC_DATA_SRC_DIR/mvd/training/panoptic/panoptic_2018.json \
                            --output $RVC_DATA_SRC_DIR/mvd/annotations/boxes_train_2018.json
fi

if [ ! -f "$RVC_DATA_TRG_DIR/mvd_boxable.rvc_train.json" ]; then
    python3 $RVC_OBJ_DET_SCRIPT_DIR/../common/remap_coco.py --input $RVC_DATA_SRC_DIR/mvd/annotations/boxes_train_2018.json \
                            --mapping $RVC_OBJ_DET_SCRIPT_DIR/obj_det_mapping.csv \
                            --mapping_row mvd_boxable_name \
                            --image_root_rel $RVC_DATA_SRC_DIR/mvd/training/images  \
                            --void_id 0 \
                            --reduce_boxable \
                            --output $RVC_DATA_TRG_DIR/mvd_boxable.rvc_train.json
fi

if [ ! -f "$RVC_DATA_TRG_DIR/mvd_boxable.rvc_test.json" ]; then
    python3 $RVC_OBJ_DET_SCRIPT_DIR/../common/create_test_image_info_coco.py --image_root_rel $RVC_DATA_SRC_DIR/mvd/testing/images \
                            --annotations_val $RVC_DATA_TRG_DIR/mvd_boxable.rvc_val.json \
                            --output $RVC_DATA_TRG_DIR/mvd_boxable.rvc_test.json
fi


# Create joined dataset
pushd $RVC_DATA_TRG_DIR
python3 $RVC_OBJ_DET_SCRIPT_DIR/../common/join_coco.py --join "coco_boxable.rvc_val.json;oid_boxable.rvc_val.json;mvd_boxable.rvc_val.json" \
       --output joined_val_boxable.json
python3 $RVC_OBJ_DET_SCRIPT_DIR/../common/join_coco.py --join "coco_boxable.rvc_train.json;oid_boxable.rvc_train.json;mvd_boxable.rvc_train.json" \
       --output joined_train_boxable.json
popd

RVC_DATA_TRG_DIR=
RVC_DATA_SRC_DIR=
RVC_OBJ_DET_SCRIPT_DIR=

echo "Finished remapping."

