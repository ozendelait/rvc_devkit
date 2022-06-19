import requests, os, sys, argparse, re, time, tqdm

CHUNK_SIZE = 32 * 1024
RESUME_SIZE_MAX =  CHUNK_SIZE * 16352 # little less than 0.5GB

def quick_url_encode(url):
    return url.split('/')[-1].replace('?','%3F').replace('&','%26')


def download_file_from_google_drive(id, destination, try_resume_bytes=-1, total_sz = None):
    gdrive_url = "https://docs.google.com/uc?export=download"
    params = {'id': id}
    download_file_with_resume(gdrive_url, destination, try_resume_bytes=-1, total_sz=None, params=params)

#based on StackOverflow answers: https://stackoverflow.com/a/39225039 ; https://stackoverflow.com/a/14270698 ; https://stackoverflow.com/a/22894211/

# try_resume_bytes  0: evaluate file size; if file on disk is smaller retry with resume
# try_resume_bytes >0: resume from this position in bytes
# try_resume_bytes <0: fails if target file exists of wrong size

def download_file_with_resume(url, destination, try_resume_bytes=-1, total_sz = None, params={}):
    while True: # iterate sessions until file downloaded or failure:
        needs_ssl = url.startswith("https://")
        with requests.Session() as session:
            resume_headers = {}
            try_resume_bytes_next = 0
            if try_resume_bytes > 0:
                if total_sz is None:
                    resume_headers =  {'Range': 'bytes=%d-' % try_resume_bytes}
                else:
                    open_sz = (total_sz - try_resume_bytes)
                    if open_sz > RESUME_SIZE_MAX:
                        open_sz = RESUME_SIZE_MAX
                        try_resume_bytes_next = try_resume_bytes + open_sz
                    resume_headers =  {'Range': 'bytes=%d-%d' % (try_resume_bytes, try_resume_bytes+open_sz)}
            try:
                response = session.get(url, params = params, headers=resume_headers, stream = True)
            except requests.exceptions.SSLError as ssl_execption:
                if not needs_ssl: #redirected http to https
                    return download_file_with_resume(url.replace("http://","https://"), destination, try_resume_bytes, total_sz, params)
                if "RVC_CUSTOM_SSL_SKIP_VERIFY" in os.environ:
                    #many python openssl requests lib setups installed via pip or conda seem to be broken in 2020; until this is fixed allow user to skip verification
                    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
                    response = session.get(url, params=params, headers=resume_headers, stream=True, verify=False)
                else:
                    ssl_err_msg = "Error: it looks like your python requests SSL verification is broken."
                    ssl_err_msg += "\nTry to update certifi: \nconda install -c anaconda certifi\nOtherwise you can skip ssl verifications by defining:\nexport RVC_CUSTOM_SSL_SKIP_VERIFY=1"
                    if sys.version_info[0] < 3:
                        sys.stderr.write(str(ssl_err_msg))
                    else:
                        print(ssl_err_msg,file=sys.stderr)
                    raise ssl_execption

            if "docs.google.com" in url:
                token = get_confirm_token(response)
                if token:
                    params_with_token = {'confirm' : token }
                    params_with_token.update(params)
                    response = session.get(url, params = params_with_token, headers=resume_headers, stream = True)
            if not response.encoding is None and '01 Jan 1990' in response.headers.get('Expires',''):
                print("Download limit reached for file "+params.get('id',url)+ ", skipping. Please retry in 24h.")
                session.close()
                return
            dest_dir = os.path.dirname(os.path.realpath(destination))
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
            if os.path.isdir(destination):
                # based on https://github.com/wkentaro/gdown/blob/master/gdown/download.py
                fname = re.search('filename="(.*)"', response.headers.get("Content-Disposition",""))
                if not fname is None:
                    fname = fname.groups()[0]
                if not fname is None and len(fname) > 0:
                    destination = os.path.join(destination, fname)
                else:
                    filename_part = params['id']+'.bin' if 'id' in params else quick_url_encode(url)
                    destination = os.path.join(destination, filename_part)
    
            if total_sz is None:
                try:
                    total_sz = response.headers.get("Content-Length")
                    if total_sz is not None:
                        total_sz = int(total_sz)
                except:
                    total_sz = None
                    
            if try_resume_bytes <= 0 and os.path.exists(destination):
                loc_sz = os.stat(destination).st_size
                if loc_sz > 0 and loc_sz == total_sz:  # file already downloaded
                    print("Info: target file " + destination + " already exists and is of correct size. Skipping")
                    session.close()
                    return
                if try_resume_bytes < 0:
                    print("Error: Target file "+destination+" already exists. ")
                    session.close()
                    return
                else:
                    resume_start = max(0,(loc_sz//CHUNK_SIZE)-2) * CHUNK_SIZE #make sure we redownload the last two chunks completely (these could have been corruptes)
                    if resume_start == 0:
                        os.remove(destination) #do a regular download
                    else:
                        session.close() # we need a new session that has seeked to the resume-byte position
                        time.sleep(0.5)#prevent connection spamming
                        try_resume_bytes=resume_start
                        continue # retry with new resume download connection 
            try:
                save_response_content(response, destination, resume_bytes = try_resume_bytes, total_sz = total_sz)
            except Exception as rethrow_execption:
                raise rethrow_execption
            finally:
                session.close()
            if try_resume_bytes_next <= 0 or try_resume_bytes_next < try_resume_bytes:
                break # finished download
            
            #still more chunks need to be downloaded
            time.sleep(0.3)#prevent connection spamming 
            try_resume_bytes=try_resume_bytes_next # retry with new resume download connection
            


def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value
    return None

def save_response_content(response, destination, resume_bytes = 0, total_sz = None):
    file_mode = "wb" if resume_bytes <= 0 else "r+b"
    pbar = tqdm.tqdm(total=total_sz, initial=max(0,resume_bytes), unit="B", unit_scale=True, mininterval=0.7)
    with open(destination, file_mode) as f:
        if resume_bytes > 0:
            f.seek(resume_bytes)
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                pbar.update(len(chunk))

def downl_main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('--id', type=str, default=None,
                        help="Google Drive Id to download; part after id= from GetSharableLink")
    parser.add_argument('--url', type=str, default=None,
                        help="Download directly from an url")
    parser.add_argument('--target_sz', type=int, default=None,
                        help="Supply known target size (needed for progress of chunk-based downloads)")
    parser.add_argument('--output', type=str, default="./",
                        help="Output file name, will try to use source filename if supplied with a directory")
    args = parser.parse_args(argv)
    destination = os.path.abspath(os.path.realpath(args.output))

    if not args.id is None:
        google_drive_id = args.id.replace("https://drive.google.com/open?id=","")
        download_file_from_google_drive(google_drive_id, destination, try_resume_bytes=0, total_sz=args.target_sz)
    if not args.url is None:
        download_file_with_resume(args.url, destination, try_resume_bytes=0, total_sz=args.target_sz, params={})

if __name__ == "__main__":
    sys.exit(downl_main())
