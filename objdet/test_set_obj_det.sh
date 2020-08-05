#!/bin/sh
# Downloads & extracts OID & COCO test sets (i.e. only benchmark input images)
# Automatically tests correctness of the mvd test set (must be downloaded manually)
# OID download needs support for the kaggle api which can be installed via:
# pip install kaggle
# and you need to supply your kaggle api credentials as described here:
# https://github.com/Kaggle/kaggle-api#api-credentials
# you can also manually unzip the test.zip from 
# https://www.kaggle.com/c/open-images-object-detection-rvc-2020/data?select=test 
# into RVC_DATA_DIR/oid/test_rvc


RVC_OBJ_DET_SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
# All data is downloaded to subfolders of RVC_DATA_DIR; if this is not defined: use the root dir + /datasets
if [ -z "${RVC_DATA_DIR}" ] ; then
  RVC_USE_DATA_ROOT_DIR=${RVC_OBJ_DET_SCRIPT_DIR}/../datasets/
else
  RVC_USE_DATA_ROOT_DIR=${RVC_DATA_DIR}/
fi

#check MVD test set size (needs to be manually installed!)
count_files_mvd=$(find ${RVC_USE_DATA_ROOT_DIR}/mvd/testing/images/. -maxdepth 1 -type f -printf "\n" 2>/dev/null | wc -l)
if [ ${count_files_mvd} -ne 5000 ] ; then
  echo "Missing MVD files (only ${count_files_mvd})! You need to request"
  echo "MVD via https://www.mapillary.com/dataset/vistas "
  echo "and unpack the file manually to ${RVC_USE_DATA_ROOT_DIR}/mvd/"
else
  #check file size to determine differnce between v1.1 and v1.2 (anonymized images)
  file_size_check_mvd=$(stat --printf="%s" "${RVC_USE_DATA_ROOT_DIR}/mvd/testing/images/0F9m3hsCahtlL0AzLph9LQ.jpg")
  if [ ${file_size_check_mvd} -ne 630864 ] ; then
    echo "Warning! You are using v1.1 of MVD; testing is done using v1.2!"
    echo "Request it via https://www.mapillary.com/dataset/vistas"
    echo "and unpack the file manually to ${RVC_USE_DATA_ROOT_DIR}/mvd/"
  fi
  file_size_check_mvd=
fi

#check COCO test set
if [ ! -d "${RVC_USE_DATA_ROOT_DIR}/coco/images/test2017" ]; then
  RVC_COCO_IMG_DIR=${RVC_USE_DATA_ROOT_DIR}/coco/images/
  mkdir -p ${RVC_COCO_IMG_DIR}
  TEST_IMGS_URL="http://images.cocodataset.org/zips/test2017.zip"
  wget --no-check-certificate --continue $TEST_IMGS_URL  -P ${RVC_COCO_IMG_DIR}
  unzip ${RVC_COCO_IMG_DIR}/test2017.zip -d ${RVC_COCO_IMG_DIR}
  rm ${RVC_COCO_IMG_DIR}/test2017.zip
fi

count_files_coco=$(find ${RVC_USE_DATA_ROOT_DIR}/coco/images/test2017/. -maxdepth 1 -type f -printf "\n" 2>/dev/null | wc -l)
if [ ${count_files_coco} -ne 40670 ] ; then
  echo "Missing COCO files (only ${count_files_coco})! Check your COCO test set installation"
fi

#check OID test set
if [ ! -d "${RVC_USE_DATA_ROOT_DIR}/oid/test_rvc" ]; then
  mkdir -p "${RVC_USE_DATA_ROOT_DIR}/oid/test_rvc"
  pushd "${RVC_USE_DATA_ROOT_DIR}/oid/test_rvc"
    kaggle competitions download -c open-images-object-detection-rvc-2020
    unzip open-images-object-detection-rvc-2020.zip
    rm open-images-object-detection-rvc-2020.zip
  popd
fi

count_files_oid=$(find ${RVC_USE_DATA_ROOT_DIR}/oid/test_rvc/test/. -maxdepth 1 -type f -printf "\n" 2>/dev/null | wc -l)
if [ ${count_files_oid} -ne 99999 ] ; then
  echo "Missing OID files (only ${count_files_oid})! Check your OID test set installation"
fi


RVC_OBJ_DET_SCRIPT_DIR=
RVC_USE_DATA_ROOT_DIR=
count_files_mvd=
count_files_coco=
count_files_oid=