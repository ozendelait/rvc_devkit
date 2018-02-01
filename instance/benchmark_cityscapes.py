import math
import png
import shutil

from benchmark import *
from dataset_format_kitti2015 import *
from util import *
from util_stereo import *

import numpy as np
import scipy.misc as sp

join = os.path.join 

class Cityscapes(Benchmark):
    def Name(self):
        return "Cityscapes instance segmentation challenge"
    
    
    def Prefix(self):
        return "cityscapes_"
    
    
    def Website(self):
        return 'https://www.cityscapes-dataset.com/'
    
    
    def SupportsTrainingDataOnlySubmissions(self):
        return False
    
    
    def SupportsTrainingDataInFullSubmissions(self):
        return True
    
    
    def GetOptions(self, metadata_dict):
        return  # No options
    
    
    def DownloadAndUnpack(self, archive_dir_path, unpack_dir_path, metadata_dict):
        print('Cityscapes should be downloaded manually and unpacked in the folder temp_unpack_dir')
        # DownloadAndUnzipFile('https://www.cityscapes-dataset.com/login/', archive_dir_path, unpack_dir_path)
    
    
    def CanConvertOriginalToFormat(self, dataset_format):
        return isinstance(dataset_format, KITTI2015Format)

    def cityscapes_to_kitti(self,cs_instance,cs_semantic):
        instance = np.zeros(cs_instance.shape,dtype="int32")
        instance[np.where(cs_instance > 1000 )] = 1+cs_instance[np.where(cs_instance > 1000 )] % 1000
        kitti_instance = cs_semantic*256 + instance 
        return kitti_instance
        
    def ConvertOriginalToFormat(self, dataset_format, unpack_dir_path, metadata_dict, training_dir_path, test_dir_path):
        temp_image_dir = join(unpack_dir_path,'cityscapes','leftImg8bit_trainvaltest','leftImg8bit')
        temp_gt_dir    = join(unpack_dir_path,'cityscapes','gtFine_trainvaltest','gtFine')

        train_splits = ['train','val']
        test_splits  = ['test']

        # move the training data
        for split in train_splits:
            city_names = [city for city in os.listdir(join(temp_image_dir,split)) if os.path.isdir(join(temp_image_dir,split,city))]
            for city in city_names : 
                # read the image file names without the prefix
                filenames = ["_".join(f.split("_")[:3]) for f in os.listdir(join(temp_image_dir,split,city)) if os.path.isfile(join(temp_image_dir,split,city,f))]
                for image_file in filenames:
                    # copy image data
                    # shutil.move(join(temp_image_dir,split,city,image_file+'_leftImg8bit.png'),join(training_dir_path,'image_2',image_file+'.png'))
                    shutil.copy2(join(temp_image_dir,split,city,image_file+'_leftImg8bit.png'),join(training_dir_path,'image_2',self.Prefix()+image_file+'.png'))
                    # copy the semantic segmentation files
                    # shutil.move(join(temp_gt_dir,split,city,image_file+"_gtFine_labelIds.png"),join(training_dir_path,'semantic',image_file+".png"))
                    shutil.copy2(join(temp_gt_dir,split,city,image_file+"_gtFine_labelIds.png"),join(training_dir_path,'semantic',self.Prefix()+image_file+".png"))
                    # convert the instance files to kitti format
                    cs_instance = sp.imread(join(temp_gt_dir,split,city,image_file+"_gtFine_instanceIds.png"))
                    cs_semantic = sp.imread(join(temp_gt_dir,split,city,image_file+"_gtFine_labelIds.png"))
                    kitti_instance = self.cityscapes_to_kitti(cs_instance,cs_semantic)
                    sp.toimage(kitti_instance,high=np.max(kitti_instance), low=np.min(kitti_instance), mode='I').save(join(training_dir_path,'instance',self.Prefix()+image_file+".png"))

        # move the test data 
        for split in test_splits :
            city_names = [city for city in os.listdir(join(temp_image_dir,split)) if os.path.isdir(join(temp_image_dir,split,city))]
            for city in city_names : 
                # read the image file names without the prefix
                filenames = [f.split("_")[:3].join("_") for f in os.listdir(join(temp_image_dir,split,city)) if os.path.isfile(join(temp_image_dir,split,city,f))]
                for image_file in filenames:
                    # copy image data
                    shutil.copy2(join(temp_image_dir,split,city,image_file+'_leftImg8bit.png'),join(test_dir_path,'image_2',image_file+'.png'))
    
    def CanCreateSubmissionFromFormat(self, dataset_format):
        return isinstance(dataset_format, KITTI2015Format)
    
    
    def CreateSubmission(self, dataset_format, method, pack_dir_path,
                         metadata_dict, training_dir_path, training_datasets,
                         test_dir_path, test_datasets, archive_base_path):
        # FILE STRUCTURE:
        # your_algo_name/pred_list/FILENAME.txt
        # your_algo_name/pred_img/FILENAME_MASKID.png
        
        # Create the archive and clean up.
        archive_filename = ZipDirectory(archive_base_path, pack_dir_path)
        DeleteFolderContents(pack_dir_path)
        
        return archive_filename
    
