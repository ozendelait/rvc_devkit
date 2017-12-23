import shutil
import struct

from benchmark import *
from util import *


# Returns the reported runtime as a float in seconds.
def ReadMiddlebury2014TimeFile(path):
    time = -1
    with open(path, 'rb') as time_file:
        text = time_file.read().strip()
        try:
            time = float(text)
        except ValueError:
            raise Exception('Cannot parse time file: ' + path)
    return time


def WriteMiddlebury2014CalibFile(path,
                                 left_fx, left_fy, left_cx, left_cy,
                                 right_fx, right_fy, right_cx, right_cy,
                                 baseline_in_mm,
                                 width,
                                 height,
                                 ndisp):
    calib_file = open(path, 'wb')
    calib_file.write(StrToBytes('cam0=[' + str(left_fx) + ' 0 ' + str(left_cx) + '; 0 ' + str(left_fy) + ' ' + str(left_cy) + '; 0 0 1]\n'))
    calib_file.write(StrToBytes('cam1=[' + str(right_fx) + ' 0 ' + str(right_cx) + '; 0 ' + str(right_fy) + ' ' + str(right_cy) + '; 0 0 1]\n'))
    calib_file.write(StrToBytes('doffs=' + str(right_cx - left_cx) + '\n'))
    calib_file.write(StrToBytes('baseline=' + str(baseline_in_mm) + '\n'))
    calib_file.write(StrToBytes('width=' + str(width) + '\n'))
    calib_file.write(StrToBytes('height=' + str(height) + '\n'))
    calib_file.write(StrToBytes('ndisp=' + str(ndisp) + '\n'))
    calib_file.close()


# Returns a 3-tuple (width, height, pixels), where pixels is a tuple of floats,
# ordered as in the PFM file (i.e., the bottommost row comes first).
def ReadMiddlebury2014PfmFile(path):
    pfm_file = open(path, 'rb')
    
    state = 0
    word = ''
    width = -1
    height = -1
    little_endian = True
    while True:
        character = pfm_file.read(1).decode('UTF-8')
        if not character:
            raise Exception('Cannot parse pfm file: unexpected end of file')
        elif character == '#' or character == ' ' or character == '\n' or character == '\r' or character == '\t':
            # Parse word
            if word != '':
                if state == 0:
                    if word != 'Pf':
                        raise Exception('Cannot parse pfm file: header is not "Pf"')
                    state = 1
                elif state == 1:
                    width = int(word)
                    state = 2
                elif state == 2:
                    height = int(word)
                    state = 3
                elif state == 3:
                    little_endian = float(word) < 0
                    break
            
            word = ''
            
            if character == '#':
                # Skip comment.
                pfm_file.readline()
            else:
                # Skip whitespace
                continue
        
        word += character
    
    # Read float buffer
    pixel_count = width * height
    endian_character = '<' if little_endian else '>'
    pixels = struct.unpack(endian_character + str(pixel_count) + 'f', pfm_file.read(4 * pixel_count))
    
    pfm_file.close()
    
    return (width, height, pixels)


# Expects pixels as a list of floats
def WriteMiddlebury2014PfmFile(path, width, height, pixels):
    pfm_file = open(path, 'wb')
    pfm_file.write(StrToBytes('Pf\n'))
    pfm_file.write(StrToBytes(str(width) + ' ' + str(height) + '\n'))
    pfm_file.write(StrToBytes('-1\n'))  # negative number means little endian
    pfm_file.write(struct.pack('<' + str(len(pixels)) + 'f', *pixels))  # < means using little endian
    pfm_file.close()


