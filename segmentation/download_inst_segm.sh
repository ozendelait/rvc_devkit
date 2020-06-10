#!/bin/sh
# Downloads all semantic segmentation datasets for RVC
# requires awscli, this can be installed using 
# pip install awscli
#
# (use gitbash for MS Windows)

RVC_DOWNL_SEM_SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
# All data is downloaded to subfolders of RVC_DATA_DIR; if this is not defined: use the root dir + /datasets
if [ -z "${RVC_DATA_DIR}" ]; then
  RVC_DOWNL_SEM_TRG_DIR=${RVC_OID_SCRIPT_DIR}/../datasets/
else
  RVC_DOWNL_SEM_TRG_DIR=${RVC_DATA_DIR}/
fi

$RVC_DOWNL_SEM_SCRIPT_DIR/../objdet/download_coco_boxable.sh
${RVC_DOWNL_SEM_SCRIPT_DIR}/download_cityscapes_pano.sh ${RVC_DOWNL_SEM_TRG_DIR}/cityscapes
$RVC_DOWNL_SEM_SCRIPT_DIR/download_kitti_pano.sh ${RVC_DOWNL_SEM_TRG_DIR}/kitti

pushd ${RVC_DOWNL_SEM_SCRIPT_DIR}/legacy/
python download_scannet.py -o ${RVC_DOWNL_SEM_TRG_DIR}/scannet --rob_task_data
python download_viper.py ${RVC_DOWNL_SEM_TRG_DIR}/viper
popd

${RVC_DOWNL_SEM_SCRIPT_DIR}/../objdet/download_oid_boxable.sh
${RVC_DOWNL_SEM_SCRIPT_DIR}/download_wilddash2.sh ${RVC_DOWNL_SEM_SCRIPT_DIR}/wilddash
echo "Downloaded instance segm. datasets to subfolders at ${RVC_DOWNL_SEM_TRG_DIR}"

