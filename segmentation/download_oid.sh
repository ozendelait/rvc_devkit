#!/bin/sh
# Downloads the open image dataset
# requires awscli, this can be installed using 
# pip install awscli
#
# (use gitbash for MS Windows)

RVC_OID_SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
# All data is downloaded to subfolders of RVC_DATA_DIR; if this is not defined: use the root dir + /datasets
if [ -z "${RVC_DATA_DIR}" ]; then
  RVC_OID_DIR=${RVC_OID_SCRIPT_DIR}/../datasets/oid
else
  RVC_OID_DIR=${RVC_DATA_DIR}/oid
fi

echo "Downloading Open Images Train And Validation to ${RVC_OID_DIR}"
echo "WARNING: the size of the full dataset is around 500GB, make sure you have enough space on the harddrive"

mkdir -p ${RVC_OID_DIR}
cd ${RVC_OID_DIR}


aws s3 --no-sign-request cp s3://open-images-dataset/tar/train_0.tar.gz ${RVC_OID_DIR}
aws s3 --no-sign-request cp s3://open-images-dataset/tar/train_1.tar.gz ${RVC_OID_DIR}
aws s3 --no-sign-request cp s3://open-images-dataset/tar/train_2.tar.gz ${RVC_OID_DIR}
aws s3 --no-sign-request cp s3://open-images-dataset/tar/train_3.tar.gz ${RVC_OID_DIR}
aws s3 --no-sign-request cp s3://open-images-dataset/tar/train_4.tar.gz ${RVC_OID_DIR}
aws s3 --no-sign-request cp s3://open-images-dataset/tar/train_5.tar.gz ${RVC_OID_DIR}
aws s3 --no-sign-request cp s3://open-images-dataset/tar/train_6.tar.gz ${RVC_OID_DIR}
aws s3 --no-sign-request cp s3://open-images-dataset/tar/train_7.tar.gz ${RVC_OID_DIR}
aws s3 --no-sign-request cp s3://open-images-dataset/tar/train_8.tar.gz ${RVC_OID_DIR}
aws s3 --no-sign-request cp s3://open-images-dataset/tar/train_9.tar.gz ${RVC_OID_DIR}
aws s3 --no-sign-request cp s3://open-images-dataset/tar/train_a.tar.gz ${RVC_OID_DIR}
aws s3 --no-sign-request cp s3://open-images-dataset/tar/train_b.tar.gz ${RVC_OID_DIR}
aws s3 --no-sign-request cp s3://open-images-dataset/tar/train_c.tar.gz ${RVC_OID_DIR}
aws s3 --no-sign-request cp s3://open-images-dataset/tar/train_d.tar.gz ${RVC_OID_DIR}
aws s3 --no-sign-request cp s3://open-images-dataset/tar/train_e.tar.gz ${RVC_OID_DIR}
aws s3 --no-sign-request cp s3://open-images-dataset/tar/train_f.tar.gz ${RVC_OID_DIR}
aws s3 --no-sign-request cp s3://open-images-dataset/tar/validation.tar.gz ${RVC_OID_DIR}

RVC_OID_DIR=
RVC_OID_SCRIPT_DIR=

echo "Finished donwloading oid."

