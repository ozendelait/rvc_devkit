import shutil

from dataset_format import *
from dataset_format_kitti2015 import *
from util import *
from util_stereo import *


# Middlebury 2014 Stereo dataset format
class Middlebury2014Format(DatasetFormat):
    
    def Name(self):
        return 'Middlebury 2014 Stereo format'
    
    
    def FolderName(self):
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
    
    
    def CanConvertInputToFormat(self, dataset_format):
        return isinstance(dataset_format, Kitti2015Format)
    
    
    # Helper for ConvertInputToFormat()
    def ConvertFile(self, in_name, out_name, out_extension, in_dataset_path, dataset_name, out_path):
        in_path = os.path.join(in_dataset_path, in_name)
        if os.path.isfile(in_path):
            out_dir = os.path.join(out_path, out_name)
            MakeDirsExistOk(out_dir)
            shutil.copy2(in_path, os.path.join(out_dir, dataset_name + out_extension))
    
    
    def ConvertInputToFormat(self, dataset_format, dataset_name, in_path, out_path):
        # Convert to Kitti2015Format.
        in_dataset_path = os.path.join(in_path, dataset_name)
        
        convert_file = lambda in_name, out_name, out_extension : (
            self.ConvertFile(in_name, out_name, out_extension, in_dataset_path, dataset_name, out_path))
        
        convert_file('im0.png', 'image_2', '.png')
        convert_file('im1.png', 'image_3', '.png')
        
        disp_gt_path = os.path.join(in_dataset_path, 'disp0GT.pfm')
        if os.path.isfile(disp_gt_path):
            disp_occ_0_dir = os.path.join(out_path, 'disp_occ_0')
            MakeDirsExistOk(disp_occ_0_dir)
            ConvertMiddlebury2014PfmToKitti2015Png(disp_gt_path, os.path.join(disp_occ_0_dir, dataset_name + '.png'))
            
            mask_path = os.path.join(in_dataset_path, 'mask0nocc.png')
            if os.path.isfile(mask_path):
                disp_noc_0_dir = os.path.join(out_path, 'disp_noc_0')
                MakeDirsExistOk(disp_noc_0_dir)
                ConvertMiddlebury2014PfmToKitti2015PngNoccOnly(disp_gt_path, mask_path, os.path.join(disp_noc_0_dir, dataset_name + '.png'))
        
        convert_file('cameras.txt', 'cameras', '.txt')
        convert_file('images.txt', 'images', '.txt')
        convert_file('gt_sample_count.pfm', 'gt_sample_count', '.pfm')
        convert_file('gt_uncertainty.pfm', 'gt_uncertainty', '.pfm')
        convert_file('mask.png', 'mask', '.png')
        convert_file('mask_dynamic_objects.png', 'mask_dynamic_objects', '.png')
        convert_file('mask_eval.png', 'mask_eval', '.png')
        convert_file('obj_map.png', 'obj_map', '.png')
    
    
    def CanConvertOutputToFormat(self, dataset_format):
        return False
    
    
    def ConvertOutputToFormat(self, dataset_format, method_name, dataset_name, in_path, out_path):
        raise NotImplementedError()
