import math
import png
import shutil
import struct

from benchmark import *
from dataset_format_middlebury import *
from dataset_format_kitti2015 import *
from util import *
from util_flow import *

import platform
import subprocess
import os,stat # To change permissions for bundler


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
   
    
    def CanConvertOriginalToFormat(self, dataset_format):
        return isinstance(dataset_format, MiddleburyFormat) or isinstance(dataset_format, Kitti2015Format)

    def ConvertToKittiFormat(self, unpack_dir_path, metadata_dict, training_dir_path, test_dir_path):

        def ConvertSequenceToKitti(seq_dir_in, seq_dir_out, seq, pas, ext_in, ext_out):
            # Convert all files from a given input directory (e.g. training/clean/alley_1)
            # to a given output directory.
            prefix_out = self.Prefix() + pas + '_' + seq
            files = [f for f in os.listdir(seq_dir_in) if f.endswith(ext_in)]
            MakeDirsExistOk(seq_dir_out)

            for f in files:
                frameno = f[f.rfind('_')+1:f.rfind('.')]
                frameno = int(frameno)

                # KITTI starts at 0, Sintel starts at 1.
                frameno = frameno-1

                file_out = os.path.join(seq_dir_out, prefix_out + '_{0:02d}'.format(frameno))

                if ext_in == '.png' and ext_out == '.png':
                    shutil.move(os.path.join(seq_dir_in, f),
                                file_out + ext_out)
                elif ext_in == '.flo' and ext_out == '.png':
                    ConvertMiddleburyFloToKittiPng(os.path.join(seq_dir_in, f),
                                                   file_out + ext_out)


        # Convert the downloaded files to KITTI format
        for (testtrain, testtrain_dir) in [('training', training_dir_path),
                                           ('test', test_dir_path)]:
            # For testing and training, copy images
            for pas in ['clean', 'final']:
                basedir_in = os.path.join(unpack_dir_path, testtrain, pas)
                sequences = [f for f in sorted(os.listdir(basedir_in))]

                for s in sequences:
                    ConvertSequenceToKitti(os.path.join(basedir_in, s),
                                           os.path.join(testtrain_dir, 'image_2'),
                                           s, pas, '.png', '.png')

            # Copy flow
            if testtrain == 'training':
                for pas in ['clean', 'final']:
                    basedir_flow_in = os.path.join(unpack_dir_path, testtrain, 'flow')
                    sequences = [f for f in sorted(os.listdir(basedir_flow_in))]

                    for s in sequences:
                        ConvertSequenceToKitti(os.path.join(basedir_flow_in, s),
                                            os.path.join(testtrain_dir, 'flow_occ'),
                                            s, pas, '.flo', '.png')


        # Delete original folder
        shutil.rmtree(os.path.join(unpack_dir_path, 'training'))
        shutil.rmtree(os.path.join(unpack_dir_path, 'test'))


    def ConvertToMiddleburyFormat(self, unpack_dir_path, metadata_dict, training_dir_path, test_dir_path):
        # Convert the downloaded files to Middlebury format
        for (testtrain, testtrain_dir) in [('training', training_dir_path),
                                           ('test', test_dir_path)]:
            # For testing and training, copy images
            for pas in ['clean', 'final']:
                for seq in os.listdir(os.path.join(unpack_dir_path, testtrain, pas)):
                    dir_in = os.path.join(unpack_dir_path, testtrain, pas, seq)
                    dir_out = os.path.join(testtrain_dir, 'images', self.Prefix() + pas + '_' + seq)
                    MakeDirsExistOk(dir_out)

                    for f in os.listdir(dir_in):
                        shutil.move(os.path.join(dir_in, f), os.path.join(dir_out, f))

            if testtrain == 'training':
                for pas in ['clean', 'final']:
                    for seq in os.listdir(os.path.join(unpack_dir_path, testtrain, pas)):
                        dir_in = os.path.join(unpack_dir_path, testtrain, 'flow', seq)
                        dir_out = os.path.join(testtrain_dir, 'flow', self.Prefix() + pas + '_' + seq)
                        MakeDirsExistOk(dir_out)

                        for f in os.listdir(dir_in):
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

        # In any case, we need to save the bundler.
        bundler_path_in = os.path.join(unpack_dir_path, 'bundler')
        training_path_parent = training_dir_path[:training_dir_path.rstrip('/').rfind('/')]
        bundler_path_out = os.path.join(training_path_parent, 'bundler')
        if os.path.isdir(bundler_path_out):
            shutil.rmtree(bundler_path_out)
        shutil.copytree(bundler_path_in, bundler_path_out)

    def CanCreateSubmissionFromFormat(self, dataset_format):
        return isinstance(dataset_format, MiddleburyFormat) or isinstance(dataset_format, Kitti2015Format)
    
    
    def CreateSubmission(self, dataset_format, method, pack_dir_path,
                         metadata_dict, training_dir_path, training_datasets,
                         test_dir_path, test_datasets, archive_base_path):

        import sys
        sys.stdout.write('\nCreating submission for Sintel...\n')
        sys.stdout.flush()
        
        # Create output directory
        flow_out_path = os.path.join(pack_dir_path, 'flow')
        MakeDirsExistOk(flow_out_path)

        # Only test dataset submission is supported.
        for (benchmark_and_dataset_name, original_dataset_name) in test_datasets:
            sys.stdout.write('Creating submission for dataset {} -- {}'.format(benchmark_and_dataset_name, original_dataset_name))
            sys.stdout.flush()

            # Format of benchmark_and_dataset_name is Sintel_pas_seq.
            parts = original_dataset_name.split('_')
            pas = parts[0]
            seq = '_'.join(parts[1:])
            # pas, seq = original_dataset_name.split('_')[:2]

            flow_dataset_path = os.path.join(flow_out_path, pas, seq)
            MakeDirsExistOk(flow_dataset_path)

            if isinstance(dataset_format, Kitti2015Format):
                dir_in = os.path.join(test_dir_path,
                                      method + '_flow_occ')

                files = [f for f in os.listdir(dir_in)
                         if f.endswith('.png') and
                         f.startswith(benchmark_and_dataset_name)]

                for f in files:
                    sys.stdout.write('.')
                    sys.stdout.flush()
                    seq, frameno, ext = ParseFilenameKitti(f)
                    outfile = os.path.join(flow_dataset_path, 'frame_{0:04d}.flo'.format(frameno+1))
                    ConvertKittiPngToMiddleburyFlo(os.path.join(dir_in, f), outfile)

            elif isinstance(dataset_format, MiddleburyFormat):
                dir_in = os.path.join(test_dir_path, method+'_flow', benchmark_and_dataset_name)

                for f in [f for f in os.listdir(dir_in) if f.endswith('.flo')]:
                    sys.stdout.write('.')
                    sys.stdout.flush()
                    shutil.copy2(os.path.join(dir_in, f), os.path.join(flow_dataset_path, f))

            
            sys.stdout.write(' Done.\n')
            sys.stdout.flush()



        training_path_parent = training_dir_path[:training_dir_path.rstrip('/').rfind('/')]
        bundler_path = os.path.join(training_path_parent, 'bundler')

        # 
        if platform.system() == 'Linux':
            bundler_bin = os.path.join(bundler_path, 'linux-x64', 'bundler')
            os.chmod(bundler_bin, stat.S_IXUSR)
        elif platform.system() == 'Darwin':
            bundler_bin = os.path.join(bundler_path, 'osx', 'bundler')
            os.chmod(bundler_bin, stat.S_IXUSR)
        elif platform.system() == 'Windows':
            bundler_bin = os.path.join(bundler_path, 'win', 'bundler.exe')
        else:
            print('== Warning: Unsupported OS for Sintel bundler. ==')


        archive_filename = archive_base_path + '.lzma'
        cmd = [bundler_bin,
               os.path.join(flow_out_path, 'clean'),
               os.path.join(flow_out_path, 'final'),
               archive_filename]


        sys.stdout.write(' Calling bundler as:\n')
        sys.stdout.write(repr(cmd))
        sys.stdout.write('\n')
        sys.stdout.flush()

        subprocess.call(cmd)

        sys.stdout.write('Done.\n')
        sys.stdout.flush()

        return archive_filename
    
