#!/bin/sh
# Downloads the open image dataset
# requires awscli, this can be installed using 
# pip install awscli
#
# (use gitbash for MS Windows)

RVC_OID_SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
# All data is downloaded to subfolders of RVC_DATA_DIR; if this is not defined: use the root dir + /datasets
if [ -z "${RVC_DATA_DIR}" ]; then
  RVC_OID_TRG_DIR=${RVC_OID_SCRIPT_DIR}/../datasets/oid
else
  RVC_OID_TRG_DIR=${RVC_DATA_DIR}/oid
fi

echo "Downloading Open Images Dataset to ${RVC_OID_TRG_DIR}"


mkdir -p ${RVC_OID_TRG_DIR}

aws s3 --no-sign-request cp s3://open-images-dataset/tar/train_0.tar.gz ${RVC_OID_TRG_DIR}
aws s3 --no-sign-request cp s3://open-images-dataset/tar/train_1.tar.gz ${RVC_OID_TRG_DIR}
aws s3 --no-sign-request cp s3://open-images-dataset/tar/train_2.tar.gz ${RVC_OID_TRG_DIR}
aws s3 --no-sign-request cp s3://open-images-dataset/tar/train_3.tar.gz ${RVC_OID_TRG_DIR}
aws s3 --no-sign-request cp s3://open-images-dataset/tar/train_4.tar.gz ${RVC_OID_TRG_DIR}
aws s3 --no-sign-request cp s3://open-images-dataset/tar/train_5.tar.gz ${RVC_OID_TRG_DIR}
aws s3 --no-sign-request cp s3://open-images-dataset/tar/train_6.tar.gz ${RVC_OID_TRG_DIR}
aws s3 --no-sign-request cp s3://open-images-dataset/tar/train_7.tar.gz ${RVC_OID_TRG_DIR}
aws s3 --no-sign-request cp s3://open-images-dataset/tar/train_8.tar.gz ${RVC_OID_TRG_DIR}
aws s3 --no-sign-request cp s3://open-images-dataset/tar/train_9.tar.gz ${RVC_OID_TRG_DIR}
aws s3 --no-sign-request cp s3://open-images-dataset/tar/train_a.tar.gz ${RVC_OID_TRG_DIR}
aws s3 --no-sign-request cp s3://open-images-dataset/tar/train_b.tar.gz ${RVC_OID_TRG_DIR}
aws s3 --no-sign-request cp s3://open-images-dataset/tar/train_c.tar.gz ${RVC_OID_TRG_DIR}
aws s3 --no-sign-request cp s3://open-images-dataset/tar/train_d.tar.gz ${RVC_OID_TRG_DIR}
aws s3 --no-sign-request cp s3://open-images-dataset/tar/train_e.tar.gz ${RVC_OID_TRG_DIR}
aws s3 --no-sign-request cp s3://open-images-dataset/tar/train_f.tar.gz ${RVC_OID_TRG_DIR}
aws s3 --no-sign-request cp s3://open-images-dataset/tar/validation.tar.gz ${RVC_OID_TRG_DIR}

kaggle competitions download -c open-images-object-detection-rvc-2020 -p ${RVC_OID_TRG_DIR}

wget --no-check-certificate https://storage.googleapis.com/openimages/challenge_2019/challenge-2019-train-detection-bbox.csv -P ${RVC_OID_TRG_DIR}/annotations
wget --no-check-certificate https://storage.googleapis.com/openimages/challenge_2019/challenge-2019-validation-detection-bbox.csv -P ${RVC_OID_TRG_DIR}/annotations
wget --no-check-certificate https://storage.googleapis.com/openimages/challenge_2019/challenge-2019-train-detection-human-imagelabels.csv -P ${RVC_OID_TRG_DIR}/annotations
wget --no-check-certificate https://storage.googleapis.com/openimages/challenge_2019/challenge-2019-validation-detection-human-imagelabels.csv -P ${RVC_OID_TRG_DIR}/annotations
wget --no-check-certificate https://storage.googleapis.com/openimages/2018_04/train/train-images-boxable-with-rotation.csv -P ${RVC_OID_TRG_DIR}/annotations
wget --no-check-certificate https://storage.googleapis.com/openimages/2018_04/validation/validation-images-with-rotation.csv -P ${RVC_OID_TRG_DIR}/annotations
wget --no-check-certificate https://storage.googleapis.com/openimages/challenge_2019/challenge-2019-classes-description-500.csv -P ${RVC_OID_TRG_DIR}/annotations

RVC_OID_TRG_DIR=
RVC_OID_SCRIPT_DIR=

echo "Finished downloading oid."

