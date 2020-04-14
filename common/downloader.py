import requests, os, sys, argparse, re, tqdm

CHUNK_SIZE = 512 * 1024

#based on StackOverflow answers: https://stackoverflow.com/a/39225039 ; https://stackoverflow.com/a/14270698 ; https://stackoverflow.com/a/22894211/

# try_resume_bytes  0: evaluate file size; if file on disk is smaller retry with resume
# try_resume_bytes >0: resume from this position
# try_resume_bytes <0: redownload the file (overwrites any data on disk)

def download_file_from_google_drive(id, destination, try_resume_bytes=-1, total_sz = None):
    URL = "https://docs.google.com/uc?export=download"
    session = requests.Session()
    resume_headers = {}
    if try_resume_bytes > 0:
        resume_headers =  {'Range': 'bytes=%d-' % try_resume_bytes}
    response = session.get(URL, params = { 'id' : id }, headers=resume_headers, stream = True)
    token = get_confirm_token(response)
    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, headers=resume_headers, stream = True)
    if not response.encoding is None and '01 Jan 1990' in response.headers.get('Expires',''):
        print("Download limit reached for file id "+id+ ", skipping. Please retry in 24h.")
        return
    if os.path.isdir(destination):
        # based on https://github.com/wkentaro/gdown/blob/master/gdown/download.py
        fname = re.search('filename="(.*)"', response.headers.get("Content-Disposition",""))
        if not fname is None:
            fname = fname.groups()[0]
        if not fname is None and len(fname) > 0:
            destination = os.path.join(destination, fname)
        else:
            destination = os.path.join(destination, id+".bin")

    if total_sz == None:
        try:
            total_sz = response.headers.get("Content-Length")
            if total_sz is not None:
                total_sz = int(total_sz)
        except:
            total_sz = None

    if try_resume_bytes <= 0 and os.path.exists(destination):
        loc_sz = os.stat(destination).st_size
        if loc_sz > 0 and loc_sz == total_sz:  # file already downloaded
            print("Info: Target file " + destination + " exists and is of correct size. ")
            return
        if try_resume_bytes < 0:
            print("Error: Target file "+destination+" already exists. ")
            return
        else:
            resume_start = max(0,(loc_sz//CHUNK_SIZE)-2) * CHUNK_SIZE #make sure we redownload the last two chunks completely (these could have been corruptes)
            if resume_start == 0:
                os.remove(destination) #do a regular download
            else:
                session.close() # we need a new session that has seeked to the resume-byte position
                return download_file_from_google_drive(id, destination, try_resume_bytes=resume_start)

    save_response_content(response, destination, resume_bytes = try_resume_bytes, total_sz = total_sz)

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value
    return None

def save_response_content(response, destination, resume_bytes = 0, total_sz = None):
    file_mode = "wb" if resume_bytes <= 0 else "r+b"
    pbar = tqdm.tqdm(total=total_sz, initial=max(0,resume_bytes), unit="B", unit_scale=True)
    with open(destination, file_mode) as f:
        if resume_bytes > 0:
            f.seek(resume_bytes)
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                pbar.update(len(chunk))

def downl_main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('--id', type=str, default="joint_mapping.json",
                        help="Google Drive Id to download; part after id= from GetSharableLink")
    parser.add_argument('--target_sz', type=int, default=None,
                        help="Supply known target size (needed for progress of chunk-based downloads)")
    parser.add_argument('--output', type=str, default="./",
                        help="Output file name, will try to use source filename if supplied with a directory")
    args = parser.parse_args(argv)
    destination = os.path.abspath(os.path.realpath(args.output))
    google_drive_id = args.id.replace("https://drive.google.com/open?id=","")
    download_file_from_google_drive(google_drive_id, destination, try_resume_bytes=0, total_sz=args.target_sz)

if __name__ == "__main__":
    sys.exit(downl_main())