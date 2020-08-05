#!/bin/bash
# Remaps predictions on the RVC joint mapping back to the original categories
# requires python

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


# Default values of arguments
PREDICTIONS="None"
DATASET="None"

# Loop through arguments and process them
for arg in "$@"
do
    case $arg in
        -p|--predictions)
        PREDICTIONS="$2"
        shift # Remove argument name from processing
        shift # Remove argument value from processing
        ;;
        -d|--dataset)
        DATASET="$2"
        shift # Remove argument name from processing
        shift # Remove argument value from processing
        ;;
        #-s|--split)
        #SPLIT="$2"
        #shift # Remove argument name from processing
        #shift # Remove argument value from processing
        #;;
    esac
done

# Rename output file
PREDICTIONS_REMAPPED=${PREDICTIONS:0: -5}_remapped_results.json

# Use appropriate mapping for each dataset.
# Because the predictions don't contain any category info the original val annotations are used
if [ $DATASET = "mvd" ]; then
    python3 $RVC_OBJ_DET_SCRIPT_DIR/../common/map_coco_back.py --predictions $PREDICTIONS \
                            --annotations $RVC_DATA_TRG_DIR/mvd/annotations/boxes_val_2018.json \
                            --mapping $RVC_OBJ_DET_SCRIPT_DIR/obj_det_mapping.csv \
                            --mapping_row mvd_boxable_name \
                            --map_to id \
                            --void_id 0 \
                            --remove_void \
                            --reduce_boxable \
                            --output $PREDICTIONS_REMAPPED

elif [ $DATASET = "coco" ]; then
    python3 $RVC_OBJ_DET_SCRIPT_DIR/../common/map_coco_back.py --predictions $PREDICTIONS \
                            --annotations $RVC_DATA_TRG_DIR/coco/annotations/instances_val2017.json \
                            --mapping $RVC_OBJ_DET_SCRIPT_DIR/obj_det_mapping.csv \
                            --mapping_row coco_boxable_name \
                            --map_to id \
                            --void_id 0 \
                            --remove_void \
                            --reduce_boxable \
                            --output $PREDICTIONS_REMAPPED
                            
elif [ $DATASET = "oid" ]; then
    python3 $RVC_OBJ_DET_SCRIPT_DIR/../common/map_coco_back.py --predictions $PREDICTIONS \
                            --annotations $RVC_DATA_TRG_DIR/oid/annotations/openimages_challenge_2019_val_bbox.json \
                            --mapping $RVC_OBJ_DET_SCRIPT_DIR/obj_det_mapping.csv \
                            --mapping_row oid_boxable_leaf \
                            --map_to freebase_id \
                            --void_id 0 \
                            --remove_void \
                            --reduce_boxable \
                            --output $PREDICTIONS_REMAPPED
                            
    echo "Converting predictions to OID format..."
    if [ ! -d $RVC_OBJ_DET_SCRIPT_DIR/openimages2coco ]; then
    # getting defined version of openimages2coco repo
        git -C $RVC_OBJ_DET_SCRIPT_DIR clone https://github.com/bethgelab/openimages2coco.git 
        git -C $RVC_OBJ_DET_SCRIPT_DIR/openimages2coco checkout 8991d9bccbd3d91f32b87f04dab60b2a61cb608e
    fi
    
    
    #remapping COCO format to OID .csv
    pushd $RVC_OBJ_DET_SCRIPT_DIR/openimages2coco/
    python3 convert_predictions.py --p $PREDICTIONS_REMAPPED --subset test-rvc2020
    popd

fi

