#!/bin/bash
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
unzip ${RVC_EXTR_ROOT_DIR}/coco/image_info_test2017.zip -d ${RVC_EXTR_ROOT_DIR}/coco/
rm ${RVC_EXTR_ROOT_DIR}/coco/image_info_test2017.zip
#unzip ${RVC_EXTR_ROOT_DIR}/coco/panoptic_annotations_trainval2017.zip -d ${RVC_EXTR_ROOT_DIR}/coco/
#rm ${RVC_EXTR_ROOT_DIR}/coco/panoptic_annotations_trainval2017.zip

echo "Extracting OID"
pushd ${RVC_EXTR_ROOT_DIR}/oid
for onetarfile in *.tar.gz
do
  echo "Extracting tar file $onetarfile..."
  tar xf $onetarfile -C ${RVC_EXTR_ROOT_DIR}/oid && rm $onetarfile
done
popd

unzip ${RVC_EXTR_ROOT_DIR}/oid/open-images-object-detection-rvc-2020.zip -d ${RVC_EXTR_ROOT_DIR}/oid
rm ${RVC_EXTR_ROOT_DIR}/oid/open-images-object-detection-rvc-2020.zip
rm ${RVC_EXTR_ROOT_DIR}/oid/sample_submission.csv

#echo "Extracting Obj365"
#pushd ${RVC_EXTR_ROOT_DIR}/objects365
#for onetarfile in *.tar.gz
#do
#  echo "Extracting tar file $onetarfile..."
  # tar file comes with an objects365 root folder
#  tar xf $onetarfile -C ${RVC_EXTR_ROOT_DIR} && rm $onetarfile
#done
#popd

unzip ${RVC_EXTR_ROOT_DIR}/mvd/mapillary-vistas-dataset_public_v1.2.zip -d ${RVC_EXTR_ROOT_DIR}/mvd/
rm ${RVC_EXTR_ROOT_DIR}/mvd/mapillary-vistas-dataset_public_v1.2.zip

RVC_EXTR_ROOT_DIR=
RVC_CONFIRM_EXTR=

echo "Finished extractions."

