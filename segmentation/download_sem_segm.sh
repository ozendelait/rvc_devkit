#!/bin/sh
# Downloads all semantic segmentation datasets for RVC
# requires awscli, this can be installed using 
# pip install awscli
# furthermore requires mseg-api ( https://github.com/mseg-dataset/mseg-api ) which needs amoung other things pytorch.
# (use gitbash for MS Windows)

RVC_SEM_SEG_SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
# All data is downloaded to subfolders of RVC_DATA_DIR; if this is not defined: use the root dir + /datasets
if [ -z "${RVC_DATA_DIR}" ]; then
  RVC_DOWNL_SEM_TRG_DIR=${RVC_SEM_SEG_SCRIPT_DIR}/../datasets/
else
  RVC_DOWNL_SEM_TRG_DIR=${RVC_DATA_DIR}/
fi

if [ ! -d "$RVC_SEM_SEG_SCRIPT_DIR/mseg_api" ]; then
  # getting defined version of mseg repo
  git -C $RVC_SEM_SEG_SCRIPT_DIR clone https://github.com/mseg-dataset/mseg-api.git $RVC_SEM_SEG_SCRIPT_DIR/mseg_api
  git -C $RVC_SEM_SEG_SCRIPT_DIR/mseg_api checkout 7e72a0f4cfb002786b10f2918ead916d0e2bc22d
  git -C $RVC_SEM_SEG_SCRIPT_DIR/mseg_api apply $RVC_SEM_SEG_SCRIPT_DIR/mseg_api.patch
  pip install -e $RVC_SEM_SEG_SCRIPT_DIR/mseg_api
fi

mseg_download_ade20k.sh ${RVC_DOWNL_SEM_TRG_DIR}/ade20k
${RVC_SEM_SEG_SCRIPT_DIR}/download_cityscapes_pano.sh ${RVC_DOWNL_SEM_TRG_DIR}/cityscapes
${RVC_SEM_SEG_SCRIPT_DIR}/download_kitti_pano.sh ${RVC_DOWNL_SEM_TRG_DIR}/kitti

pushd ${RVC_SEM_SEG_SCRIPT_DIR}/legacy/
python download_scannet.py -o ${RVC_DOWNL_SEM_TRG_DIR}/scannet --rob_task_data
python download_viper.py ${RVC_DOWNL_SEM_TRG_DIR}/viper
popd

${RVC_SEM_SEG_SCRIPT_DIR}/download_wilddash2.sh ${RVC_DOWNL_SEM_TRG_DIR}/wilddash
echo "Downloaded & extracted sem. segm. datasets to subfolders at ${RVC_DOWNL_SEM_TRG_DIR}"

