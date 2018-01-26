import math
import png
import shutil
import struct

from benchmark import *
from dataset_format_middlebury import *
from dataset_format_kitti2015 import *
from util import *
from util_flow import *


class Kitti2015(Benchmark):
    def Name(self):
        return "Kitti 2015 Optical Flow"
    
    
    def Prefix(self):
        return "Kitti2015_"
    
    
    def Website(self):
        return 'http://www.cvlibs.net/datasets/kitti/eval_scene_flow.php?benchmark=flow'
    
    
    def SupportsTrainingDataOnlySubmissions(self):
        return False
    
    
    def SupportsTrainingDataInFullSubmissions(self):
        return False
    
    
    def GetOptions(self, metadata_dict):
        return  # No options
    
    
    def DownloadAndUnpack(self, archive_dir_path, unpack_dir_path, metadata_dict):
        # Download input images (training + test) and ground truth
        #TODO: Do we also need to explicitly download the flow?
        DownloadAndUnzipFile('http://kitti.is.tue.mpg.de/kitti/data_scene_flow_multiview.zip', archive_dir_path, unpack_dir_path)
        
        # NOTE: Calibration files would be here:
        # http://kitti.is.tue.mpg.de/kitti/data_scene_flow_calib.zip
        
        # NOTE: Multi-view extension would be here:
        # http://kitti.is.tue.mpg.de/kitti/data_scene_flow_multiview.zip
    
    
    def CanConvertOriginalToFormat(self, dataset_format):
        return isinstance(dataset_format, MiddleburyFormat) or isinstance(dataset_format, Kitti2015Format)

    def ConvertToKittiFormat(self, unpack_dir_path, metadata_dict, training_dir_path, test_dir_path):
        # Convert the downloaded file to KITTI format
        # (i.e., just copy.)
        shutil.move(os.path.join(unpack_dir_path, 'training', 'image_2'),
                    training_dir_path)
        shutil.move(os.path.join(unpack_dir_path, 'training', 'flow_occ'),
                    training_dir_path)
        shutil.move(os.path.join(unpack_dir_path, 'testing', 'image_2'),
                    test_dir_path)

    def ConvertToKittiFormat(self, unpack_dir_path, metadata_dict, training_dir_path, test_dir_path):
        # Convert downloaded files to Middlebury format
        src_training_path = os.path.join(unpack_dir_path, 'training')
        src_testing_path = os.path.join(unpack_dir_path, 'testing')
        
        for folder_names in [(src_testing_path, test_dir_path),
                             (src_training_path, training_dir_path)]:
            input_folder_path = folder_names[0]

            image_path = os.path.join(input_folder_path, 'image_2')  # contains input images

            for image_name in os.listdir(image_2_path):
                dataset_name = image_name[:image_name.rfind('_')]  # remove file extension
                frameno = image_name[image_name.rfind('_')+1:image_name.rfind('.')]
                frameno =int(frameno)

                output_dataset_image_path = os.path.join(folder_names[1], 'images', self.Prefix() + dataset_name)
                MakeDirsExistOk(output_dataset_path)

                # Move image
                outname = 'frame_{0:04d}.png'.format(frameno)
                shutil.move(os.path.join(image_2_path, image_name),
                            os.path.join(output_dataset_path, outname)) 

            if folder_names[1] == training_dir_path:
                # Convert flow, too
                flow_path = os.path.join(input_folder_path, 'flow_occ')  # contains training flow.

                for image_name in os.listdir(flow_path):
                    dataset_name = image_name[:image_name.rfind('_')]  # remove file extension
                    frameno = image_name[image_name.rfind('_')+1:image_name.rfind('.')]
                    frameno =int(frameno)

                    output_dataset_flow_path = os.path.join(folder_names[1], 'flow', self.Prefix() + dataset_name)
                    MakeDirsExistOk(output_dataset_flow_path)

                    # Move flow
                    outname = 'frame_{0:04d}.flo'.format(frameno)
                    ConvertKittiPngToMiddleburyFlo(os.path.join(flow_path, image_name),
                                                   os.path.join(output_dataset_flow_path, outname))


           
            # Delete original folder
            shutil.rmtree(input_folder_path)
    
    
    def CanCreateSubmissionFromFormat(self, dataset_format):
        return isinstance(dataset_format, MiddleburyFormat) or isinstance(dataset_format, Kitti2015Format)
    
    
    def CreateSubmission(self, dataset_format, method, pack_dir_path,
                         metadata_dict, training_dir_path, training_datasets,
                         test_dir_path, test_datasets, archive_base_path):
        # Create output directory
        flow_out_path = os.path.join(pack_dir_path, 'flow')
        MakeDirsExistOk(flow_out_path)
        
        # Only test dataset submission is supported.
        for (benchmark_and_dataset_name, original_dataset_name) in test_datasets:
            if isinstance(dataset_format, Kitti2015Format):
                # Convert from KITTI (i.e., just copy to the right location and
                # remove dataset prefix.
                src_png_path = os.path.join(
                    test_dir_path, method + '_flow_occ', benchmark_and_dataset_name + '_10.png')
                dest_png_path = os.path.join(flow_out_path, original_dataset_name + '_10.png')
                shutils.copy2(src_png_path, dest_png_path)

            elif isinstance(dataset_format, MiddleburyFormat):
                # Convert from Middlebury directory layout
                src_flo_path = os.path.join(
                    test_dir_path, method + '_flow', benchmark_and_dataset_name,
                    'frame_0010.flo')
                
                dest_png_path = os.path.join(flow_out_path, original_dataset_name + '_10.png')
                ConvertMiddleburyFloToKittyPng(src_flo_path, dest_png_path)
       
        # Create the archive and clean up.
        archive_filename = ZipDirectory(archive_base_path, pack_dir_path)
        DeleteFolderContents(pack_dir_path)
        
        return archive_filename
    
