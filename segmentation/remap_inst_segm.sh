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


#convert oid gt
$RVC_OBJ_DET_SCRIPT_DIR/../objdet/convert_oid_coco.sh

python $RVC_OBJ_DET_SCRIPT_DIR/../common/remap_coco.py --input $RVC_DATA_SRC_DIR/coco/annotations/panoptic_val2017.json \
                        --mapping $RVC_OBJ_DET_SCRIPT_DIR/inst_mapping.csv \
                        --mapping_row coco_inst_name \
                        --image_root_rel $RVC_DATA_SRC_DIR/coco/images \
                        --annotation_root_rel $RVC_DATA_SRC_DIR/coco/annotations/panoptic_val2017/ \
                        --void_id 0 \
                        --output $RVC_DATA_TRG_DIR/coco_inst.rvc_val.json

python $RVC_OBJ_DET_SCRIPT_DIR/../common/remap_coco.py --input $RVC_DATA_SRC_DIR/coco/annotations/panoptic_train2017.json \
                        --mapping $RVC_OBJ_DET_SCRIPT_DIR/inst_mapping.csv \
                        --mapping_row coco_inst_name \
                        --image_root_rel $RVC_DATA_SRC_DIR/coco/images \
                        --annotation_root_rel $RVC_DATA_SRC_DIR/coco/annotations/panoptic_train2017/ \
                        --void_id 0 \
                        --output $RVC_DATA_TRG_DIR/coco_inst.rvc_train.json
                        
python $RVC_OBJ_DET_SCRIPT_DIR/../common/remap_coco.py --input $RVC_DATA_SRC_DIR/kitti/data_panoptic/training.json \
                        --mapping $RVC_OBJ_DET_SCRIPT_DIR/inst_mapping.csv \
                        --mapping_row kitti_inst_name \
                        --image_root_rel $RVC_DATA_SRC_DIR/kitti/training/image_2 \
                        --annotation_root_rel $RVC_DATA_SRC_DIR/kitti/data_panoptic/training/ \
                        --void_id 0 \
                        --output $RVC_DATA_TRG_DIR/kitti_inst.rvc_train.json
                        
python $RVC_OBJ_DET_SCRIPT_DIR/../common/remap_coco.py --input $RVC_DATA_SRC_DIR/oid/annotations/openimages_challenge_2019_val_panoptic.json \
                        --mapping $RVC_OBJ_DET_SCRIPT_DIR/inst_mapping.csv \
                        --mapping_row oid_inst_leaf \
                        --image_root_rel $RVC_DATA_SRC_DIR/oid/val/ \
                        --annotation_root_rel $RVC_DATA_SRC_DIR/coco/annotations/panoptic_val_challenge_2019/ \
                        --void_id 0 \
                        --output $RVC_DATA_TRG_DIR/oid_inst.rvc_val.json

python $RVC_OBJ_DET_SCRIPT_DIR/../common/remap_coco.py --input $RVC_DATA_SRC_DIR/oid/annotations/openimages_challenge_2019_train_panoptic.json \
                        --mapping $RVC_OBJ_DET_SCRIPT_DIR/inst_mapping.csv \
                        --mapping_row oid_inst_leaf \
                        --image_root_rel "$RVC_DATA_SRC_DIR/oid/train_{file_name[0]}/" \
                        --annotation_root_rel $RVC_DATA_SRC_DIR/coco/annotations/panoptic_train_challenge_2019/train_{file_name[0]}/ \
                        --void_id 0 \
                        --output $RVC_DATA_TRG_DIR/oid_inst.rvc_train.json

python $RVC_OBJ_DET_SCRIPT_DIR/../common/remap_coco.py --input $RVC_DATA_SRC_DIR/mvd/validation/panoptic/panoptic_2018.json \
                        --mapping $RVC_OBJ_DET_SCRIPT_DIR/inst_mapping.csv \
                        --mapping_row mvd_inst_name \
                        --image_root_rel $RVC_DATA_SRC_DIR/mvd/validation/images \
                        --annotation_root_rel $RVC_DATA_SRC_DIR/mvd/validation/panoptic \
                        --void_id 0 \
                        --output $RVC_DATA_TRG_DIR/mvd_inst.rvc_val.json

