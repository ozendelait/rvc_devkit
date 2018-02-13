import math
import png
import shutil
import struct

from benchmark import *
from dataset_format_middlebury import *
from dataset_format_kitti2015 import *
from util import *
from util_flow import *


class Middlebury(Benchmark):
    def Name(self):
        return "Middlebury Optical Flow"
    
    
    def Prefix(self):
        return "Middlebury_"
    
    
    def Website(self):
        return 'http://vision.middlebury.edu/flow'
    
    
    def SupportsTrainingDataOnlySubmissions(self):
        return False
    
    
    def SupportsTrainingDataInFullSubmissions(self):
        return False
    
    
    def GetOptions(self, metadata_dict):
        return  # No options
    
    
    def DownloadAndUnpack(self, archive_dir_path, unpack_dir_path, metadata_dict):
        # Download input images (training + test) and ground truth

        DownloadAndUnzipFile('http://vision.middlebury.edu/flow/data/comp/zip/eval-color-allframes.zip', archive_dir_path, unpack_dir_path)
        DownloadAndUnzipFile('http://vision.middlebury.edu/flow/data/comp/zip/other-color-allframes.zip', archive_dir_path, unpack_dir_path)
        DownloadAndUnzipFile('http://vision.middlebury.edu/flow/data/comp/zip/other-gt-flow.zip', archive_dir_path, unpack_dir_path)
   
        # Format:
        # Test: eval-data/SEQUENCE/frameXX.png
        # Training: other-data/SEQUENCE/frameXX.png
        # GT Flow: other-gt-flow/SEQUENCE/frame10.flo
    
    def CanConvertOriginalToFormat(self, dataset_format):
        return isinstance(dataset_format, MiddleburyFormat) or isinstance(dataset_format, Kitti2015Format)

    def ConvertToKittiFormat(self, unpack_dir_path, metadata_dict, training_dir_path, test_dir_path):

        def ConvertSequenceToKitti(seq_dir_in, seq_dir_out, seq, ext_in, ext_out):
            # Convert all files from a given input directory (e.g. other-data/sequence)
            # to a given output directory.
            prefix_out = self.Prefix() + seq
            files = [f for f in os.listdir(seq_dir_in) if f.endswith(ext_in)]
            MakeDirsExistOk(seq_dir_out)

            for f in files:
                frameno = f[:f.rfind('.')][-2:]
                frameno = int(frameno)

                file_out = os.path.join(seq_dir_out, prefix_out + '_{0:02d}'.format(frameno))

                if ext_in == '.png' and ext_out == '.png':
                    shutil.move(os.path.join(seq_dir_in, f),
                                file_out + ext_out)
                elif ext_in == '.flo' and ext_out == '.png':
                    ConvertMiddleburyFloToKittiPng(os.path.join(seq_dir_in, f),
                                                   file_out + ext_out)


        # Convert the downloaded images to KITTI format
        for (testtrain, testtrain_dir) in [('other-data', training_dir_path),
                                           ('eval-data', test_dir_path)]:
            # For testing and training, copy images
            basedir_in = os.path.join(unpack_dir_path, testtrain)
            sequences = [f for f in sorted(os.listdir(basedir_in))]

            for s in sequences:
                ConvertSequenceToKitti(os.path.join(basedir_in, s),
                                        os.path.join(testtrain_dir, 'image_2'),
                                        s, '.png', '.png')

        # Convert the downloaded flow fields to KITTI format
        for (testtrain, testtrain_dir) in [('other-gt-flow', training_dir_path),]:
            # Copy flow
            basedir_flow_in = os.path.join(unpack_dir_path, testtrain)
            sequences = [f for f in sorted(os.listdir(basedir_flow_in))]

            for s in sequences:
                ConvertSequenceToKitti(os.path.join(basedir_flow_in, s),
                                    os.path.join(testtrain_dir, 'flow_occ'),
                                    s, '.flo', '.png')


        # Delete original folder
        shutil.rmtree(os.path.join(unpack_dir_path, 'other-data'))
        shutil.rmtree(os.path.join(unpack_dir_path, 'other-gt-flow'))
        shutil.rmtree(os.path.join(unpack_dir_path, 'eval-data'))


    def ConvertToMiddleburyFormat(self, unpack_dir_path, metadata_dict, training_dir_path, test_dir_path):
        # Convert the downloaded files to Middlebury format
        for (testtrain, testtrain_dir) in [('other-data', training_dir_path),
                                           ('eval-data', test_dir_path)]:
            # For testing and training, copy images
            for seq in os.listdir(os.path.join(unpack_dir_path, testtrain)):
                dir_in = os.path.join(unpack_dir_path, testtrain, seq)
                dir_out = os.path.join(testtrain_dir, 'images', self.Prefix() + seq)
                MakeDirsExistOk(dir_out)

                for f in os.listdir(dir_in):
                    frameno = f[:f.rfind('.')][-2:]
                    frameno = int(frameno)
                    shutil.move(os.path.join(dir_in, f),
                                 os.path.join(dir_out, 'frame_{0:04d}.png'.format(frameno)))

        for (testtrain, testtrain_dir) in [('other-gt-flow', training_dir_path),]:
            for seq in os.listdir(os.path.join(unpack_dir_path, testtrain)):
                dir_in = os.path.join(unpack_dir_path, testtrain, seq)
                dir_out = os.path.join(testtrain_dir, 'flow', self.Prefix() + seq)
                MakeDirsExistOk(dir_out)

                for f in os.listdir(dir_in):
                    frameno = f[:f.rfind('.')][-2:]
                    frameno = int(frameno)
                    shutil.move(os.path.join(dir_in, f),
                                 os.path.join(dir_out, 'frame_{0:04d}.flo'.format(frameno)))


        # Delete original folder
        shutil.rmtree(os.path.join(unpack_dir_path, 'other-data'))
        shutil.rmtree(os.path.join(unpack_dir_path, 'other-gt-flow'))
        shutil.rmtree(os.path.join(unpack_dir_path, 'eval-data'))


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

        # Output is flow10.flo, not frame_0010.flo!

        # Only test dataset submission is supported.
        for (benchmark_and_dataset_name, original_dataset_name) in test_datasets:
            seq = original_dataset_name

            flow_dataset_path = os.path.join(pack_dir_path, 'middlebury', seq)
            MakeDirsExistOk(flow_dataset_path)

            if isinstance(dataset_format, Kitti2015Format):
                dir_in = os.path.join(test_dir_path,
                                      method + '_flow_occ')

                files = [f for f in os.listdir(dir_in)
                         if f.endswith('.png') and
                         f.startswith(benchmark_and_dataset_name)]

                for f in files:
                    frameno = f[f.rfind('_')+1:f.rfind('.')]
                    frameno = int(frameno)
                    outfile = os.path.join(flow_dataset_path, 'flow{0:02d}.flo'.format(frameno))
                    ConvertKittiPngToMiddleburyFlo(os.path.join(dir_in, f), outfile)

            elif isinstance(dataset_format, MiddleburyFormat):
                dir_in = os.path.join(test_dir_path, method+'_flow', benchmark_and_dataset_name)

                for f in [f for f in os.listdir(dir_in) if f.endswith('.flo')]:
                    frameno = f[f.rfind('_')+1:f.rfind('.')]
                    frameno = int(frameno)

                    shutil.copy2(os.path.join(dir_in, f),
                                 os.path.join(flow_dataset_path, 'flow{0:02d}'.format(frameno)))

        # Create the archive and clean up.
        archive_filename = ZipDirectory(archive_base_path,
                                        os.path.join(pack_dir_path, 'middlebury'))

        DeleteFolderContents(pack_dir_path)
        return archive_filename
    
