import shutil

from benchmark import *
from benchmark_middlebury2014 import *
from util import *


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
    
    
    def GetOptions(self):
        return  # No options
    
    
    def DownloadAndConvert(self, archive_dir_path, unpack_dir_path, datasets_dir_path, training_dir_path, test_dir_path):
        temp_training_dir = os.path.join(unpack_dir_path, 'training')
        MakeDirsExistOk(temp_training_dir)
        
        temp_testing_dir = os.path.join(unpack_dir_path, 'test')
        MakeDirsExistOk(temp_testing_dir)
        
        # NOTE: The website publicly advertises only .7z versions of the
        #       archives. I added .zip versions for the two-view files such that
        #       installing 7zip is not required for the stereo challenge.
        DownloadAndUnzipFile('https://www.eth3d.net/data/two_view_training.zip', archive_dir_path, temp_training_dir)
        DownloadAndUnzipFile('https://www.eth3d.net/data/two_view_training_gt.zip', archive_dir_path, temp_training_dir)
        DownloadAndUnzipFile('https://www.eth3d.net/data/two_view_test.zip', archive_dir_path, temp_testing_dir)
        
        # Move the datasets to the common folders, while adding the benchmark prefix.
        for dataset in os.listdir(temp_training_dir):
            os.rename(os.path.join(temp_training_dir, dataset),
                      os.path.join(training_dir_path, self.Prefix() + dataset))
        
        for dataset in os.listdir(temp_testing_dir):
            os.rename(os.path.join(temp_testing_dir, dataset),
                      os.path.join(test_dir_path, self.Prefix() + dataset))
        
        shutil.rmtree(temp_training_dir)
        shutil.rmtree(temp_testing_dir)
        
        # NOTE: In addition to the Middlebury format, the ETH3D datasets also
        #       have the files "cameras.txt" and "images.txt".
    
    
    def CreateSubmissionArchive(self, method, datasets_dir_path, training_dataset_names, test_dataset_names, training_dir_path, test_dir_path, pack_dir_path, archive_base_path):
        low_res_two_view_path = os.path.join(pack_dir_path, 'low_res_two_view')
        MakeDirsExistOk(low_res_two_view_path)
        
        # Handle training and test datasets in the same way.
        for pair in ([(name, os.path.join(training_dir_path, name)) for name in training_dataset_names] +
                     [(name, os.path.join(test_dir_path, name)) for name in test_dataset_names]):
            benchmark_and_dataset_name = pair[0]
            dataset_path = pair[1]
            
            original_dataset_name = benchmark_and_dataset_name[len(self.Prefix()):]
            
            # Copy .pfm file to pack dir
            shutil.copy2(os.path.join(dataset_path, 'disp0' + method + '.pfm'),
                         os.path.join(low_res_two_view_path, original_dataset_name + '.pfm'))
            
            # Convert time file into required format
            src_time_path = os.path.join(dataset_path, 'time' + method + '.txt')
            time = ReadMiddlebury2014TimeFile(src_time_path)
            
            dest_time_path = os.path.join(low_res_two_view_path, original_dataset_name + '.txt')
            with open(dest_time_path, 'wb') as dest_time_file:
                dest_time_file.write(StrToBytes('runtime ' + str(time)))
        
        # Create the archive and clean up.
        # NOTE: .7z would be the preferred format for ETH3D, but for two-view
        #       submissions it does not really matter.
        archive_filename = ZipDirectory(archive_base_path, pack_dir_path)
        DeleteFolderContents(pack_dir_path)
        
        return archive_filename
    
