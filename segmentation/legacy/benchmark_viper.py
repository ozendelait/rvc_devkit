import math
import os.path as op
import shutil
import imageio
import numpy as np

from benchmark import *
from benchmark_kitti2015 import KITTI2015
from dataset_format_kitti2015 import *
from util import *
from util_segmentation import *

common_rvc_subfolder = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(os.path.abspath(__file__))),"../../common/"))
if common_rvc_subfolder not in sys.path:
    sys.path.insert(0, common_rvc_subfolder)
from rvc_download_helper import download_file_from_google_drive, download_file_with_resume


class VIPER(Benchmark):

    def __init__(self):
        self.archives_imgjpg_train = {
        # '00-77_0':'1-O7vWiMa3mDNFXUoYxE3vkKZQpiDXUCf', # GDrive
        '00-77_0':'train_img_00-77_0_jpg.zip',
        }
        self.archives_inst_train = {
        # '00-77_0':'1HOG-vQTgeLYzDILAlvekeMbUoB-EtcRM',
        '00-77_0':'train_inst_00-77_0.zip'
        }
        self.archives_cls_train = {
        # '00-77_0':'1lAbmIVuQTLZu4-hNKD20wmGn1SThvFtv',
        '00-77_0':'train_cls_00-77_0.zip'
        }
        self.archives_imgjpg_val = {
        # '00-47_0':'1951O6Eu-VuMHaL1vJ9V35njcj30GjPiN',
        '00-47_0':'val_img_00-47_0_jpg.zip'
        }
        self.archives_inst_val = {
        # '00-47_0':'1ow37dljI0KfEQ9kbOvb-qQsjSpGTOnz2',
        '00-47_0':'val_inst_00-47_0.zip'
        }
        self.archives_cls_val = {
        # '00-47_0':'1QN2OSXTDsXPXntNrY-ojDpj-vFWjBZlK',
        '00-47_0':'val_cls_00-47_0.zip'
        }
        self.archives_imgjpg_test = {
        # '00-60_0':'1KYSsgv-hp5BGU0EOfvX3gajr00wwSmFc', 
        '00-60_0':'test_img_00-60_0_jpg.zip'
        }

    def Name(self):
        return 'VIPER Semantic Labeling Task'
    
    
    def Prefix(self):
        return 'VIPER_'
    
    
    def Website(self):
        return 'https://playing-for-benchmarks.org/'
    
    def LabelIds(self):
        return range(0,33)

    def LabelNames(self):
        return ['unlabeled', 'ambiguous', 'sky', 'road', 'sidewalk', 'railtrack', 'terrain', 'tree', 'vegetation', 
        'building', 'infrastructure', 'fence', 'billboard', 'trafficlight', 'trafficsign', 'mobilebarrier', 
        'firehydrant', 'chair', 'trash', 'trashcan', 'person', 'animal', 'bicycle', 'motorcycle', 'car', 'van', 
        'bus', 'truck', 'trailer', 'train', 'plane', 'boat']
    
    def SupportsTrainingDataOnlySubmissions(self):
        return False
    
    
    def SupportsTrainingDataInFullSubmissions(self):
        return False
    
    
    def GetOptions(self, metadata_dict):
        return  # No options
    
    
    def DownloadAndUnpack(self, archive_dir_path, unpack_dir_path, metadata_dict):
        archives_to_download = ['archives_imgjpg_train', 'archives_inst_train', 'archives_cls_train', 'archives_imgjpg_val', 'archives_inst_val', 'archives_cls_val', 'archives_imgjpg_test']
        
        for archive in archives_to_download:
            archive_dict = getattr(self, archive)
            for archive_id, gdrive_id in archive_dict.items():
                archive_path = os.path.join(archive_dir_path, archive[9:] + '_' + archive_id + '.zip')
                if not os.path.exists(archive_path):

                    url = 'https://viper-dataset.s3.amazonaws.com/' + gdrive_id
                    download_file_with_resume(url, archive_path, try_resume_bytes=-1, total_sz = None)

                    # original viper website (GDrive)
                    # download_file_from_google_drive(gdrive_id, archive_path, try_resume_bytes=-1, total_sz = None)
                    if os.path.exists(archive_path):
                        UnzipFile(archive_path, unpack_dir_path)
                        pass
                    pass
            pass
        pass

    def CanConvertOriginalToFormat(self, dataset_format):
        return isinstance(dataset_format, KITTI2015Format)

        
    def ConvertOriginalToFormat(self, dataset_format, unpack_dir_path, metadata_dict, training_dir_path, test_dir_path):
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
                    shutil.move(os.path.join(seq_src_dir, f), os.path.join(seq_dst_dir, '%s_%04d.%s' % (self.Prefix(), seq, frame, img[-3:])))
                    pass
                pass

            # shutil.rmtree(subset_src_dir)
            pass

        # convert class segmentation
        seg_src_dir = os.path.join(src_train_path, 'cls')
        seg_dst_dir = os.path.join(training_dir_path, 'semantic')

        sequences = [d for d in os.listdir(seg_src_dir) if os.path.isdir(os.path.join(seg_src_dir, d))]
        for seq in sequences:
            seq_src_dir = os.path.join(seg_src_dir, seq)
            seq_dst_dir = os.path.join(seg_dst_dir)

            MakeDirsExistOk(seq_dst_dir)

            labelmaps = [f for f in os.listdir(seq_src_dir) if f.endswith('.png')]            
            for labelmap in labelmaps:
                frame = int(labelmap[4:-4])
                seg_src_path = os.path.join(seq_src_dir, labelmap)
                seg_dst_path = os.path.join(seq_dst_dir, '%s%s_%04d.png' % (self.Prefix(), seq, frame))
                
                shutil.move(seg_src_path, seg_dst_path)
                pass

            # shutil.rmtree(seg_src_dir)
            pass

        # instance segmentation
        seg_src_dir = os.path.join(src_train_path, 'inst')
        seg_dst_dir = os.path.join(training_dir_path, 'instance')

        sequences = [d for d in os.listdir(seg_src_dir) if os.path.isdir(os.path.join(seg_src_dir, d))]
        for seq in sequences:
            seq_src_dir = os.path.join(seg_src_dir, seq)
            seq_dst_dir = os.path.join(seg_dst_dir)

            MakeDirsExistOk(seq_dst_dir)

            labelmaps = [f for f in os.listdir(seq_src_dir) if f.endswith('.png')]            
            for labelmap in labelmaps:
                frame = int(labelmap[4:-4])
                seg_src_path = os.path.join(seq_src_dir, labelmap)
                seg_dst_path = os.path.join(seq_dst_dir, '%s%s_%04d.png' % (self.Prefix(), seq, frame))
                
                img_viper  = imageio.imread(seg_src_path).astype(np.uint16)
                h,w,_      = img_viper.shape
                viper_ids  = img_viper[:,:,1] * 256 + img_viper[:,:,2]
                u, indices = np.unique(viper_ids, return_inverse=True)
                assert u[0] == 0
                img_kitti = img_viper[:,:,0] * 256 + indices.reshape((h,w)).astype(np.uint16)
                imageio.imwrite(seg_dst_path, img_kitti)
                pass

            shutil.rmtree(seg_src_dir)
            pass
        pass


    def CanCreateSubmissionFromFormat(self, dataset_format):
        return isinstance(dataset_format, KITTI2015Format)