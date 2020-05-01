import math
import png
import shutil
import struct
import os
import array
import numpy as np
import scipy.io

from benchmark import *
from dataset_format_middlebury import *
from dataset_format_kitti2015 import *
from util import *
from util_flow import *



class VIPER(Benchmark):
    def __init__(self):
        self.archives_imgjpg_train = {
        '00-77_0':'1-O7vWiMa3mDNFXUoYxE3vkKZQpiDXUCf',
        '00-77_1':'1alD_fZja9qD7PUnk4AkD6l-jBhlCnzKr',
        }
        self.archives_flow_train = {
        '00-09_0':'1rXF2FuCTBrGymo3UXT2KnSyJ8OXO_Y_y',
        '10-19_0':'1HbyFrvZBNdPN7GxvKN11gFwrQHhRE94m',
        '20-29_0':'1xB9Vg5Jp8-XHvjEaFKpjzQXpoERUoTZB',
        '30-39_0':'1vZ83ji8woRjoBPGwQciRsRTSZq3lhqyq',
        '40-49_0':'1-DA6SFtJjEtaAAfu4yi1yHU4mIkf2lyH',
        '50-59_0':'1RsY8yaFlNNcP49wyZX2UI34MZx3va7EK',
        '60-69_0':'19vKpozdNFZPNK19OocEXtx8awcpSoRU7',
        '70-77_0':'1r1wBC2asa-E4E7U59A2Dwhetz8rV_hr-',
        }
        self.archives_imgjpg_val = {
        '00-47_0':'1951O6Eu-VuMHaL1vJ9V35njcj30GjPiN',
        '00-47_1':'1OqEjlrx97ThCMlQePEZPSBjqhRqPwOEd',
        }
        self.archives_flow_val = {
        
        }
        self.archives_imgjpg_test = {
        '00-60_0':'1KYSsgv-hp5BGU0EOfvX3gajr00wwSmFc', 
        '00_60_1':'1D-WbX5TOTuzwaqnJmPoCVc0Owa0y-Buk', 
        }


    def Name(self):
        return "VIPER Optical Flow"
    
    
    def Prefix(self):
        return "VIPER_"
    
    
    def Website(self):
        return 'https://playing-for-benchmarks.org/leaderboards/flow_2d/'
    
    
    def SupportsTrainingDataOnlySubmissions(self):
        return False
    
    
    def SupportsTrainingDataInFullSubmissions(self):
        return False
    
    
    def GetOptions(self, metadata_dict):
        return  # No options
    
    
    def DownloadAndUnpack(self, archive_dir_path, unpack_dir_path, metadata_dict):

        archives_to_download = ['archives_imgjpg_train', 'archives_flow_train', 'archives_imgjpg_test']

        for archive in archives_to_download:
            archive_dict = getattr(self, archive)
            for archive_id, gdrive_id in archive_dict.items():
                archive_path = os.path.join(archive_dir_path, archive[9:] + '_' + archive_id + '.zip')
                if not os.path.exists(archive_path):
                    DownloadFileFromGDrive(gdrive_id, archive_path)
                    pass
                if os.path.exists(archive_path):
                    UnzipFile(archive_path, unpack_dir_path, overwrite=False)
                    pass
                pass
            pass
        pass
    
    def CanConvertOriginalToFormat(self, dataset_format):
        return isinstance(dataset_format, MiddleburyFormat)# or isinstance(dataset_format, Kitti2015Format)

    def ConvertToKittiFormat(self, unpack_dir_path, metadata_dict, training_dir_path, test_dir_path):
        # Convert downloaded files to Middlebury format
        src_train_path = os.path.join(unpack_dir_path, 'train')
        src_test_path  = os.path.join(unpack_dir_path, 'test')

        # convert images
        for subset_src_dir, subset_dst_dir in [(src_train_path, training_dir_path), (src_test_path, test_dir_path)]:
            img_src_dir = os.path.join(subset_src_dir, 'img')
            img_dst_dir = os.path.join(subset_dst_dir, 'image_2')

            sequences = [d for d in os.listdir(img_src_dir) if os.path.isdir(os.path.join(img_src_dir, d))]
            for seq in sequences:
                seq_src_dir = os.path.join(img_src_dir, seq)
                seq_dst_dir = os.path.join(img_dst_dir)

                MakeDirsExistOk(seq_dst_dir)

                images = [f for f in os.listdir(seq_src_dir) if f.endswith('.jpg') or f.endswith('.png')]
                for img in images:
                    frame = int(img[4:-4])
                    shutil.move(os.path.join(seq_src_dir, f), os.path.join(seq_dst_dir, '%s_%04d.%s' % (seq, frame, img[-3:])))
                    pass
                pass

            shutil.rmtree(subset_src_dir)
            pass

        # convert flow
        flow_src_dir = os.path.join(src_train_path, 'flow')
        flow_dst_dir = os.path.join(training_dir_path, 'flow_occ')

        sequences = [d for d in os.listdir(flow_src_dir) if os.path.isdir(os.path.join(flow_src_dir, d))]
        for seq in sequences:
            seq_src_dir = os.path.join(flow_src_dir, seq)
            seq_dst_dir = os.path.join(flow_dst_dir)

            MakeDirsExistOk(seq_dst_dir)

            flows = [f for f in os.listdir(seq_src_dir) if f.endswith('.npz')]            
            for flow in flows:
                frame = int(flow[4:-7])
                flow_src_path = os.path.join(seq_src_dir, flow)
                flow_dst_path = os.path.join(seq_dst_dir, '%s_%04d.png' % (seq, frame))
                
                d   = np.load(flow_src_path)
                h,w = d['u'].shape[:2]
                u   = array.array('f', np.asarray(d['u'].astype(np.float32)))
                v   = array.array('f', np.asarray(d['v'].astype(np.float32)))
                WriteKittiPngFile(flow_dst_path, w, h, u, v)
                pass

            shutil.rmtree(flow_src_dir)
            pass
        pass

    def ConvertToMiddleburyFormat(self, unpack_dir_path, metadata_dict, training_dir_path, test_dir_path):
        
        # Convert downloaded files to Middlebury format
        src_train_path = os.path.join(unpack_dir_path, 'train')
        src_test_path  = os.path.join(unpack_dir_path, 'test')

        # convert images
        for subset_src_dir, subset_dst_dir in [(src_train_path, training_dir_path), (src_test_path, test_dir_path)]:
            img_src_dir = os.path.join(subset_src_dir, 'img')
            img_dst_dir = os.path.join(subset_dst_dir, 'images')

            sequences = [d for d in os.listdir(img_src_dir) if os.path.isdir(os.path.join(img_src_dir, d))]
            for seq in sequences:
                seq_src_dir = os.path.join(img_src_dir, seq)
                seq_dst_dir = os.path.join(img_dst_dir, seq)

                MakeDirsExistOk(seq_dst_dir)

                images = [f for f in os.listdir(seq_src_dir) if f.endswith('.jpg') or f.endswith('.png')]
                for img in images:
                    frame = int(img[4:-4])
                    shutil.move(os.path.join(seq_src_dir, f), os.path.join(seq_dst_dir, 'frame_%04d.%s' % (frame, img[-3:])))
                    pass
                pass

            shutil.rmtree(subset_src_dir)
            pass

        # convert flow
        flow_src_dir = os.path.join(src_train_path, 'flow')
        flow_dst_dir = os.path.join(training_dir_path, 'flow')

        sequences = [d for d in os.listdir(flow_src_dir) if os.path.isdir(os.path.join(flow_src_dir, d))]
        for seq in sequences:
            seq_src_dir = os.path.join(flow_src_dir, seq)
            seq_dst_dir = os.path.join(flow_dst_dir, seq)

            MakeDirsExistOk(seq_dst_dir)

            flows = [f for f in os.listdir(seq_src_dir) if f.endswith('.npz')]            
            for flow in flows:
                frame = int(flow[4:-7])
                flow_src_path = os.path.join(seq_src_dir, flow)
                flow_dst_path = os.path.join(seq_dst_dir, 'frame_%04d.flo' % (frame))
                
                d   = np.load(flow_src_path)
                h,w = d['u'].shape[:2]
                u   = array.array('f', np.asarray(d['u'].astype(np.float32)))
                v   = array.array('f', np.asarray(d['v'].astype(np.float32)))
                WriteMiddleburyFloFile(flow_dst_path, w, h, u, v)
                pass

            shutil.rmtree(flow_src_dir)
            pass
        pass


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
        raise NotImplementedError
        return isinstance(dataset_format, MiddleburyFormat) or isinstance(dataset_format, Kitti2015Format)
    
    
    def CreateSubmission(self, dataset_format, method, pack_dir_path,
                         metadata_dict, training_dir_path, training_datasets,
                         test_dir_path, test_datasets, archive_base_path):
        raise NotImplementedError
    
