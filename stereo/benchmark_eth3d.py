import shutil

from benchmark import *
from dataset_format_middlebury2014 import *
from util import *
from util_stereo import *


class ETH3D2017(Benchmark):
    def Name(self):
        return "ETH3D Low-Res Two-View Scenario"
    
    
    def Prefix(self):
        return "ETH3D2017_"
    
    
    def Website(self):
        return 'https://www.eth3d.net/low_res_two_view'
    
    
    def SupportsTrainingDataOnlySubmissions(self):
        return True
    
    
    def SupportsTrainingDataInFullSubmissions(self):
        return True
    
    
    def GetOptions(self, metadata_dict):
        return  # No options
    
    
    def DownloadAndUnpack(self, archive_dir_path, unpack_dir_path, metadata_dict):
        temp_training_dir = os.path.join(unpack_dir_path, 'training')
        temp_test_dir = os.path.join(unpack_dir_path, 'test')
        
        MakeDirsExistOk(temp_training_dir)
        MakeDirsExistOk(temp_test_dir)
        
        # NOTE: The website publicly advertises only .7z versions of the
        #       archives. I added .zip versions for the two-view files such that
        #       installing 7zip is not required for taking part in the stereo
        #       challenge.
        DownloadAndUnzipFile('https://www.eth3d.net/data/two_view_training.zip', archive_dir_path, temp_training_dir)
        DownloadAndUnzipFile('https://www.eth3d.net/data/two_view_training_gt.zip', archive_dir_path, temp_training_dir)
        DownloadAndUnzipFile('https://www.eth3d.net/data/two_view_test.zip', archive_dir_path, temp_test_dir)
    
    
    def CanConvertOriginalToFormat(self, dataset_format):
        return isinstance(dataset_format, Middlebury2014Format)
    
    
    def ConvertOriginalToFormat(self, dataset_format, unpack_dir_path, metadata_dict, training_dir_path, test_dir_path):
        temp_training_dir = os.path.join(unpack_dir_path, 'training')
        temp_test_dir = os.path.join(unpack_dir_path, 'test')
        
        # Move the datasets to the common folders, while adding the benchmark prefix.
        for (src_path, dest_path) in [(temp_training_dir, training_dir_path), (temp_test_dir, test_dir_path)]:
            for dataset in os.listdir(src_path):
                os.rename(os.path.join(src_path, dataset),
                          os.path.join(dest_path, self.Prefix() + dataset))
        
        shutil.rmtree(temp_training_dir)
        shutil.rmtree(temp_test_dir)
        
        # NOTE: In addition to the Middlebury format, the ETH3D datasets also
        #       have the files "cameras.txt" and "images.txt".
    
    
    def CanCreateSubmissionFromFormat(self, dataset_format):
        return isinstance(dataset_format, Middlebury2014Format)
    
    
    def CreateSubmission(self, dataset_format, method, pack_dir_path,
                         metadata_dict, training_dir_path, training_datasets,
                         test_dir_path, test_datasets, archive_base_path):
        low_res_two_view_path = os.path.join(pack_dir_path, 'low_res_two_view')
        MakeDirsExistOk(low_res_two_view_path)
        
        for (src_folder_path, benchmark_and_dataset_name, original_dataset_name) in (
                [(training_dir_path, a, b) for (a, b) in training_datasets] +
                [(test_dir_path, a, b) for (a, b) in test_datasets]):
            src_dataset_path = os.path.join(src_folder_path, benchmark_and_dataset_name)
            
            # Copy .pfm file
            shutil.copy2(os.path.join(src_dataset_path, 'disp0' + method + '.pfm'),
                         os.path.join(low_res_two_view_path, original_dataset_name + '.pfm'))
            
            # Convert time file into required format
            src_time_path = os.path.join(src_dataset_path, 'time' + method + '.txt')
            time = ReadMiddlebury2014TimeFile(src_time_path)
            
            dest_time_path = os.path.join(low_res_two_view_path, original_dataset_name + '.txt')
            with open(dest_time_path, 'wb') as dest_time_file:
                dest_time_file.write(StrToBytes('runtime ' + str(time)))
        
        # Create the archive and clean up.
        # NOTE: .7z would be the preferred format for ETH3D, but for two-view
        #       submissions it does not really matter as those are small.
        archive_filename = ZipDirectory(archive_base_path, pack_dir_path)
        DeleteFolderContents(pack_dir_path)
        
        return archive_filename
    