class Middlebury2014(Benchmark):
    def Name(self):
        return "Middlebury 2014 Stereo"
    
    
    def Prefix(self):
        return "Middlebury2014_"
    
    
    def Website(self):
        return 'http://vision.middlebury.edu/stereo/eval3/'
    
    
    def SupportsTrainingDataOnlySubmissions(self):
        return True
    
    
    def SupportsTrainingDataInFullSubmissions(self):
        return True
    
    
    def GetOptions(self):
        print('Choose the resolution for the Middlebury 2014 stereo datasets by entering f, h, or q:')
        print('  [f] Full resolution (up to 3000 x 2000, ndisp <= 800)')
        print('  [h] Half resolution (up to 1500 x 1000, ndisp <= 400)')
        print('  [q] Quarter resolution (up to 750 x 500, ndisp <= 200)')
        self.middlebury_resolution = ''
        while True:
            response = GetUserInput("> ")
            if response == 'f' or response == 'h' or response == 'q':
                self.middlebury_resolution = response.upper()
                break
            else:
                print('Please enter f, h, or q.')
    
    
    def DownloadAndConvert(self, archive_dir_path, unpack_dir_path, datasets_dir_path, training_dir_path, test_dir_path):
        # Download input images (training + test)
        DownloadAndUnzipFile('http://vision.middlebury.edu/stereo/submit3/zip/MiddEval3-data-' + self.middlebury_resolution + '.zip', archive_dir_path, unpack_dir_path)
        
        # Download ground truth for left view (training)
        DownloadAndUnzipFile('http://vision.middlebury.edu/stereo/submit3/zip/MiddEval3-GT0-' + self.middlebury_resolution + '.zip', archive_dir_path, unpack_dir_path)
        
        # NOTE: Ground truth for right view would be at:
        # 'http://vision.middlebury.edu/stereo/submit3/zip/MiddEval3-GT1-' + self.middlebury_resolution + '.zip'
        
        # NOTE: Ground truth for y-disparities would be at:
        # 'http://vision.middlebury.edu/stereo/submit3/zip/MiddEval3-GTy-' + self.middlebury_resolution + '.zip'
        
        # Move datasets into common folder
        src_dir_path = os.path.join(unpack_dir_path, 'MiddEval3')
        
        src_training_dir_path = os.path.join(src_dir_path, 'training' + self.middlebury_resolution)
        for dataset in os.listdir(src_training_dir_path):
            os.rename(os.path.join(src_training_dir_path, dataset),
                      os.path.join(training_dir_path, self.Prefix() + dataset))
        
        src_test_dir_path = os.path.join(src_dir_path, 'test' + self.middlebury_resolution)
        for dataset in os.listdir(src_test_dir_path):
            os.rename(os.path.join(src_test_dir_path, dataset),
                      os.path.join(test_dir_path, self.Prefix() + dataset))
        
        shutil.rmtree(src_dir_path)
        
        # Store chosen resolution
        with open(os.path.join(datasets_dir_path, self.Prefix() + 'settings.txt'), 'wb') as resolution_file:
            resolution_file.write(StrToBytes('resolution ' + self.middlebury_resolution))
    
    
    def CreateSubmissionArchive(self, method, datasets_dir_path, training_dataset_names, test_dataset_names, training_dir_path, test_dir_path, pack_dir_path, archive_base_path):
        # Read resolution
        with open(os.path.join(datasets_dir_path, self.Prefix() + 'settings.txt'), 'rb') as resolution_file:
            self.middlebury_resolution = resolution_file.read().split()[1]
        
        # Define training and test output directories
        dest_training_path = os.path.join(pack_dir_path, 'training' + self.middlebury_resolution)
        dest_test_path = os.path.join(pack_dir_path, 'test' + self.middlebury_resolution)
        
        # Handle training and test datasets in the same way.
        for item in ([(name, True) for name in training_dataset_names] +
                     [(name, False) for name in test_dataset_names]):
            benchmark_and_dataset_name = item[0]
            is_training = item[1]
            
            src_dataset_path = os.path.join(training_dir_path if is_training else test_dir_path, benchmark_and_dataset_name)
            original_dataset_name = benchmark_and_dataset_name[len(self.Prefix()):]
            
            # Create destination dataset folder
            dest_dataset_path = os.path.join(dest_training_path if is_training else dest_test_path, original_dataset_name)
            MakeDirsExistOk(dest_dataset_path)
            
            # Copy .pfm file to dest_dataset_path
            shutil.copy2(os.path.join(src_dataset_path, 'disp0' + method + '.pfm'),
                         os.path.join(dest_dataset_path, 'disp0' + method + '.pfm'))
            
            # Copy time file to dest_dataset_path
            shutil.copy2(os.path.join(src_dataset_path, 'time' + method + '.txt'),
                         os.path.join(dest_dataset_path, 'time' + method + '.txt'))
        
        # Create the archive and clean up.
        archive_filename = ZipDirectory(archive_base_path, pack_dir_path)
        DeleteFolderContents(pack_dir_path)
        
        return archive_filename
    
