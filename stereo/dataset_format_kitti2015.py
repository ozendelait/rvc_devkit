from dataset_format import *
import dataset_format_middlebury2014  # Avoid issues with circular dependency using this import style
from util import *
from util_stereo import *


# Kitti 2015 Stereo dataset format
class Kitti2015Format(DatasetFormat):
    
    def Name(self):
        return 'Kitti 2015 Stereo format'
    
    
    def FolderName(self):
        return 'kitti2015'
    
    
    def Website(self):
        return 'http://www.cvlibs.net/datasets/kitti/eval_scene_flow.php?benchmark=stereo'
    
    
    def ListDatasets(self, dataset_folder_path):
        return [dataset[:dataset.rfind('.')] for dataset
                in os.listdir(os.path.join(dataset_folder_path, 'image_2'))
                if os.path.isfile(os.path.join(dataset_folder_path, 'image_2', dataset))]
    
    
    def ListMethods(self, dataset_folder_path, dataset_name):
        methods = []
        folder_list = os.listdir(dataset_folder_path)
        for folder in folder_list:
            folder_path = os.path.join(dataset_folder_path, folder)
            
            # Check whether this is a folder that ends on _time and contains
            # a time file for the given dataset.
            if (os.path.isdir(folder_path) and
                folder.endswith('_time') and
                os.path.isfile(os.path.join(folder_path, dataset_name + '.txt'))):
                method_name = folder[:-len('_time')]
                
                # Check whether a corresponding disparity .png file also exists.
                if os.path.isfile(os.path.join(dataset_folder_path, method_name + '_disp_0', dataset_name + '.png')):
                    methods.append(method_name)
        
        return methods
    
    
    def CanConvertInputToFormat(self, dataset_format):
        return False
    
    
    def ConvertInputToFormat(self, dataset_format, dataset_name, in_path, out_path):
        raise NotImplementedError()


    def CanConvertOutputToFormat(self, dataset_format):
        return isinstance(dataset_format, dataset_format_middlebury2014.Middlebury2014Format)
    
    
    def ConvertOutputToFormat(self, dataset_format, method_name, dataset_name, in_path, out_path):
        # Convert to Middlebury2014Format.
        out_dataset_path = os.path.join(out_path, dataset_name)
        MakeDirsExistOk(out_dataset_path)
        
        in_disp_path = os.path.join(in_path, method_name + '_disp_0', dataset_name + '.png')
        out_pfm_path = os.path.join(out_dataset_path, 'disp0' + method_name + '.pfm')
        ConvertKitti2015PngToMiddlebury2014Pfm(in_disp_path, out_pfm_path)
        
        in_time_path = os.path.join(in_path, method_name + '_time', dataset_name + '.txt')
        out_time_path = os.path.join(out_dataset_path, 'time' + method_name + '.txt')
        shutil.copy2(in_time_path, out_time_path)
    