#!/bin/sh
# Downloads the open image dataset
# requires awscli, this can be installed using 
# pip install awscli
#
# (use gitbash for MS Windows)

RVC_OID_SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
# All data is downloaded to subfolders of RVC_DATA_DIR; if this is not defined: use the root dir + /datasets
if [ -z "${RVC_DATA_DIR}" ]; then
  RVC_EXTR_ROOT_DIR=${RVC_OID_SCRIPT_DIR}/../datasets
else
  RVC_EXTR_ROOT_DIR=${RVC_DATA_DIR}/
fi

echo "Extracting RVC files and removing archive files in the process. This can take 24h+ depending on your hdd/cpu configuration!"
read -p "This process will remove archives (zip/tar/tar.gz) once they are extracted. Proceed? [y/n] " -n 1 -r RVC_CONFIRM_EXTR
echo    # move to a new line
if [[ ! $RVC_CONFIRM_EXTR =~ ^[Yy]$ ]]; then
  RVC_EXTR_ROOT_DIR=
  RVC_CONFIRM_EXTR=
  exit 1
fi

#ADE20K is extracted by the mseg download script

unzip ${RVC_EXTR_ROOT_DIR}/cityscapes/gtFine_trainvaltest.zip -d ${RVC_EXTR_ROOT_DIR}/cityscapes
rm ${RVC_EXTR_ROOT_DIR}/cityscapes/gtFine_trainvaltest.zip
# Note: README and license are found in both files
rm ${RVC_EXTR_ROOT_DIR}/cityscapes/README
rm ${RVC_EXTR_ROOT_DIR}/cityscapes/license.txt
unzip ${RVC_EXTR_ROOT_DIR}/cityscapes/leftImg8bit_trainvaltest.zip -d ${RVC_EXTR_ROOT_DIR}/cityscapes
rm ${RVC_EXTR_ROOT_DIR}/cityscapes/leftImg8bit_trainvaltest.zip

#unzip ${RVC_EXTR_ROOT_DIR}/kitti/data_semantics.zip -d ${RVC_EXTR_ROOT_DIR}/kitti
#rm ${RVC_EXTR_ROOT_DIR}/kitti/data_semantics.zip
#unzip ${RVC_EXTR_ROOT_DIR}/kitti/data_panoptic.zip -d ${RVC_EXTR_ROOT_DIR}/kitti
#rm ${RVC_EXTR_ROOT_DIR}/kitti/data_panoptic.zip

unzip ${RVC_EXTR_ROOT_DIR}/scannet/scannet_frames_25k.zip -d ${RVC_EXTR_ROOT_DIR}/scannet
rm ${RVC_EXTR_ROOT_DIR}/scannet/scannet_frames_25k.zip
mkdir -p ${RVC_EXTR_ROOT_DIR}/scannet/bench
unzip ${RVC_EXTR_ROOT_DIR}/scannet/scannet_frames_test.zip -d ${RVC_EXTR_ROOT_DIR}/scannet/bench
rm ${RVC_EXTR_ROOT_DIR}/scannet/scannet_frames_test.zip

unzip ${RVC_EXTR_ROOT_DIR}/mvd/mapillary-vistas-dataset_public_v1.1.zip -d ${RVC_EXTR_ROOT_DIR}/mvd/
rm ${RVC_EXTR_ROOT_DIR}/mvd/mapillary-vistas-dataset_public_v1.1.zip

unzip ${RVC_EXTR_ROOT_DIR}/wilddash/wd_public_02.zip -d ${RVC_EXTR_ROOT_DIR}/wilddash/
rm ${RVC_EXTR_ROOT_DIR}/wilddash/wd_public_02.zip

RVC_EXTR_ROOT_DIR=
RVC_CONFIRM_EXTR=

echo "Finished extractions."

