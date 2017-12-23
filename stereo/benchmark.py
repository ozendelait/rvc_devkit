from abc import ABCMeta
from abc import abstractmethod


# Virtual base class for benchmark implementations
class Benchmark(object):
    __metaclass__ = ABCMeta
    
    # Must return a user-visible benchmark name.
    @abstractmethod
    def Name(self):
        raise NotImplementedError()
    
    
    # Must return the prefix added to dataset names of this benchmark.
    @abstractmethod
    def Prefix(self):
        raise NotImplementedError()
    
    
    # Must return the benchmark website URL.
    @abstractmethod
    def Website(self):
        raise NotImplementedError()
    
    
    # Must return whether this benchmark supports the online submission of
    # training-data-only archives.
    @abstractmethod
    def SupportsTrainingDataOnlySubmissions(self):
        raise NotImplementedError()
    
    
    # Must return whether full submissions for this benchmark can include
    # results on the training datasets.
    @abstractmethod
    def SupportsTrainingDataInFullSubmissions(self):
        raise NotImplementedError()
    
    
    # Must determine any options, e.g., which version of a dataset to download
    # in case there are different versions with different image resolutions.
    # This is always called first before DownloadAndConvert(), but not before
    # CreateSubmissionArchive().
    @abstractmethod
    def GetOptions(self):
        raise NotImplementedError()
    
    
    # Must download and unpack the dataset files, and convert them into a
    # specific format.
    @abstractmethod
    def DownloadAndConvert(self, archive_dir_path, unpack_dir_path, datasets_dir_path, training_dir_path, test_dir_path):
        raise NotImplementedError()
    
    
    # Must create the submission archive within the submission_dir_path
    # directory and return the filename of the archive within this directory.
    # The basename (without file extension) is given by base_filename.
    @abstractmethod
    def CreateSubmissionArchive(self, method, datasets_dir_path, training_dataset_names, test_dataset_names, training_dir_path, test_dir_path, pack_dir_path, archive_base_path):
        raise NotImplementedError()
    
