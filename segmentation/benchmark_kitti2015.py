import math
import os.path as op
import png
import shutil
import struct

from benchmark import *
from dataset_format_kitti2015 import *
from util import *
from util_segmentation import *


class KITTI2015(Benchmark):
    def Name(self):
        return 'KITTI 2015 instance semgentation challenge'
    
    
    def Prefix(self):
        return 'Kitti2015_'
    
    
    def Website(self):
        return 'http://www.cvlibs.net/datasets/kitti/'
    
    
    def SupportsTrainingDataOnlySubmissions(self):
        return False
    
    
    def SupportsTrainingDataInFullSubmissions(self):
        return False
    
    
    def GetOptions(self, metadata_dict):
        return  # No options
    
    
    def DownloadAndUnpack(self, archive_dir_path, unpack_dir_path, metadata_dict):
        # Download input images and ground truth segmentation (temporary location, will be moved to cvlibs)
        DownloadAndUnzipFile('http://hci-benchmark.org/media/downloads/kitti2015.zip',
                             archive_dir_path, op.join(unpack_dir_path))

    
    def CanConvertOriginalToFormat(self, dataset_format):
        return isinstance(dataset_format, KITTI2015Format)
    
    
    def ConvertOriginalToFormat(self, dataset_format, unpack_dir_path, metadata_dict, training_dir_path, test_dir_path):
        # Move datasets into common folder
        src_dir_path = op.join(unpack_dir_path, 'kitti2015', 'segmentation')
        
        for (mode, dest_path) in [('training', training_dir_path), ('testing', test_dir_path)]:
            src_mode_path = op.join(src_dir_path, mode)

            for folder in [f for f in ['image_2', 'instance', 'semantic'] if op.isdir(op.join(src_mode_path, f))]:
                src_folder_path = op.join(src_mode_path, folder)

                for filename in [f for f in os.listdir(src_folder_path) if op.isfile(op.join(src_folder_path, f))]:
                    shutil.move(op.join(src_folder_path, filename),
                                op.join(dest_path, folder, self.Prefix() + filename))
        
        shutil.rmtree(src_dir_path)

    
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