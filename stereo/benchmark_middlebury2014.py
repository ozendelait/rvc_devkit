import argparse
import shutil

from benchmark import *
from dataset_format_middlebury2014 import *
from util import *
from util_stereo import *


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
    
    
    def GetOptions(self, metadata_dict):
        parser = argparse.ArgumentParser()
        parser.add_argument('--middlebury_resolution', choices=['f', 'F', 'h', 'H', 'q', 'Q'], nargs='?')
        args, unknown = parser.parse_known_args()
        
        if args.middlebury_resolution is not None:
            metadata_dict['resolution'] = args.middlebury_resolution.upper()
        else:
            print('Choose the resolution for the Middlebury 2014 stereo datasets by entering f, h, or q:')
            print('  [f] Full resolution (up to 3000 x 2000, ndisp <= 800)')
            print('  [h] Half resolution (up to 1500 x 1000, ndisp <= 400)')
            print('  [q] Quarter resolution (up to 750 x 500, ndisp <= 200)')
            while True:
                response = GetUserInput("> ")
                if response == 'f' or response == 'h' or response == 'q':
                    print('')
                    metadata_dict['resolution'] = response.upper()
                    break
                else:
                    print('Please enter f, h, or q.')
    
    
    def DownloadAndUnpack(self, archive_dir_path, unpack_dir_path, metadata_dict):
        # Download input images (training + test)
        DownloadAndUnzipFile('http://vision.middlebury.edu/stereo/submit3/zip/MiddEval3-data-' + metadata_dict['resolution'] + '.zip', archive_dir_path, unpack_dir_path)
        
        # Download ground truth for left view (training)
        DownloadAndUnzipFile('http://vision.middlebury.edu/stereo/submit3/zip/MiddEval3-GT0-' + metadata_dict['resolution'] + '.zip', archive_dir_path, unpack_dir_path)
        
        # NOTE: Ground truth for right view would be at:
        # 'http://vision.middlebury.edu/stereo/submit3/zip/MiddEval3-GT1-' + metadata_dict['resolution'] + '.zip'
        
        # NOTE: Ground truth for y-disparities would be at:
        # 'http://vision.middlebury.edu/stereo/submit3/zip/MiddEval3-GTy-' + metadata_dict['resolution'] + '.zip'
    
    
    def CanConvertOriginalToFormat(self, dataset_format):
        return isinstance(dataset_format, Middlebury2014Format)
    
    
    def ConvertOriginalToFormat(self, dataset_format, unpack_dir_path, metadata_dict, training_dir_path, test_dir_path):
        # Move datasets into common folder
        src_dir_path = os.path.join(unpack_dir_path, 'MiddEval3')
        
        for (mode, dest_path) in [('training', training_dir_path), ('test', test_dir_path)]:
            src_mode_path = os.path.join(src_dir_path, mode + metadata_dict['resolution'])
            for dataset in os.listdir(src_mode_path):
                os.rename(os.path.join(src_mode_path, dataset),
                          os.path.join(dest_path, self.Prefix() + dataset))
        
        shutil.rmtree(src_dir_path)
    
    
    def CanCreateSubmissionFromFormat(self, dataset_format):
        return isinstance(dataset_format, Middlebury2014Format)
    
    
    def CreateSubmission(self, dataset_format, method, pack_dir_path,
                         metadata_dict, training_dir_path, training_datasets,
                         test_dir_path, test_datasets, archive_base_path):
        # Define training and test output directories
        dest_training_path = os.path.join(pack_dir_path, 'training' + metadata_dict['resolution'])
        dest_test_path = os.path.join(pack_dir_path, 'test' + metadata_dict['resolution'])
        
        for (src_folder_path, benchmark_and_dataset_name, dest_folder_path, original_dataset_name) in (
                [(training_dir_path, a, dest_training_path, b) for (a, b) in training_datasets] +
                [(test_dir_path, a, dest_test_path, b) for (a, b) in test_datasets]):
            src_dataset_path = os.path.join(src_folder_path, benchmark_and_dataset_name)
            
            # Create destination dataset folder
            dest_dataset_path = os.path.join(dest_folder_path, original_dataset_name)
            MakeDirsExistOk(dest_dataset_path)
            
            # Copy files
            for filename in ['disp0' + method + '.pfm', 'time' + method + '.txt']:
                shutil.copy2(os.path.join(src_dataset_path, filename),
                             os.path.join(dest_dataset_path, filename))
        
        # Create the archive and clean up.
        archive_filename = ZipDirectory(archive_base_path, pack_dir_path)
        DeleteFolderContents(pack_dir_path)
        
        return archive_filename
    
