#!/bin/bash
# Extract and cleanup instance segmentation datasets
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

echo "Extracting COCO"
mkdir -p ${RVC_EXTR_ROOT_DIR}/coco/images
unzip ${RVC_EXTR_ROOT_DIR}/coco/train2017.zip -d ${RVC_EXTR_ROOT_DIR}/coco/images
rm ${RVC_EXTR_ROOT_DIR}/coco/train2017.zip
unzip ${RVC_EXTR_ROOT_DIR}/coco/val2017.zip -d ${RVC_EXTR_ROOT_DIR}/coco/images
rm ${RVC_EXTR_ROOT_DIR}/coco/val2017.zip
unzip ${RVC_EXTR_ROOT_DIR}/coco/test2017.zip -d ${RVC_EXTR_ROOT_DIR}/coco/images
rm ${RVC_EXTR_ROOT_DIR}/coco/test2017.zip

unzip ${RVC_EXTR_ROOT_DIR}/coco/annotations_trainval2017.zip -d ${RVC_EXTR_ROOT_DIR}/coco/
rm ${RVC_EXTR_ROOT_DIR}/coco/annotations_trainval2017.zip
unzip ${RVC_EXTR_ROOT_DIR}/coco/panoptic_annotations_trainval2017.zip -d ${RVC_EXTR_ROOT_DIR}/coco/
rm ${RVC_EXTR_ROOT_DIR}/coco/panoptic_annotations_trainval2017.zip
unzip ${RVC_EXTR_ROOT_DIR}/coco/annotations/panoptic_val2017.zip -d ${RVC_EXTR_ROOT_DIR}/coco/annotations/
rm ${RVC_EXTR_ROOT_DIR}/coco/annotations/panoptic_val2017.zip
unzip ${RVC_EXTR_ROOT_DIR}/coco/annotations/panoptic_train2017.zip -d ${RVC_EXTR_ROOT_DIR}/coco/annotations/
rm ${RVC_EXTR_ROOT_DIR}/coco/annotations/panoptic_train2017.zip

echo "Extracting OID"
pushd ${RVC_EXTR_ROOT_DIR}/oid
for onetarfile in *.tar
do
  echo "Extracting tar file $onetarfile..."
  tar xf $onetarfile -C ${RVC_EXTR_ROOT_DIR}/oid && rm $onetarfile
done
popd

unzip ${RVC_EXTR_ROOT_DIR}/cityscapes/gtFine_trainvaltest.zip -d ${RVC_EXTR_ROOT_DIR}/cityscapes
rm ${RVC_EXTR_ROOT_DIR}/cityscapes/gtFine_trainvaltest.zip
# Note: README and license are found in both files
rm ${RVC_EXTR_ROOT_DIR}/cityscapes/README
rm ${RVC_EXTR_ROOT_DIR}/cityscapes/license.txt
unzip ${RVC_EXTR_ROOT_DIR}/cityscapes/leftImg8bit_trainvaltest.zip -d ${RVC_EXTR_ROOT_DIR}/cityscapes
rm ${RVC_EXTR_ROOT_DIR}/cityscapes/leftImg8bit_trainvaltest.zip
$RVC_OID_SCRIPT_DIR/convert_cityscapes_coco.sh ${RVC_EXTR_ROOT_DIR}/cityscapes

unzip ${RVC_EXTR_ROOT_DIR}/kitti/data_semantics.zip -d ${RVC_EXTR_ROOT_DIR}/kitti
rm ${RVC_EXTR_ROOT_DIR}/kitti/data_semantics.zip
unzip ${RVC_EXTR_ROOT_DIR}/kitti/data_panoptic.zip -d ${RVC_EXTR_ROOT_DIR}/kitti
rm ${RVC_EXTR_ROOT_DIR}/kitti/data_panoptic.zip

unzip ${RVC_EXTR_ROOT_DIR}/scannet/scannet_frames_25k.zip -d ${RVC_EXTR_ROOT_DIR}/scannet
rm ${RVC_EXTR_ROOT_DIR}/scannet/scannet_frames_25k.zip
mkdir -p ${RVC_EXTR_ROOT_DIR}/scannet/bench
unzip ${RVC_EXTR_ROOT_DIR}/scannet/scannet_frames_test.zip -d ${RVC_EXTR_ROOT_DIR}/scannet/bench
rm ${RVC_EXTR_ROOT_DIR}/scannet/scannet_frames_test.zip
$RVC_OID_SCRIPT_DIR/convert_scannet_coco.sh ${RVC_EXTR_ROOT_DIR}/scannet

unzip ${RVC_EXTR_ROOT_DIR}/mvd/mapillary-vistas-dataset_public_v1.1.zip -d ${RVC_EXTR_ROOT_DIR}/mvd/
rm ${RVC_EXTR_ROOT_DIR}/mvd/mapillary-vistas-dataset_public_v1.1.zip
$RVC_OID_SCRIPT_DIR/convert_mvd_coco.sh ${RVC_EXTR_ROOT_DIR}/mvd
#viper is extracted by the downloader itself
$RVC_OID_SCRIPT_DIR/convert_viper_coco.sh ${RVC_EXTR_ROOT_DIR}/viper

unzip ${RVC_EXTR_ROOT_DIR}/wilddash/wd_public_02.zip -d ${RVC_EXTR_ROOT_DIR}/wilddash/
rm ${RVC_EXTR_ROOT_DIR}/wilddash/wd_public_02.zip

RVC_EXTR_ROOT_DIR=
RVC_CONFIRM_EXTR=

echo "Finished extractions."

