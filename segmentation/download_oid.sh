#!/bin/sh
# Downloads the open image dataset
# requires awscli, this can be installed using 
# pip install awscli
#
# (use gitbash for MS Windows)

RVC_OID_SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
# All data is downloaded to subfolders of RVC_DATA_DIR; if this is not defined: use the root dir + /datasets
if [ -z "${RVC_OID_TRG_DIR}" ]; then
  RVC_OID_TRG_DIR=${RVC_OID_SCRIPT_DIR}/../datasets/oid
else
  RVC_OID_TRG_DIR=${RVC_DATA_DIR}/oid
fi

echo "Downloading Open Images Train And Validation to ${RVC_OID_TRG_DIR}"
echo "WARNING: the size of the full dataset is around 500GB, make sure you have enough space on the harddrive"

mkdir -p ${RVC_OID_TRG_DIR}
cd ${RVC_OID_TRG_DIR}

hexendings=0123456789abcdef
for (( i=0; i<${#hexendings}; i++ )); do
  #aws s3 --no-sign-request cp s3://open-images-dataset/tar/train_${hexendings:$i:1}.tar.gz ${RVC_OID_TRG_DIR}
  wget --no-check-certificate  https://storage.googleapis.com/openimages/challenge_2019/train-masks/challenge-2019-train-masks-${hexendings:$i:1}.zip -P ${RVC_OID_TRG_DIR}/challenge_2019_train_masks/
  wget --no-check-certificate https://storage.googleapis.com/openimages/challenge_2019/validation-masks/challenge-2019-validation-masks-${hexendings:$i:1}.zip -P ${RVC_OID_TRG_DIR}/challenge_2019_train_masks/
done


wget --no-check-certificate https://storage.googleapis.com/openimages/challenge_2019/challenge-2019-train-detection-human-imagelabels.csv -P ${RVC_OID_TRG_DIR}/annotations
wget --no-check-certificate https://storage.googleapis.com/openimages/challenge_2019/challenge-2019-validation-detection-human-imagelabels.csv -P ${RVC_OID_TRG_DIR}/annotations
wget --no-check-certificate https://storage.googleapis.com/openimages/2018_04/train/train-images-boxable-with-rotation.csv -P ${RVC_OID_TRG_DIR}/annotations
wget --no-check-certificate https://storage.googleapis.com/openimages/2018_04/validation/validation-images-with-rotation.csv -P ${RVC_OID_TRG_DIR}/annotations
wget --no-check-certificate https://storage.googleapis.com/openimages/challenge_2019/challenge-2019-classes-description-500.csv -P ${RVC_OID_TRG_DIR}/annotations
wget --no-check-certificate https://storage.googleapis.com/openimages/challenge_2019/challenge-2019-train-segmentation-masks.csv -P ${RVC_OID_TRG_DIR}/annotations
wget --no-check-certificate https://storage.googleapis.com/openimages/challenge_2019/challenge-2019-validation-segmentation-masks.csv -P ${RVC_OID_TRG_DIR}/annotations

RVC_OID_TRG_DIR=
RVC_OID_SCRIPT_DIR=

echo "Finished donwloading oid."

