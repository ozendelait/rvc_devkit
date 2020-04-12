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
        self.archives_flow_train = {
        '001-003':'1ZKQiDABFztFOILUPK1ehPdDzDjYIY1Ba',
        '004':'10G8b87MYCOG8_VulldUcMIWFvh-qRfh0',
        '005-006':'1EQHU5CmMGW3zpdaTcgRHehcl-tixt4jq',
        '007':'11bWGWZFpYOMyhcGKmbCSszDR9DeFplm0',
        '008':'1u2n-H8BKu5qFbyC0t7W34iHppVOaoxJN',
        '009':'12rOKembl3W-jI0JLgCODsiUAdj0qDUO_',
        '010-013':'1lbqRqm2CsV3zAmrmqLMO2H1mNjZ6me2Y',
        '014':'17FtRZWphiZljMPmdbAgWy8buMucSv6Gg',
        '015-016':'1idy0ZNOS2_rS4RYizPeCUPCbWFYWjUBo',
        '017':'1CslhQOI1SPLjJA5L1LJSfkahyGEQMx-G',
        '018':'14hkSy-NTxti2ttaQgaQuQ0DXhy59PaQD',
        '019':'14YrkC_01NZbZ8Mnov7a0YCXFWyobjkA3',
        '020-021':'1rBQEgvItSXzLh3X9dgU57UZDXuj2NDIa',
        '022-024':'1eQhubY0GwGAh_p5vbuies8lTYa1nHh9X',
        '025':'1V37_z9-UlUvh_c8M1Y3-LzceO42ZPFnu',
        '026':'1tDZ-wTUjEh2pO_hW4gIKp1jaK3QWw1nG',
        '027-029':'1WEV-Fkn8f2udJCZBWU7A0FuOBzvudy3c',
        '030-032':'1Vjv4nJLy4ATyGfDyw6JD4I0eKX8O9kjn',
        '033-034':'1mDlNaYXhOiD9YDAPaXdFIcxDj6EWc612',
        '035-036':'1xO9xW2Npw25F5iJd-R3zR3RGOzW9d1Va',
        '037-039':'1nADeJDbzY7V3NzVRT1p4ew-mZJR6lQrb',
        '040':'1SzrRjaDs5Yd9q-FXPj8meuz0QASVvML4',
        '041':'1bj3qzhUAq5OhChsjqT9b2A7qDPPN4sD_',
        '042-043':'1v-Uwoh2DRd1ciDGszhjlMRiN4bRzscOb',
        '044-045':'1XLNDDFbf811WD8LwTZrh3_NErDgAl2v9',
        '046':'1ilwwJ4nd0-MpcDfzbdmU3w5m7lhRftg0',
        '047':'1md2Weo9RJ1phwo1R2TZ1fK43YVND6SRl',
        '048':'1e5H0_Ocaz7efAHuEnSV48ZGSVnDoPlTW',
        '049':'1AN1d8a7SbcdGgtUOVMBEe3Xusy7HeGsl',
        '050':'1zF_YGxTlAKvueLwG-WFqpGfP8jUFhqPy',
        '051-054':'1eoBEhYzGIlCjdXDJt0QvPFRoddI7G2gI',
        '055-056':'10BVuWYMzQis4KRs6rt4chTSFVctxJ1hy',
        '057-058':'1-K48yayD4pRDLSb9agvqXnO-vG6SeaMi',
        '059-061':'1M5Hiqln-0opfp0F98r9_pufEkK7P5JEG',
        '062':'1x4F9oaHmnZjGDpVEk3kTsMtgv3f99b5s',
        '063':'1VZ0XdhmP0Iu2LU0kVAlSi8-MsSgrTklK',
        '064-065':'1DzKIOvZqHs6mNIr8LimcYOMdi8aY79us',
        '066-067':'1jmpGSNVHmPBsjf6SiYRPvhmItAZFXrug',
        '068':'1PX771dslOxKFxzpIYxAhE-I8RRGv30vY',
        '069-070':'1WwKv3ESI1VcEl4FmXsBTvDxxWu8gvXNk',
        '071':'12zb4K6aKZ2Q95vi4if-k2R8m5hiU0H9L',
        '072':'1DBPWInxKM3pGvTGDAL524qvB2rwEVr47',
        '073-074':'1Knd2mFO3OwwycAqnQEsvsBdlkQIZJzv_',
        '075':'1ooOnGnBwAjLUxMNS0xKRnra2iGz1eA_-',
        '076-077':'15wHJtPUyrPnZB8xelBtgkG_vSpFKPDNQ',
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
        self.archives_flow_val = {
        
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

            flows = [f for f in os.listdir(seq_src_dir) if f.endswith('_bw.mat')]            
            for flow in flows:
                frame = int(flow[4:-7])
                flow_src_path = os.path.join(seq_src_dir, flow)
                flow_dst_path = os.path.join(seq_dst_dir, '%s_%04d.png' % (seq, frame))
                
                d   = scipy.io.loadmat(flow_src_path)
                h,w = d['u'].shape[:2]
                u   = array.array('f', np.asarray(-d['u']))
                v   = array.array('f', np.asarray(-d['v']))
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

            flows = [f for f in os.listdir(seq_src_dir) if f.endswith('_bw.mat')]            
            for flow in flows:
                frame = int(flow[4:-7])
                flow_src_path = os.path.join(seq_src_dir, flow)
                flow_dst_path = os.path.join(seq_dst_dir, 'frame_%04d.flo' % (frame))
                
                d   = scipy.io.loadmat(flow_src_path)
                h,w = d['u'].shape[:2]
                u   = array.array('f', np.asarray(-d['u']))
                v   = array.array('f', np.asarray(-d['v']))
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
    
