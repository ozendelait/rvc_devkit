#!/bin/sh
# Downloads & extracts all Panoptic Segm. test sets (i.e. only benchmark input images)
# Except MVD, this must be manually downloaded. 
# However, the script does check the validity of the mvd test set



RVC_SEGM_SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
# All data is downloaded to subfolders of RVC_DATA_DIR; if this is not defined: use the root dir + /datasets
if [ -z "${RVC_DATA_DIR}" ] ; then
  RVC_USE_DATA_ROOT_DIR=${RVC_SEGM_SCRIPT_DIR}/../datasets/
else
  RVC_USE_DATA_ROOT_DIR=${RVC_DATA_DIR}/
fi

ALL_TESTSETS_CORRECT=1

#check MVD test set size (needs to be manually installed!)
count_files_mvd=$(find ${RVC_USE_DATA_ROOT_DIR}/mvd/testing/images/. -maxdepth 1 -type f -printf "\n" 2>/dev/null | wc -l)
if [ ${count_files_mvd} -ne 5000 ] ; then
  echo "Missing MVD files (only ${count_files_mvd})! You need to request"
  echo "MVD via https://www.mapillary.com/dataset/vistas "
  echo "and unpack the file manually to ${RVC_USE_DATA_ROOT_DIR}/mvd/"
  ALL_TESTSETS_CORRECT=0
else
  #check file size to determine differnce between v1.1 and v1.2 (anonymized images)
  file_size_check_mvd=$(stat --printf="%s" "${RVC_USE_DATA_ROOT_DIR}/mvd/testing/images/0F9m3hsCahtlL0AzLph9LQ.jpg")
  if [ ${file_size_check_mvd} -ne 630864 ] ; then
    echo "Warning! You are using v1.1 of MVD; testing is done using v1.2!"
    echo "Request it via https://www.mapillary.com/dataset/vistas"
    echo "and unpack the file manually to ${RVC_USE_DATA_ROOT_DIR}/mvd/"
    ALL_TESTSETS_CORRECT=0
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
  ALL_TESTSETS_CORRECT=0
fi

#check Cityscapes test set
if [ ! -d "${RVC_USE_DATA_ROOT_DIR}/cityscapes/leftImg8bit/test" ]; then
  echo "Cityscapes files missing. Please extract cityscapes' leftImg8bit_trainvaltest.zip"
  echo "to ${RVC_USE_DATA_ROOT_DIR}/cityscapes/"
  echo "See https://github.com/ozendelait/rvc_devkit/tree/master/segmentation#dataset-download"
  echo "on how to automatically download/extract the cityscapes files"
fi

count_files_cs=$(find ${RVC_USE_DATA_ROOT_DIR}/cityscapes/leftImg8bit/test/. -maxdepth 2 -type f -printf "\n" 2>/dev/null | wc -l)
if [ ${count_files_cs} -ne 1525 ] ; then
  echo "Missing Cityscapes files (only ${count_files_cs})! Check your Cityscapes test set installation"
  ALL_TESTSETS_CORRECT=0
fi

#check KITTI test set

if [ ! -d "${RVC_USE_DATA_ROOT_DIR}/kitti/testing" ]; then
  KITTI_SEM_URL="https://avg-kitti.s3.eu-central-1.amazonaws.com/data_semantics.zip"
  wget --no-check-certificate --continue $KITTI_SEM_URL -P ${RVC_USE_DATA_ROOT_DIR}/kitti
  unzip ${RVC_USE_DATA_ROOT_DIR}/kitti/data_semantics.zip -d ${RVC_USE_DATA_ROOT_DIR}/kitti
  rm ${RVC_USE_DATA_ROOT_DIR}/kitti/data_semantics.zip
  KITTI_SEM_URL=
fi

