from dataset_format import *
import dataset_format_kitti2015  # Avoid issues with circular dependency using this import style
from util import *
from util_flow import *


# Middlebury flow dataset format
class MiddleburyFormat(DatasetFormat):
    
    def Name(self):
        return 'Middlebury Flow format'
    
    
    def Identifier(self):
        return 'middlebury'
    
    
    def Website(self):
        return 'https://vision.middlebury.edu/flow'
    
    
    def ListDatasets(self, dataset_folder_path):
        print(dataset_folder_path)
        imagepath = os.path.join(dataset_folder_path, 'images')
        return [dataset
                for dataset in os.listdir(imagepath)
                if os.path.isdir(os.path.join(imagepath, dataset))]
   
    
    def ListMethods(self, dataset_folder_path, dataset_name):
        # For existing methods, we expect flow files in
        # dataset_folder_path/images/dataset_name/frame_XX.flo
        #
        print(dataset_folder_path, dataset_name)
        methods = []
        folder_list = [folder for folder in os.listdir(dataset_folder_path)
                       if folder.endswith('_flow')
                       and os.path.isdir(os.path.join(dataset_folder_path, folder))]

        for folder in folder_list:
            folder_path = os.path.join(dataset_folder_path, folder, dataset_name)

            # Check if any flow files exist corresponding to given dataset
            flow_files = [f for f in os.listdir(folder_path)
                          if f.endswith('.flo') and f.startswith('frame_')]
            if len(flow_files) > 0:
                method_name = folder[:folder.rfind('_flow')]
                methods.append(method_name)

        return methods
    
    
    def PrepareRunningMethod(self, method_name, dataset_folder_path, dataset_name):
        im0_path = os.path.join(dataset_folder_path, 'images', dataset_name, 'frame_0010.png')
        im1_path = os.path.join(dataset_folder_path, 'images', dataset_name, 'frame_0011.png')
        output_dir_path = os.path.join(dataset_folder_path, method_name + '_flow', dataset_name, 'frame_0010' + method_name + '.flo')
        return [im0_path, im1_path, output_dir_path]
    
    
    def CanConvertInputToFormat(self, dataset_format):
        return isinstance(dataset_format, dataset_format_kitti2015.Kitti2015Format)


    def ConvertSeq(self, in_dir, out_dir, seq, in_ext, out_ext):
        # in_dir contains all sequences as subdirs
        # out_dir contains sequences as SEQ_xx.png
        MakeDirsExistOk(out_dir)

        in_dir_seq = os.path.join(in_dir, seq)
        files_to_copy = [f for f in sorted(os.listdir(in_dir_seq))
                         if f.endswith(in_ext)]
        files_to_copy = [os.path.join(in_dir_seq, f) for f in files_to_copy]
        files_to_copy = [f for f in files_to_copy if os.path.isfile(f)]

        if in_ext == '.png' and out_ext == '.png':
            copy_ = shutil.copy2
        elif in_ext == '.flo' and out_ext == '.png':
            copy_ = ConvertMiddleburyFloToKittiPng

        for file_in in files_to_copy:
            frameno = file_in[file_in.rfind('_')+1:file_in.rfind('.')]
            frameno = int(frameno)

            # We need this, otherwise the KITTI format would break.
            assert frameno < 100

            file_out = os.path.join(out_dir, seq + '_{0:02d}'.format(frameno) + out_ext)
            copy_(file_in, file_out)

    
    def ConvertInputToFormat(self, dataset_format, dataset_name, in_path, out_path):
        # Input format:
        # images/SEQUENCE/frame_{xxxx}.png
        # [flow/SEQUENCE/frame_{xxxx}.flo]
        #
        # Output format:
        # image_2/SEQUENCE_{xx}.png
        # [If existing: flow_occ/SEQUENCE_{xx}.png]
        #
        assert isinstance(dataset_format, dataset_format_kitti2015.Kitti2015Format)

        # Convert images
        in_image_path = os.path.join(in_path, 'images')
        out_image_path = os.path.join(out_path, 'image_2')
        self.ConvertSeq(in_image_path, out_image_path, dataset_name, '.png', '.png')

        # Convert flow
        in_flow_path = os.path.join(in_path, 'flow')
        if os.path.isdir(in_flow_path):
            out_flow_path = os.path.join(out_path, 'flow_occ')
            self.ConvertSeq(in_flow_path, out_flow_path, dataset_name, '.flo', '.png')


    def CanConvertOutputToFormat(self, dataset_format):
        return isinstance(dataset_format, dataset_format_kitti2015.Kitti2015Format)
    
    
    def ConvertOutputToFormat(self, dataset_format, method_name, dataset_name, in_path, out_path):
        assert isinstance(dataset_format, dataset_format_kitti2015.Kitti2015Format)

        in_flow_path = os.path.join(in_path, method_name + '_flow')
        out_flow_path = os.path.join(out_path, method_name + '_flow_occ')
        MakeDirsExistOk(out_flow_path)
        self.ConvertSeq(in_flow_path, out_flow_path, dataset_name, '.flo', '.png')
