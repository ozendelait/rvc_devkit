from dataset_format import *
import dataset_format_middlebury  # Avoid issues with circular dependency using this import style
from util import *
from util_flow import *


# Kitti 2015 Stereo dataset format
class Kitti2015Format(DatasetFormat):
    
    def Name(self):
        return 'Kitti 2015 Flow format'
    
    
    def Identifier(self):
        return 'kitti2015'
    
    
    def Website(self):
        return 'http://www.cvlibs.net/datasets/kitti/eval_scene_flow.php?benchmark=flow'
    
    
    def ListDatasets(self, dataset_folder_path):
        return [dataset[:dataset.rfind('.')] for dataset
                in os.listdir(os.path.join(dataset_folder_path, 'image_2'))
                if os.path.isfile(os.path.join(dataset_folder_path, 'image_2', dataset))]
    
    
    def ListMethods(self, dataset_folder_path, dataset_name):
        methods = []
        folder_list = os.listdir(dataset_folder_path)
        for folder in folder_list:
            folder_path = os.path.join(dataset_folder_path, folder)

            # Check whether the corresponding flow file is in the given folder
            if (os.path.isdir(folder_path) and
                folder.endswith('_flow') and
                os.path.isfile(os.path.join(folder_path, dataset_name + '.png'))):
                method_name = folder[:-len('_flow')]
                methods.append(method_name)
       
        return methods
    
    
    def PrepareRunningMethod(self, method_name, dataset_folder_path, dataset_name):
        flow_dir_path = os.path.join(dataset_folder_path, method_name + '_flow')
        MakeDirsExistOk(flow_dir_path)
        # We do not have any timings -- time always has to be entered manually.
        return [dataset_folder_path, dataset_name, flow_dir_path]
    
    
    def CanConvertInputToFormat(self, dataset_format):
        return isinstance(dataset_format, dataset_format_middlebury.MiddleburyFormat)
    
    
    def ConvertInputToFormat(self, dataset_format, dataset_name, in_path, out_path):
        # TODO
        raise NotImplementedError()


    def CanConvertOutputToFormat(self, dataset_format):
        return isinstance(dataset_format, dataset_format_middlebury.MiddleburyFormat)
    
    
    def ConvertOutputToFormat(self, dataset_format, method_name, dataset_name, in_path, out_path):
        # TODO
        # Convert to Middlebury flow format.
        out_dataset_path = os.path.join(out_path, dataset_name)
        MakeDirsExistOk(out_dataset_path)

        in_disp_path = os.path.join(in_path, method_name + '_flow', dataset_name + '.png')
        out_pfm_path = os.path.join(out_dataset_path, 'disp0' + method_name + '.pfm')
        ConvertKitti2015PngToMiddlebury2014Pfm(in_disp_path, out_pfm_path)
