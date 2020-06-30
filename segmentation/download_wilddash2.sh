#!/bin/sh

# Based on https://github.com/mseg-dataset/mseg-api/blob/master/download_scripts/mseg_download_wilddash.sh
# Downloads the Wilddash dataset.

# By using this script, you agree to the
# WildDash license agreement:
# https://wilddash.cc/license/wilddash
# If over VPN, otherwise upload from browswer.

# -------------------------------------------------------------------

# wd benchmark images download URL
WILDDASH_BENCH_ZIP_URL="https://wilddash.cc/download/wd_both_02.zip"
# wd ground truth download URL
WILDDASH_GT_ZIP_URL="https://wilddash.cc/download/wd_public_02.zip"
WILDDASH_COOKIE_FILE=wd_cookies_downl.txt
WILDDASH_DST_FOLDER=$1

echo "Downloading WildDash to $WILDDASH_DST_FOLDER"
mkdir -p $WILDDASH_DST_FOLDER
cd $WILDDASH_DST_FOLDER

if [ -f "$WILDDASH_COOKIE_FILE" ]; then
  echo "Restarting download with existing session. If this fails, manually delete $WILDDASH_COOKIE_FILE and retry."
else
	#start session to get CSRF token
	wget --no-verbose --no-check-certificate --keep-session-cookies --save-cookies=wd_cookies_auth.txt -O wd_resp_auth_token.html https://wilddash.cc/accounts/login
	#safe CSRF in variable
	WILDDASH_CSRF=$(grep csrfmiddlewaretoken wd_resp_auth_token.html | sed "s/.*value='\(.*\)'.*/\1/")
	rm wd_resp_auth_token.html
	#escape @,?,+,& symbol
	WILDDASH_USERNAME_ESC=$(echo "$WILDDASH_USERNAME" | sed "s/@/%40/g")
	WILDDASH_PASSWORD_ESC=$(echo "$WILDDASH_PASSWORD" | sed "s/@/%40/g" | sed "s/\\?/%3F/g" | sed "s/=/%3D/g" | sed "s/\\+/%2B/g" | sed "s/&/%26/g" | sed "s/\\$/%24/g")
	#login to the WildDash webpage
	WILDDASH_USERDATA="username=$WILDDASH_USERNAME_ESC&password=$WILDDASH_PASSWORD_ESC&csrfmiddlewaretoken=$WILDDASH_CSRF&submit=Login"
	wget --no-verbose --no-check-certificate --keep-session-cookies --load-cookies=wd_cookies_auth.txt --save-cookies=$WILDDASH_COOKIE_FILE -O wd_login_page.html --post-data $WILDDASH_USERDATA https://wilddash.cc/accounts/login
	#cleanup env
	WILDDASH_USERDATA=
	WILDDASH_CSRF=
	WILDDASH_USERNAME_ESC=
	WILDDASH_PASSWORD_ESC=
	rm wd_cookies_auth.txt
	rm wd_login_page.html
fi
# will download "wd_public_02.zip" (3.2GB) and "wd_both_02.zip" (0.4GB)
wget --no-check-certificate --continue --load-cookies $WILDDASH_COOKIE_FILE --content-disposition $WILDDASH_GT_ZIP_URL
wget --no-check-certificate --continue --load-cookies $WILDDASH_COOKIE_FILE --content-disposition $WILDDASH_BENCH_ZIP_URL

echo "WildDash v2 alpha dataset downloaded."
