import shutil

from dataset_format import *
from util import *
from util_stereo import *


# Middlebury 2014 Stereo dataset format
class Middlebury2014Format(DatasetFormat):
    
    def Name(self):
        return 'Middlebury 2014 Stereo format'
    
    
    def Identifier(self):
        return 'middlebury2014'
    
    
    def Website(self):
        return 'http://vision.middlebury.edu/stereo/data/scenes2014/'
    
    
    def ListDatasets(self, dataset_folder_path):
        return [dataset for dataset
                in os.listdir(dataset_folder_path)
                if os.path.isdir(os.path.join(dataset_folder_path, dataset))]
    
    
    def ListMethods(self, dataset_folder_path, dataset_name):
        result_file_scheme = [('disp0', '.pfm'), ('time', '.txt')]
        
        contains_all_result_files = lambda path, method : (
            all([os.path.isfile(os.path.join(path, prefix + method + suffix))
                for (prefix, suffix) in result_file_scheme]))
        
        dataset_path = os.path.join(dataset_folder_path, dataset_name)
        first_prefix = result_file_scheme[0][0]
        first_suffix = result_file_scheme[0][1]
        
        method_list = []
        
        for filename in os.listdir(dataset_path):
            if filename.startswith(first_prefix) and filename.endswith(first_suffix):
                method = filename[len(first_prefix):-len(first_suffix)]  # strip prefix and suffix
                if contains_all_result_files(dataset_path, method):
                    method_list.append(method)
        
        return method_list
    
    
    def PrepareRunningMethod(self, method_name, dataset_folder_path, dataset_name):
        im0_path = os.path.join(dataset_folder_path, dataset_name, 'im0.png')
        im1_path = os.path.join(dataset_folder_path, dataset_name, 'im1.png')
        calib = ReadMiddlebury2014CalibFile(os.path.join(dataset_folder_path, dataset_name, 'calib.txt'))
        output_dir_path = os.path.join(dataset_folder_path, dataset_name)
        return [im0_path, im1_path, calib['ndisp'], output_dir_path]
