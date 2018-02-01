import shutil

from dataset_format import *
from util import *
from util_stereo import *
join = os.path.join

# KITTI 2015 Stereo dataset format
class KITTI2015Format(DatasetFormat):
    
    def Name(self):
        return 'KITTI 2015 instance semgnetation format'
    
    
    def Identifier(self):
        return 'kitti2015'
    
    
    def Website(self):
        return 'http://kitti.is.tue.mpg.de/kitti/'
    
    
    def ListDatasets(self, dataset_folder_path):
        return [dataset for dataset
                in os.listdir(dataset_folder_path)
                if os.path.isdir(join(dataset_folder_path, dataset))]
    
    
    def ListMethods(self, dataset_folder_path, dataset_name):
        result_file_scheme = [('', '.txt')]
        
        contains_all_result_files = lambda path, method : (
            all([os.path.isfile(join(path, prefix + method + suffix))
                for (prefix, suffix) in result_file_scheme]))
        
        dataset_path = join(dataset_folder_path, dataset_name)
        first_prefix = result_file_scheme[0][0]
        first_suffix = result_file_scheme[0][1]
        
        method_list = []
        
        for filename in os.listdir(dataset_path):
            if filename.startswith(first_prefix) and filename.endswith(first_suffix):
                method = filename[len(first_prefix):-len(first_suffix)]  # strip prefix and suffix
                if contains_all_result_files(dataset_path, method):
                    method_list.append(method)
        
        return method_list
    
    
    def PrepareRunningMethod(self, method_name, dataset_folder_path, dataset_name,test=False):
        image_dir = join(dataset_folder_path, dataset_name, 'training' ,'image_2')
        semantic_instance_dir = join(dataset_folder_path, dataset_name, 'training' ,'instance')
        image_path_list = [join(semantic_instance_dir,f) for f in os.listdir(image_dir) if os.path.isfile(join(image_dir,f))]
        semantic_instance_path_list = [join(semantic_instance_dir,f) for f in os.listdir(semantic_instance_dir) if os.path.isfile(join(semantic_instance_dir,f))]

        return image_path_list, semantic_instance_path_list