python $RVC_OBJ_DET_SCRIPT_DIR/../common/remap_coco.py --input $RVC_DATA_SRC_DIR/mvd/training/panoptic/panoptic_2018.json  \
                        --mapping $RVC_OBJ_DET_SCRIPT_DIR/inst_mapping.csv \
                        --mapping_row mvd_inst_name \
                        --image_root_rel $RVC_DATA_SRC_DIR/mvd/training/images  \
                        --annotation_root_rel $RVC_DATA_SRC_DIR/mvd/training/panoptic \
                        --void_id 0 \
                        --output $RVC_DATA_TRG_DIR/mvd_inst.rvc_train.json

python $RVC_OBJ_DET_SCRIPT_DIR/../common/remap_coco.py --input $RVC_DATA_SRC_DIR/viper/train/pano.json \
                        --mapping $RVC_OBJ_DET_SCRIPT_DIR/inst_mapping.csv \
                        --mapping_row viper_inst_name \
                        --image_root_rel $RVC_DATA_SRC_DIR/viper/train/img/{file_name[0]}{file_name[1]}{file_name[2]} \
                        --annotation_root_rel $RVC_DATA_SRC_DIR/viper/train/pano/{file_name[0]}{file_name[1]}{file_name[2]} \
                        --void_id 0 \
                        --output $RVC_DATA_TRG_DIR/viper_inst.rvc_train.json
                        
python $RVC_OBJ_DET_SCRIPT_DIR/../common/remap_coco.py --input $RVC_DATA_SRC_DIR/viper/val/pano.json \
                        --mapping $RVC_OBJ_DET_SCRIPT_DIR/inst_mapping.csv \
                        --mapping_row viper_inst_name \
                        --image_root_rel $RVC_DATA_SRC_DIR/viper/val/img/{file_name[0]}{file_name[1]}{file_name[2]} \
                        --annotation_root_rel $RVC_DATA_SRC_DIR/viper/val/pano/{file_name[0]}{file_name[1]}{file_name[2]} \
                        --void_id 0 \
                        --output $RVC_DATA_TRG_DIR/viper_inst.rvc_val.json

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
                        
#Creates random split for train/val (currently no specific split supplied)
python $RVC_OBJ_DET_SCRIPT_DIR/../common/rvc_split_coco.py --input $RVC_DATA_SRC_DIR/scannet/scannet_panoptic.json --split "80;20" --output $RVC_DATA_SRC_DIR/scannet/instances.json

python $RVC_OBJ_DET_SCRIPT_DIR/../common/remap_coco.py --input $RVC_DATA_SRC_DIR/scannet/instances_0.json \
                        --mapping $RVC_OBJ_DET_SCRIPT_DIR/inst_mapping.csv \
                        --mapping_row wilddash_inst_name \
                        --image_root_rel $RVC_DATA_SRC_DIR/scannet/scannet_frames_25k \
                        --annotation_root_rel $RVC_DATA_SRC_DIR/scannet/scannet_panoptic \
                        --void_id 0 \
                        --output $RVC_DATA_TRG_DIR/scannet_inst.rvc_train.json

python $RVC_OBJ_DET_SCRIPT_DIR/../common/remap_coco.py --input $RVC_DATA_SRC_DIR/scannet/instances_1.json \
                        --mapping $RVC_OBJ_DET_SCRIPT_DIR/inst_mapping.csv \
                        --mapping_row wilddash_inst_name \
                        --image_root_rel $RVC_DATA_SRC_DIR/scannet/scannet_frames_25k \
                        --annotation_root_rel $RVC_DATA_SRC_DIR/scannet/scannet_panoptic \
                        --void_id 0 \
                        --output $RVC_DATA_TRG_DIR/scannet_inst.rvc_val.json

                        
pushd $RVC_DATA_TRG_DIR
python $RVC_OBJ_DET_SCRIPT_DIR/../common/join_coco.py --join "coco_inst.rvc_val.json;wd2_inst.rvc_val.json;cs_inst.rvc_val.json;viper_inst.rvc_val.json;mvd_inst.rvc_val.json;oid_inst.rvc_val.json;scannet_inst.rvc_val.json" \
       --output joined_val_inst.json
python $RVC_OBJ_DET_SCRIPT_DIR/../common/join_coco.py --join "coco_inst.rvc_train.json;wd2_inst.rvc_train.json;kitti_inst.rvc_train.json;cs_inst.rvc_train.json;viper_inst.rvc_train.json;mvd_inst.rvc_train.json;oid_inst.rvc_train.json;scannet_inst.rvc_train.json" \
       --output joined_train_inst.json
popd

RVC_DATA_TRG_DIR=
RVC_DATA_SRC_DIR=
RVC_OBJ_DET_SCRIPT_DIR=

echo "Finished remapping."

