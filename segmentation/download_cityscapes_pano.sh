#!/bin/sh

# Downloads the KITTI dataset with panoptic GT. (~0.5GB of input images and annotations)
# Based on https://github.com/mseg-dataset/mseg-api/blob/master/download_scripts/mseg_download_cityscapes.sh

# By using this script, you agree to all terms and
# conditions set forth by the Cityscapes dataset
# creators and certify you have lawfully obtained
# a license from their website.
# License terms can be found here:
# https://github.com/mcordts/cityscapesScripts/blob/master/license.txt

RVC_CITYSCAPES_TRG_DIR=$1

echo "Cityscapes will be downloaded to "$RVC_CITYSCAPES_TRG_DIR
mkdir -p $RVC_CITYSCAPES_TRG_DIR
# ------------------- Downloading -------------------------------

# Cityscapes images download URL (leftImg8bit_trainvaltest.zip)
CITYSCAPES_IMGS_ZIP_URL="https://www.cityscapes-dataset.com/file-handling/?packageID=3"
# Cityscapes ground truth download URL (for gtFine_trainvaltest.zip) 
CITYSCAPES_GT_ZIP_URL="https://www.cityscapes-dataset.com/file-handling/?packageID=1"

pushd $RVC_CITYSCAPES_TRG_DIR
CITYSCAPES_USERNAME_ESC=$(echo "$CITYSCAPES_USERNAME" | sed "s/@/%40/g")
CITYSCAPES_PASSWORD_ESC=$(echo "$CITYSCAPES_PASSWORD" | sed "s/@/%40/g" | sed "s/\\?/%3F/g" | sed "s/=/%3D/g" | sed "s/\\+/%2B/g" | sed "s/&/%26/g" | sed "s/\\$/%24/g")
CITYSCAPES_USERDATA="username=$CITYSCAPES_USERNAME_ESC&password=$CITYSCAPES_PASSWORD_ESC&submit=Login"
echo $CITYSCAPES_USERDATA
wget --no-check-certificate --keep-session-cookies --save-cookies=cookies.txt --post-data $CITYSCAPES_USERDATA https://www.cityscapes-dataset.com/login/
CITYSCAPES_USERDATA=
CITYSCAPES_USERNAME_ESC=
CITYSCAPES_PASSWORD_ESC=
# will download "gtFine_trainvaltest.zip" (241MB)
wget -O gtFine_trainvaltest.zip --no-check-certificate --continue  --load-cookies cookies.txt --content-disposition $CITYSCAPES_GT_ZIP_URL
# will download "leftImg8bit_trainvaltest.zip (11GB)"
wget -O leftImg8bit_trainvaltest.zip --no-check-certificate --continue  --load-cookies cookies.txt --content-disposition $CITYSCAPES_IMGS_ZIP_URL
rm cookies.txt
rm index.html

echo "Cityscapes panoptic dataset downloaded."
popd 

RVC_CITYSCAPES_TRG_DIR=
