import math
import png
import shutil
import struct

from benchmark import *
from dataset_format_kitti2015 import *
from util import *
from util_stereo import *
join = os.path.join


class KITTI2015(Benchmark):
    def Name(self):
        return "KITTI 2015 instance semgentation"
    
    
    def Prefix(self):
        return "kitti2015_"
    
    
    def Website(self):
        return 'http://www.cvlibs.net/datasets/kitti/'
    
    
    def SupportsTrainingDataOnlySubmissions(self):
        return False
    
    
    def SupportsTrainingDataInFullSubmissions(self):
        return False
    
    
    def GetOptions(self, metadata_dict):
        return  # No options
    
    
    def DownloadAndUnpack(self, archive_dir_path, unpack_dir_path, metadata_dict):
        # Download input images (training + test) and ground truth
        print('KITTI 2015 should be downloaded manually and unpacked in the folder temp_unpack_dir')
        # DownloadAndUnzipFile('http://kitti.is.tue.mpg.de/kitti/data_scene_flow.zip', archive_dir_path, unpack_dir_path)
        
    
    
    def CanConvertOriginalToFormat(self, dataset_format):
        return isinstance(dataset_format, KITTI2015Format)
    
    
    def ConvertOriginalToFormat(self, dataset_format, unpack_dir_path, metadata_dict, training_dir_path, test_dir_path):

        # Move datasets into common folder
        src_dir_path = join(unpack_dir_path, 'kitti2015')
        
        for (mode, dest_path) in [('training', training_dir_path), ('testing', test_dir_path)]: #
            src_mode_path = join(src_dir_path, mode )
            for folder in [f for f in ['image_2','instance','semantic'] if os.path.isdir(join(src_mode_path,f)) ]:
                src_folder_path = join(src_mode_path,folder)
                for filename in [f for f in os.listdir(src_folder_path) if os.path.isfile(join(src_folder_path,f))] :
                    shutil.copy2(join(src_folder_path, filename),
                              join(dest_path,folder, self.Prefix() + filename))
        
        # shutil.rmtree(src_dir_path)

    
    def CanCreateSubmissionFromFormat(self, dataset_format):
        return isinstance(dataset_format, Middlebury2014Format)
    
    
    def CreateSubmission(self, dataset_format, method, pack_dir_path,
                         metadata_dict, training_dir_path, training_datasets,
                         test_dir_path, test_datasets, archive_base_path):

        # Create the archive and clean up.
        archive_filename = ZipDirectory(archive_base_path, pack_dir_path)
        DeleteFolderContents(pack_dir_path)
        
        return archive_filename
    
