import math
import png
import shutil
import struct

from benchmark import *
from dataset_format_middlebury import *
from dataset_format_kitti2015 import *
from util import *
from util_flow import *


class Sintel(Benchmark):
    def Name(self):
        return "Sintel Optical Flow"
    
    
    def Prefix(self):
        return "Sintel_"
    
    
    def Website(self):
        return 'http://www.mpi-sintel.de'
    
    
    def SupportsTrainingDataOnlySubmissions(self):
        return False
    
    
    def SupportsTrainingDataInFullSubmissions(self):
        return False
    
    
    def GetOptions(self, metadata_dict):
        return  # No options
    
    
    def DownloadAndUnpack(self, archive_dir_path, unpack_dir_path, metadata_dict):
        # Download input images (training + test) and ground truth
        DownloadAndUnzipFile('http://files.is.tue.mpg.de/sintel/MPI-Sintel-complete.zip', archive_dir_path, unpack_dir_path)
        
        # NOTE: Calibration files would be here:
        # http://kitti.is.tue.mpg.de/kitti/data_scene_flow_calib.zip
        
        # NOTE: Multi-view extension would be here:
        # http://kitti.is.tue.mpg.de/kitti/data_scene_flow_multiview.zip
    
    
    def CanConvertOriginalToFormat(self, dataset_format):
        return isinstance(dataset_format, MiddleburyFormat) or isinstance(dataset_format, Kitti2015Format)

    def ConvertToKittiFormat(self, unpack_dir_path, metadata_dict, training_dir_path, test_dir_path):

        def ConvertSequenceToKitti(seq_dir_in, seq_dir_out, seq, pas, ext_in, ext_out):
            # Convert all files from a given input directory (e.g. training/clean/alley_1)
            # to a given output directory.
            prefix_out = self.Prefix() + pas + '_' + seq
            files = [f for f in os.listdir(seq_dir_in) if f.endswith(ext_in)]

            for f in files:
                frameno = f[f.rfind('_')+1:f.rfind('.')]
                frameno = int(frameno)

                file_out = os.path.join(seq_dir_out, prefix_out + '_{0:02d}'.format(frameno))

                if ext_in == '.png' and ext_out == '.png':
                    shutil.move(os.path.join(seq_dir_in, f),
                                file_out + ext_out)
                elif ext_in == '.flo' and ext_out == '.png':
                    ConvertMiddleburyFloToKittiPng(os.path.join(seq_dir_in, f),
                                                   file_out + ext_out)


        # Convert the downloaded files to KITTI format
        for (testtrain, testtrain_dir) in [('training', training_dir_path),
                                           ('testing', test_dir_path)]:
            # For testing and training, copy images
            for pas in ['clean', 'final']:
                basedir_in = os.path.join(unpack_dir_path, testtrain_dir, pas)
                sequences = [f for f in sorted(os.listdir(basedir_in))]

                for s in sequences:
                    ConvertSequenceToKitti(os.path.join(basedir_in, s),
                                           os.path.join(testtrain_dir, 'image_2'),
                                           s, pas, '.png', '.png')

            # Copy flow
            if testtrain == 'training':
                for pas in ['clean', 'final']:
                    basedir_in = os.path.join(unpack_dir_path, testtrain_dir, pas)
                    basedir_flow = os.path.join(unpack_dir_path, testtrain_dir, 'flow')
                    sequences = [f for f in sorted(os.listdir(basedir_in))]

                    for s in sequences:
                        ConvertSequenceToKitti(os.path.join(basedir_flow, s),
                                            os.path.join(testtrain_dir, 'flow_occ'),
                                            s, pas, '.flo', '.png')


        # Delete original folder
        shutil.rmtree(os.path.join(unpack_dir_path, 'training'))
        shutil.rmtree(os.path.join(unpack_dir_path, 'test'))


    def ConvertToMiddleburyFormat(self, unpack_dir_path, metadata_dict, training_dir_path, test_dir_path):
        # Convert the downloaded files to Middlebury format
        for (testtrain, testtrain_dir) in [('training', training_dir_path),
                                           ('testing', test_dir_path)]:
            # For testing and training, copy images
            for pas in ['clean', 'final']:
                for seq in os.listdir(os.path.join(unpack_dir_path, testtrain, pas)):
                    dir_in = os.path.join(unpack_dir_path, testtrain, pas, seq)
                    dir_out = os.path.join(training_dir_path, 'images', self.Prefix() + pas + '_' + seq)
                    MakeDirsExistOk(dir_out)

                    for f in os.listidr(dir_in):
                        shutil.move(os.path.join(dir_in, f), os.path.join(dir_out, f))

            if testtrain == 'training':
                for pas in ['clean', 'final']:
                    for seq in os.listdir(os.path.join(unpack_dir_path, testtrain, pas)):
                        dir_in = os.path.join(unpack_dir_path, testtrain, 'flow', seq)
                        dir_out = os.path.join(training_dir_path, 'flow', self.Prefix() + pas + '_' + seq)
                        MakeDirsExistOk(dir_out)

                        for f in os.listidr(dir_in):
                            shutil.move(os.path.join(dir_in, f), os.path.join(dir_out, f))

        # Delete original folder
        shutil.rmtree(os.path.join(unpack_dir_path, 'training'))
        shutil.rmtree(os.path.join(unpack_dir_path, 'test'))


    def ConvertOriginalToFormat(self, dataset_format, unpack_dir_path, metadata_dict, training_dir_path, test_dir_path):
        if isinstance(dataset_format, MiddleburyFormat):
            self.ConvertToMiddleburyFormat(
                unpack_dir_path,
                metadata_dict,
                training_dir_path,
                test_dir_path)

        elif isinstance(dataset_format, Kitti2015Format):
            self.ConvertToKittiFormat(
                unpack_dir_path,
                metadata_dict,
                training_dir_path,
                test_dir_path)
 
    
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
    
