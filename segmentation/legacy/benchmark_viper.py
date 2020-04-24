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

common_rvc_subfolder = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(os.path.abspath(__file__))),"../common/"))
if common_rvc_subfolder not in sys.path:
    sys.path.insert(0, common_rvc_subfolder)
from rvc_download_helper import download_file_from_google_drive


class VIPER(Benchmark):

    def __init__(self):
        self.archives_imgjpg_train = {
        '001-019':'1e6ti6DDU3YTOH46jRu6hMuX9962hksNK',
        '020-039':'1_JDLF9YwoeanB9F0XxjR58dT_DHlKm4b',
        '040-059':'1w-Gyt9QpQpiPqe_jjawVhXd9s3qgyrJq',
        '060-077':'1Q6ALN3baxlQn0NSMB1FgUD7p6obtwVuY',
        }
        self.archives_imgpng_train = {
        'part_1':'1SckwMXEozB0MNfJjde3EQPe9yupvRIPn',
        'part_2':'1yiPdoLGdxfcQTsXMG2xI-LmcEJHEDK0E',
        'part_3':'1CTCdrm6WGt1AwQEIqpCYTZwV99IuFdZX',
        'part_4':'180rLxMLJPFUmkZy1ULVbYtVuL-DnlcKE',
        'part_5':'1iLvCIgtCKXOvQZvKgLBGiIKFugoD2RUY',
        'part_6':'1jeM6KpxVLKS46x1RDDIYGsvg5OaO3gVU',
        'part_7':'1tFMES2skiVNV1PpmkLfiw_p7APYZzYlP',
        'part_8':'1hQcUzC03_yjIoubSOmN7i2-KNUA5p29l',
        'part_9':'12zydZFogWm8OoRtK6r-WHJ8djidQdEXF',
        'part_10':'17gRlaTcvdeKxnkAfbZFZXSuSanRu84Gq',
        'part_11':'1nbiUsflExEK4wm5MLlVwbqS8yW8_1_II',
        'part_12':'1AE-6kSt0d8up6HbQoWzYQcsv5vsqTrN-',
        'part_13':'1MpaCqnqWuzG8PGHY-_9mi-uprDMSrt8L',
        'part_14':'1HTVFUowCfYRiNLK8ctFu5d2nivISIorY',
        'part_15':'1Z8HLdi-_dC60sX35JRmjWMReTTAKs9DQ',
        'part_16':'1nQkfQuKBvXNH3qZacBdBvO3Fv_N1aWhU',
        'part_17':'12dzv04R_vNtazp2o24iXr-c6Ho7FWhus',
        'part_18':'1pVOOrkL8JW4c6f1tjMhuJWIKwsQfMQjv',
        'part_19':'10vC8u-YzmewsqLwviyFgOoGIpAPYZaiq',
        'part_20':'1i2AMhedwBn-gndYWhw1Q_YgW5hZec8ay',
        'part_21':'1-iRBsEVbjf-ZEuz5Ivo6dRLYusRQLEbO',
        'part_22':'1gCivxvlqFQbyDiK7uGDF4X8-A9dIOd8w',
        'part_23':'1s5fcklj84BATkZitQiT-SWGq0KWsxaIX',
        'part_24':'1nqp2Gt2sfoj0EZ8Ov23-Fp-kM6Zec41m',
        'part_25':'1uyyqHakW2wwoUeBoFRD4sXGJT1GYzj_D',
        'part_26':'18FbWJp-e2hrF7vaBK3_3BO5b6Mt34-Gc',
        }
        self.archives_inst_train = {
        '001-077':'1EBWpik35KbUjMFI7gMWVrY6I1nbX_fly'
        }
        self.archives_cls_train = {
        '001-077':'0B-ePgl6HF260UC1NWkRlN214Wlk'
        }
        self.archives_imgjpg_val = {
        'part_1':'0B-ePgl6HF260UkhBQUJsa0cyMm8',
        'part_2':'0B-ePgl6HF260TnlNaUd0WkRjdkE',
        }
        self.archives_imgpng_val = {
        'part_1':'1TT-rJc5b8Uo0FEYr0vHD4QxAdgkIpyto',
        'part_2':'1rQi_BkB6hYq67mA0YZJ-eiZV3hd8j-_c',
        'part_3':'179b3xFYyeJKYX2qKiCPAbU-ySpymnNIg',
        'part_4':'1lpT_HDfj3-9lx_k2FE5fcoQm39k07jF4',
        'part_5':'1gfQ7NpUDtvKnDNLa00gcXr1kY1ac0ifd',
        'part_6':'1AUqn2PJaVQyQqkKEAg1Ya8w0XXi4Ekam',
        'part_7':'1_pSJ3WoRV6K5d6gwcYBonViQ6ERIyFkM',
        'part_8':'1-b3eZubBzhTWl3priHEu1B5WOAYuoLiV',
        'part_9':'1Kz32rVOdIcOX_YxfIkshIWiUThQ_l_S-',
        'part_10':'1HJyb6B34t0iM7YWNDJjHTY4xX-wV5wLx',
        }
        self.archives_inst_val = {
        '001-077':'1sdL_L0XFaEZXRJMHPXlYBRczBd305XeL'
        }
        self.archives_cls_val = {
        '001-077':'0B-ePgl6HF260dHN2VTl2T2sweVE'
        }
        self.archives_imgjpg_test = {
        'part_1':'0B-ePgl6HF260R3JibG5BQU12WlU', 
        'part_2':'0B-ePgl6HF260Q2pCRW5mZUNaWmc', 
        'part_3':'0B-ePgl6HF260b3F5OHhvTFBxY1E'
        }
        self.archives_imgpng_test = {
        'part_1':'1oMwJiur2-uAptwU5WfksXC-x52b1QtvY',
        'part_2':'1oZAbPhSw_H5u5c02NDn6dRFO0tcU2Dz6',
        'part_3':'1xHagdlOuSMbpclcX9Aci400yp3rOdaSL',
        'part_4':'1l_tUPLzpZWEDdYi36cTliu5CpVcCxtbt',
        'part_5':'1dhza6zC3rMQ1rp8ey3abA6gXTL6GhjjE',
        'part_6':'1Zd_e-k3MGABmYkGIjYta6UmPAHOkD0E7',
        'part_7':'1U76F8yFez0QIJxwHV8thvBUayjKiLIdj',
        'part_8':'13Ni9bMe7PpUhaWiFTB_dKVlgjzZ_mlpj',
        'part_9':'15HKVztWsPU73r-nipikqeXCl2KwP-7Th',
        'part_10':'1JyoauLNdlBuqHIJs-miz6Si1B-sALW1R',
        'part_11':'1RVFHknG3J_uSKPy3PxjbOvhgrhTd6iZN',
        'part_12':'1VQs7zZR01JbO9WHs4VNjYQ19E7xI4zSY',
        'part_13':'170ZwZcBE47mtjOBKDtA6FDcE5QyZ7Oc4',
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
        archives_to_download = ['archives_imgjpg_train', 'archives_inst_train', 'archives_cls_train', 'archives_imgjpg_test']
        
        for archive in archives_to_download:
            archive_dict = getattr(self, archive)
            for archive_id, gdrive_id in archive_dict.items():
                archive_path = os.path.join(archive_dir_path, archive[9:] + '_' + archive_id + '.zip')
                if not os.path.exists(archive_path):
                    download_file_from_google_drive(gdrive_id, archive_path, try_resume_bytes=-1, total_sz = None)
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