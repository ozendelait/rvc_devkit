#!/bin/bash
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

if ! command -v awscli &> /dev/null
then
    echo "awscli could not be found! It can be installed via pip install awscli"
    exit
fi



echo "Downloading Open Images Train And Validation to ${RVC_OID_TRG_DIR}"
echo "WARNING: the size of the full dataset is around 550GB, make sure you have enough space on the harddrive"

mkdir -p ${RVC_OID_TRG_DIR}
cd ${RVC_OID_TRG_DIR}

rvc_hexendings=0123456789abcdef
for (( i=0; i<${#rvc_hexendings}; i++ )); do
  #get rgb images
  aws s3 --no-sign-request cp s3://open-images-dataset/tar/train_${rvc_hexendings:$i:1}.tar.gz ${RVC_OID_TRG_DIR}
  echo "Extracting train_${rvc_hexendings:$i:1}.tar.gz, this may take a while..."
  tar -C ${RVC_OID_TRG_DIR} -xcvf train_${rvc_hexendings:$i:1}.tar.gz
  rm train_${rvc_hexendings:$i:1}.tar.gz
  #get training instance masks (downloads, extracts & removes old archive)
  rvc_target_zip_dir=${RVC_OID_TRG_DIR}/annotations/challenge_2019_train_masks/train_${rvc_hexendings:$i:1}
  rvc_target_zip_file=${rvc_target_zip_dir}/challenge-2019-train-masks-${rvc_hexendings:$i:1}.zip
  wget -N --no-check-certificate  https://storage.googleapis.com/openimages/challenge_2019/train-masks/challenge-2019-train-masks-${rvc_hexendings:$i:1}.zip -P ${rvc_target_zip_dir}
  echo "Extracting ${rvc_target_zip_file}, this may take a while..."
  unzip -q ${rvc_target_zip_file} -d ${rvc_target_zip_dir}
  rm ${rvc_target_zip_file}
  #get validation instance masks (downloads, extracts & removes old archive)
  rvc_target_zip_dir=${RVC_OID_TRG_DIR}/annotations/challenge_2019_validation_masks/
  rvc_target_zip_file=${rvc_target_zip_dir}/challenge-2019-validation-masks-${rvc_hexendings:$i:1}.zip
  wget -N --no-check-certificate  https://storage.googleapis.com/openimages/challenge_2019/validation-masks/challenge-2019-validation-masks-${rvc_hexendings:$i:1}.zip -P ${rvc_target_zip_dir}
  echo "Extracting ${rvc_target_zip_file}, this may take a while..."
  unzip -q ${rvc_target_zip_file} -d ${rvc_target_zip_dir}
  rm ${rvc_target_zip_file}
done

rvc_target_zip_file=
rvc_target_zip_dir=
rvc_hexendings=

wget -N --no-check-certificate https://storage.googleapis.com/openimages/challenge_2019/challenge-2019-train-detection-human-imagelabels.csv -P ${RVC_OID_TRG_DIR}/annotations
wget -N --no-check-certificate https://storage.googleapis.com/openimages/challenge_2019/challenge-2019-validation-detection-human-imagelabels.csv -P ${RVC_OID_TRG_DIR}/annotations
wget -N --no-check-certificate https://storage.googleapis.com/openimages/2018_04/train/train-images-boxable-with-rotation.csv -P ${RVC_OID_TRG_DIR}/annotations
wget -N --no-check-certificate https://storage.googleapis.com/openimages/2018_04/validation/validation-images-with-rotation.csv -P ${RVC_OID_TRG_DIR}/annotations
wget -N --no-check-certificate https://storage.googleapis.com/openimages/challenge_2019/challenge-2019-classes-description-500.csv -P ${RVC_OID_TRG_DIR}/annotations
wget -N --no-check-certificate https://storage.googleapis.com/openimages/challenge_2019/challenge-2019-train-segmentation-masks.csv -P ${RVC_OID_TRG_DIR}/annotations
wget -N --no-check-certificate https://storage.googleapis.com/openimages/challenge_2019/challenge-2019-validation-segmentation-masks.csv -P ${RVC_OID_TRG_DIR}/annotations

RVC_OID_TRG_DIR=
RVC_OID_SCRIPT_DIR=

echo "Finished downloading oid."