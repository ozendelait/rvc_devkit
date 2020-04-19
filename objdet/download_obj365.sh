#!/bin/sh
# Downloads the objects365 dataset
# The AWS-stored version is provided for participants of RVC 2020 
# and may be taken down afterwards without warning!
#
# See the enclosed license.txt for license terms
# The annotations in this dataset along with this website belong to the Objects365 Consortium 
# and are licensed under a Creative Commons Attribution 4.0 License. To view the license, visit https://creativecommons.org/licenses/by-sa/4.0/ .
# When using this dataset, please cite:
# Objects365: A Large-scale, High-quality Dataset for Object Detection
# Shuai Shao, Zeming Li, Tianyuan Zhang, Chao Peng, Gang Yu, Jing Li, Xiangyu Zhang, Jian Sun ICCV, 2019

# This script requires the awscli packages to work; 
# If missing, they can be installed via:   
#   pip install awscli 
# (use gitbash for MS Windows)

RVC_OBJ365_SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
# All data is downloaded to subfolders of RVC_DATA_DIR; if this is not defined: use this script's dir
if [ -z "${RVC_DATA_DIR}" ]; then
  RVC_OBJ365_TRG_DIR=${RVC_OBJ365_SCRIPT_DIR}/../datasets/objects365
else
  RVC_OBJ365_TRG_DIR=${RVC_DATA_DIR}/objects365
fi

echo "Downloading objects365 to ${RVC_OBJ365_TRG_DIR}"

mkdir -p ${RVC_OBJ365_TRG_DIR}
aws s3 --no-sign-request sync s3://objects365/objects365-v2-released/ ${RVC_OBJ365_TRG_DIR}

RVC_OBJ365_TRG_DIR=
RVC_OBJ365_SCRIPT_DIR=

echo "Finished donwloading objects365."