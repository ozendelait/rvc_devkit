from dataset_format import *
import dataset_format_middlebury  # Avoid issues with circular dependency using this import style
from util import *
from util_flow import *


# Kitti 2015 flow dataset format
class Kitti2015Format(DatasetFormat):
    
    def Name(self):
        return 'Kitti 2015 Flow format'
    
    
    def Identifier(self):
        return 'kitti2015'
    
    
    def Website(self):
        return 'http://www.cvlibs.net/datasets/kitti/eval_scene_flow.php?benchmark=flow'
    
    
    def ListDatasets(self, dataset_folder_path):
        imagepath = os.path.join(dataset_folder_path, 'image_2')
        datasets = []
        for dataset in os.listdir(imagepath):
            # Chop of frame number
            dataset_base = dataset[:dataset.rfind('_')]

            if os.path.isfile(os.path.join(imagepath, dataset)) and not dataset_base in datasets:
                datasets.append(dataset_base)

        return list(sorted(datasets))

    
    def ListMethods(self, dataset_folder_path, dataset_name):
        # For existing methods, we expect flow files in
        # dataset_folder_path/METHOD_flow_occ/dataset_name_??.png
        #
        methods = []
        folder_list = [folder for folder in os.listdir(dataset_folder_path)
                       if folder.endswith('_flow_occ')
                       and os.path.isdir(os.path.join(dataset_folder_path, folder))]

        for folder in folder_list:
            folder_path = os.path.join(dataset_folder_path, folder)

            # Check if any flow files exist corresponding to given dataset
            flow_files = [f for f in os.listdir(folder_path)
                          if f.endswith('.png') and f[:f.rfind('_')]==dataset_name]
            if len(flow_files) > 0:
                method_name = folder[:folder.rfind('_flow_occ')]
                methods.append(method_name)

        return methods
    
    
    def PrepareRunningMethod(self, method_name, dataset_folder_path, dataset_name):
        im0_path = os.path.join(dataset_folder_path, 'image_2', dataset_name +'_10.png')
        im1_path = os.path.join(dataset_folder_path, 'image_2', dataset_name +'_11.png')
        output_dir_path = os.path.join(dataset_folder_path, method_name + '_flow_occ', dataset_name + '_10.png')
        return [im0_path, im1_path, output_dir_path]
    
    
    def CanConvertInputToFormat(self, dataset_format):
        return isinstance(dataset_format, dataset_format_middlebury.MiddleburyFormat)


    def ConvertSeq(self, in_dir, out_dir, seq, in_ext, out_ext):
        # in_dir contains all sequences as files SEQ_{xx}
        # out_dir contains subdirs SEQ.
        MakeDirsExistOk(out_dir_seq)

        out_dir_seq = os.path.join(out_dir, seq)
        files_to_copy = [f for f in sorted(os.listdir(in_dir))
                         if (f.endswith(in_ext) and f.startswith(seq))]
        files_to_copy = [os.path.join(in_dir, f) for f in files_to_copy]
        files_to_copy = [f for f in files_to_copy if os.path.isfile(f)]

        if in_ext == '.png' and out_ext == '.png':
            copy_ = shutil.copy2
        elif in_ext == '.png' and out_ext == '.flo':
            copy_ = ConvertKittiPngToMiddleburyFlo

        for file_in in files_to_copy:
            frameno = file_in[file_in.rfind('_')+1:file_in.rfind('.')]
            frameno = int(frameno)

            file_out = os.path.join(out_dir_seq, 'frame_{0:04d}'.format(frameno) + out_ext)
            copy_(file_in, file_out)

    
    def ConvertInputToFormat(self, dataset_format, dataset_name, in_path, out_path):
        # Input format:
        # image_2/SEQUENCE_{xx}.png
        # [If existing: flow_occ/SEQUENCE_{xx}.png]
        #
        # Output format:
        # images/SEQUENCE/frame_{xxxx}.png
        # [flow/SEQUENCE/frame_{xxxx}.flo]
        #
        assert isinstance(dataset_format, dataset_format_middlebury.MiddleburyFormat)

        # Convert images
        in_image_path = os.path.join(in_path, 'image_2')
        out_image_path = os.path.join(out_path, 'images')
        self.ConvertSeq(in_image_path, out_image_path, dataset_name, '.png', '.png')

        # Convert flow
        in_flow_path = os.path.join(in_path, 'flow_occ')
        if os.path.isdir(in_flow_path):
            out_flow_path = os.path.join(out_path, 'flow')
            self.ConvertSeq(in_flow_path, out_flow_path, dataset_name, '.png', '.flo')


    def CanConvertOutputToFormat(self, dataset_format):
        return isinstance(dataset_format, dataset_format_middlebury.MiddleburyFormat)
    
    
    def ConvertOutputToFormat(self, dataset_format, method_name, dataset_name, in_path, out_path):
        assert isinstance(dataset_format, dataset_format_middlebury.MiddleburyFormat)

        in_flow_path = os.path.join(in_path, method_name + '_flow_occ')
        out_flow_path = os.path.join(out_path, method_name + '_flow')
        MakeDirsExistOk(out_flow_path)
        self.ConvertSeq(in_flow_path, out_flow_path, dataset_name, '.png', '.flo')
