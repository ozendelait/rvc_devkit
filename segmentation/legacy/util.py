import errno
import os
import shutil
import sys
import traceback
import zipfile

if sys.version_info[0] == 2:
    import urllib2
else:
    import urllib.request


# Converts a string to bytes (for writing the string into a file). Provided for
# compatibility with Python 2 and 3.
def StrToBytes(text):
    if sys.version_info[0] == 2:
        return text
    else:
        return bytes(text, 'UTF-8')


# Outputs the given text and lets the user input a response (submitted by
# pressing the return key). Provided for compatibility with Python 2 and 3.
def GetUserInput(text):
    if sys.version_info[0] == 2:
        return raw_input(text)
    else:
        return input(text)


# Creates the given directory (hierarchy), which may already exist. Provided for
# compatibility with Python 2 and 3.
def MakeDirsExistOk(directory_path):
    try:
        os.makedirs(directory_path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


# Deletes all files and folders within the given folder.
def DeleteFolderContents(folder_path):
  for file_name in os.listdir(folder_path):
    file_path = os.path.join(folder_path, file_name)
    try:
      if os.path.isfile(file_path):
        os.unlink(file_path)
      else:  #if os.path.isdir(file_path):
        shutil.rmtree(file_path)
    except Exception as e:
      print('Exception in DeleteFolderContents():')
      print(e)
      print('Stack trace:')
      print(traceback.format_exc())


# Creates the given directory, respectively deletes all content of the directory
# in case it already exists.
def MakeCleanDirectory(folder_path):
    if os.path.isdir(folder_path):
        DeleteFolderContents(folder_path)
    else:
        MakeDirsExistOk(folder_path)


# Downloads the file with given GDrive ID to the given destination path.
# https://stackoverflow.com/a/39225039
def DownloadFileFromGDrive(gdrive_id, dest_file_path):
    import requests

    def get_confirm_token(response):
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                return value

        return None

    def save_response_content(response, destination):
        CHUNK_SIZE = 32768

        with open(dest_file_path, "wb") as f:
            for chunk in response.iter_content(CHUNK_SIZE):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)

    URL = "https://drive.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params = { 'id' : gdrive_id }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : gdrive_id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)

    save_response_content(response, dest_file_path)    
    pass

# Downloads the given URL to a file in the given directory. Returns the
# path to the downloaded file.
# In part adapted from: https://stackoverflow.com/questions/22676
def DownloadFile(url, dest_dir_path):
    file_name = url.split('/')[-1]
    dest_file_path = os.path.join(dest_dir_path, file_name)
    
    if os.path.isfile(dest_file_path):
        print('The following file already exists:')
        print(dest_file_path)
        print('Please choose whether to re-download and overwrite the file [o] or to skip downloading this file [s] by entering o or s.')
        while True:
            response = GetUserInput("> ")
            if response == 's':
                return dest_file_path
            elif response == 'o':
                break
            else:
                print('Please enter o or s.')
    
    url_object = None
    if sys.version_info[0] == 2:
        url_object = urllib2.urlopen(url)
    else:
        url_object = urllib.request.urlopen(url)
    
    with open(dest_file_path, 'wb') as outfile:
        meta = url_object.info()
        file_size = 0
        if sys.version_info[0] == 2:
            file_size = int(meta.getheaders("Content-Length")[0])
        else:
            file_size = int(meta["Content-Length"])
        print("Downloading: %s (size [bytes]: %s)" % (url, file_size))
        
        file_size_downloaded = 0
        block_size = 8192
        while True:
            buffer = url_object.read(block_size)
            if not buffer:
                break
            
            file_size_downloaded += len(buffer)
            outfile.write(buffer)
            
            sys.stdout.write("%d / %d  (%3f%%)\r" % (file_size_downloaded, file_size, file_size_downloaded * 100. / file_size))
            sys.stdout.flush()
    
    return dest_file_path


# Unzips the given zip file into the given directory.
def UnzipFile(file_path, unzip_dir_path):
    print("Extracting archive: %s" % file_path)
    zip_ref = zipfile.ZipFile(open(file_path, 'rb'))
    zip_ref.extractall(unzip_dir_path)
    zip_ref.close()


# Creates a zip file with the contents of the given directory.
# The archive_base_path must not include the extension .zip. The full, final
# path of the archive is returned by the function.
def ZipDirectory(archive_base_path, root_dir_path):
    print("Creating archive: %s.zip" % archive_base_path)
    with zipfile.ZipFile(archive_base_path + '.zip', "w", zipfile.ZIP_DEFLATED, allowZip64=True) as zf:
        for root, dirnames, filenames in os.walk(root_dir_path):
            # move files (empty directories are ignored)
            for filename in filenames:
                src_name = os.path.join(root, filename)
                tgt_name = os.path.normpath(os.path.join(root[len(root_dir_path):], filename))
                zf.write(src_name, tgt_name)
    return archive_base_path + '.zip'


# Downloads a zip file and directly unzips it.
def DownloadAndUnzipFile(url, archive_dir_path, unzip_dir_path):
    archive_path = DownloadFile(url, archive_dir_path)
    UnzipFile(archive_path, unzip_dir_path)
