import shutil

from dataset_format import *
from util import *
from util_segmentation import *
join = os.path.join

# KITTI 2015 Stereo dataset format
class KITTI2015Format(DatasetFormat):
    
    def Name(self):
        return 'KITTI 2015 instance segmentation format'
    
    
    def Identifier(self):
        return 'kitti2015'
    
    
    def Website(self):
        return 'http://www.cvlibs.net/datasets/kitti/eval_semantics.php'
    
    
    def ListDatasets(self, dataset_folder_path):
        input_folder_path = join(dataset_folder_path, "image_2")
        datasets = [fname for fname
                    in os.listdir(input_folder_path)
                    if os.path.isfile(join(input_folder_path, fname))]
        return datasets

    
    def ListMethods(self, task_name, dataset_folder_path, dataset_name):
        if task_name == "semantic":
            return self.ListSemanticMethods(dataset_folder_path, dataset_name)

        if task_name == "instance":
            return self.ListInstanceMethods(dataset_folder_path, dataset_name)


    def ListSemanticMethods(self, dataset_folder_path, dataset_name):
        # find all algorithm directories with semantic segmentation results
        algo_dirs = [dd for dd in os.listdir(dataset_folder_path) if dd.startswith("algo_")
                     and dd.endswith("_semantic") and os.path.isdir(os.path.join(dataset_folder_path, dd))]

        methods = []
        # check if result file for specific dataset image exists
        for algo_dir in algo_dirs:
            if os.path.isfile(os.path.join(dataset_folder_path, algo_dir, dataset_name)):
                algo_name = "_".join(algo_dir.split("_")[1:-1])
                methods.append(algo_name)

        return methods


    def ListInstanceMethods(self, dataset_folder_path, dataset_name):
        # find all algorithm directories with instance segmentation results
        algo_dirs = [dd for dd in os.listdir(dataset_folder_path) if dd.startswith("algo_")
                     and dd.endswith("_instance") and os.path.isdir(os.path.join(dataset_folder_path, dd))]

        methods = []
        # check if result file for specific dataset image exists
        for algo_dir in algo_dirs:
            if os.path.isfile(
                    os.path.join(dataset_folder_path, algo_dir, "pred_list", dataset_name.replace(".png", ".txt").replace(".jpg",".txt"))):
                algo_name = "_".join(algo_dir.split("_")[1:-1])
                methods.append(algo_name)

        return methods


    def PrepareRunningMethod(self, method_name, dataset_folder_path, dataset_name,test=False):
        image_dir = join(dataset_folder_path, dataset_name, 'training', 'image_2')
        semantic_instance_dir = join(dataset_folder_path, dataset_name, 'training', 'instance')

        image_path_list = [join(semantic_instance_dir, f) for f in os.listdir(image_dir) if os.path.isfile(join(image_dir, f))]
        semantic_instance_path_list = [join(semantic_instance_dir, f) for f in os.listdir(semantic_instance_dir) if os.path.isfile(join(semantic_instance_dir, f))]

        return image_path_list, semantic_instance_path_list
