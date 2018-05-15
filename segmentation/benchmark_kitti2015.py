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
        return 'KITTI 2015 Segmentation Challenge'
    
    
    def Prefix(self):
        return 'Kitti2015_'
    
    
    def Website(self):
        return 'http://www.cvlibs.net/datasets/kitti/'
    
    def LabelIds(self):
        return range(0,34)

    def LabelNames(self):
        return ["unlabeled","ego vehicle","rectification border","out of roi","static",
                "dynamic","ground","road","sidewalk","parking","rail track","building","wall","fence",
                "guard rail","bridge","tunnel","pole","polegroup","traffic light","traffic sign","vegetation",
                "terrain","sky","person","rider","car","truck","bus","caravan","trailer","train","motorcycle",
                "bicycle"]

    def SupportsTrainingDataOnlySubmissions(self):
        return False
    
    
    def SupportsTrainingDataInFullSubmissions(self):
        return False
    
    
    def GetOptions(self, metadata_dict):
        return  # No options
    
    
    def DownloadAndUnpack(self, archive_dir_path, unpack_dir_path, metadata_dict):
        # Download input images and ground truth segmentation (temporary location, will be moved to cvlibs)
        DownloadAndUnzipFile('https://s3.eu-central-1.amazonaws.com/avg-kitti/data_semantics.zip',
                             archive_dir_path, op.join(unpack_dir_path))

    
    def CanConvertOriginalToFormat(self, dataset_format):
        return isinstance(dataset_format, KITTI2015Format)
    
    
    def ConvertOriginalToFormat(self, dataset_format, unpack_dir_path, metadata_dict, training_dir_path, test_dir_path):
        # Move datasets into common folder
        src_dir_path = unpack_dir_path 
        
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
    
    
    def CreateSubmission(self, task_name, dataset_format, method, pack_dir_path,
                         metadata_dict, training_dir_path, training_datasets,
                         test_dir_path, test_datasets, archive_base_path):

        # do we want semantic and instance results to be packed into the same submission?
        # currently, separate directories and archives are created
        archive_base_path = op.join(archive_base_path + "_" + task_name)
        method_dir = op.join(pack_dir_path, method + "_" + task_name)

        if task_name == "semantic":
            archive_filename = self.CreateSemanticSubmission(task_name, method, method_dir, pack_dir_path,
                                                             test_dir_path, test_datasets, archive_base_path)

        if task_name == "instance":
            archive_filename = self.CreateInstanceSubmission(task_name, method, method_dir, pack_dir_path,
                                                             test_dir_path, test_datasets, archive_base_path)

        return archive_filename


    def CreateSemanticSubmission(self, task_name, method, method_dir, pack_dir_path,
                                 test_dir_path, test_datasets, archive_base_path):

        MakeDirsExistOk(op.join(method_dir, task_name))

        # copy semantic segmentation results
        for rob_name, original_name in test_datasets:
            src_img = op.join(test_dir_path, "algo_%s_semantic" % method, rob_name)
            tgt_img = op.join(method_dir, task_name, original_name)
            shutil.copy(src_img, tgt_img)

        # create archive and clean up
        archive_filename = ZipDirectory(archive_base_path, method_dir)
        DeleteFolderContents(pack_dir_path)

        return archive_filename


    def CreateInstanceSubmission(self, task_name, method, method_dir, pack_dir_path,
                                 test_dir_path, test_datasets, archive_base_path):

        # prepare source directories and retrieve all binary instance mask names
        src_pred_list_dir = op.join(test_dir_path, "algo_%s_instance" % method, "pred_list")
        src_pred_img_dir = op.join(test_dir_path, "algo_%s_instance" % method, "pred_img")
        mask_names = [op.splitext(img)[0] for img in os.listdir(src_pred_img_dir) if img.startswith(self.Prefix())]

        # prepare target directories
        tgt_pred_list_dir = op.join(method_dir, task_name, "pred_list")
        tgt_pred_img_dir = op.join(method_dir, task_name, "pred_img")
        MakeDirsExistOk(tgt_pred_list_dir)
        MakeDirsExistOk(tgt_pred_img_dir)

        labeIds = self.LabelIds()
        # for each image: copy the list file and all corresponding mask files
        for rob_name, original_name in test_datasets:

            # read original mask list file
            with open(op.join(src_pred_list_dir, rob_name.replace(".png", ".txt")), "r") as f:
                lines = f.readlines()

            # save converted file with removed prefixes
            with open(op.join(tgt_pred_list_dir, original_name.replace(".png", ".txt")), "w") as f:
                for line in lines:
                    relative_path, label_id, confidence = line.strip().split(" ")
                    if int(label_id) in labeIds : 
                        relative, subdir, img_name = relative_path.split("/")
                        new_line = "%s/%s/%s %s %s\n" % (
                        relative, subdir, img_name[len(self.Prefix()):], label_id, confidence)
                        f.write(new_line)

            # copy all binary masks for the given image
            img_masks = [img for img in mask_names if img.startswith(op.splitext(rob_name)[0])]
            for img_mask in img_masks:
                src_mask = op.join(test_dir_path, "algo_%s_instance" % method, "pred_img", img_mask + ".png")
                tgt_mask = op.join(tgt_pred_img_dir, img_mask[len(self.Prefix()):] + ".png")
                shutil.copy2(src_mask, tgt_mask)

        archive_filename = ZipDirectory(archive_base_path, op.join(method_dir,task_name))
        DeleteFolderContents(pack_dir_path)

        return archive_filename