count_files_kitti=$(find ${RVC_USE_DATA_ROOT_DIR}/kitti/testing/image_2/*_10.png -maxdepth 1 -type f -printf "\n" 2>/dev/null | wc -l)
if [ ${count_files_kitti} -ne 200 ] ; then
  echo "Missing KITTI files (only ${count_files_kitti})! Check your KITTI test set installation"
  ALL_TESTSETS_CORRECT=0
fi

#check VIPER test set
if [ ! -d "${RVC_USE_DATA_ROOT_DIR}/viper/test" ]; then
  VIPER_TEST_SET_URL="https://viper-dataset.s3.amazonaws.com/test_img_00-60_0_jpg.zip"
  wget --no-check-certificate --continue $VIPER_TEST_SET_URL -P ${RVC_USE_DATA_ROOT_DIR}/viper
  unzip ${RVC_USE_DATA_ROOT_DIR}/viper/test_img_00-60_0_jpg.zip -d ${RVC_USE_DATA_ROOT_DIR}/viper
  rm ${RVC_USE_DATA_ROOT_DIR}/viper/test_img_00-60_0_jpg.zip
fi

count_files_viper=$(find ${RVC_USE_DATA_ROOT_DIR}/viper/test/. -maxdepth 3 -type f -printf "\n" 2>/dev/null | wc -l)
if [ ${count_files_viper} -ne 2500 ] ; then
  echo "Missing VIPER files (only ${count_files_viper})! Check your VIPER test set installation"
  ALL_TESTSETS_CORRECT=0
fi

#check WildDash2 test set
if [ ! -d "${RVC_USE_DATA_ROOT_DIR}/wilddash/test" ]; then
  if [ -f "${RVC_USE_DATA_ROOT_DIR}/wilddash/wd_both_02.zip" ]; then
    mkdir -p "${RVC_USE_DATA_ROOT_DIR}/wilddash/test"
    unzip ${RVC_USE_DATA_ROOT_DIR}/wilddash/wd_both_02.zip -d ${RVC_USE_DATA_ROOT_DIR}/wilddash/test
  else
    echo "WildDash2 test files missing. Please extract WildDash2's wd_public_02.zip"
    echo "to ${RVC_USE_DATA_ROOT_DIR}/wilddash/test/"
    echo "See https://github.com/ozendelait/rvc_devkit/tree/master/segmentation#dataset-download"
    echo "on how to automatically download the WildDash2 files"
  fi
fi

count_files_wilddash=$(find ${RVC_USE_DATA_ROOT_DIR}/wilddash/test/images/. -maxdepth 1 -type f -printf "\n" 2>/dev/null | wc -l)
if [ ${count_files_wilddash} -ne 812 ] ; then
  echo "Missing WildDash2 files (only ${count_files_wilddash})! Check your WildDash2 test set installation"
  ALL_TESTSETS_CORRECT=0
fi

if [ ${ALL_TESTSETS_CORRECT} -eq 1 ] ; then
  echo "Success: all test sets found and verified."
  if [ -n "${RVC_TEST_SET_COLLECT_DIR}" ] ; then
    if [ -z "${RVC_TEST_SET_COLLECT_TYPE}" ] ; then
      echo "use export RVC_TEST_SET_COLLECT_TYPE=<coll_type> to define collection operation type."
      echo "potential choices: dryrun, symlink, copy, move, copy_files, move_files"
    else
      pushd ${RVC_USE_DATA_ROOT_DIR}
        python ${RVC_SEGM_SCRIPT_DIR}/../common/rvc_collect_dirs.py --dst_root "${RVC_TEST_SET_COLLECT_DIR}" --src "./mvd/testing/images;./coco/images/test2017;./cityscapes/leftImg8bit/test;./kitti/testing/image_2/*_10.png;./viper/test;./wilddash/test/images" --type ${RVC_TEST_SET_COLLECT_TYPE} --collapse_depth 3
      popd
    fi
  fi
fi

RVC_SEGM_SCRIPT_DIR=
RVC_USE_DATA_ROOT_DIR=
ALL_TESTSETS_CORRECT=
count_files_mvd=
count_files_coco=
count_files_cs=
count_files_kitti=
count_files_viper=
count_files_wilddash=
