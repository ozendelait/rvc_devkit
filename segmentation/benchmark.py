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
    # This can be done by interactive user input, or by parsing program
    # arguments. This function is always called first before
    # DownloadAndUnpack() and CanConvertOriginalToFormat(), but not before
    # CreateSubmission(). Option values can be stored in metadata_dict. Those
    # values will be stored in the benchmark metadata file and are later read
    # again such that they are also available to CreateSubmission().
    @abstractmethod
    def GetOptions(self, metadata_dict):
        raise NotImplementedError()
    
    
    # Must download the benchmark archives into archive_dir_path and unpack them
    # into unpack_dir_path.
    @abstractmethod
    def DownloadAndUnpack(self, archive_dir_path, unpack_dir_path,
                          metadata_dict):
        raise NotImplementedError()
    
    
    # Must return whether the class supports converting from the original
    # dataset format (as downloaded) to the given format.
    @abstractmethod
    def CanConvertOriginalToFormat(self, dataset_format):
        raise NotImplementedError()
    
    
    # Must convert from the original dataset format (as unpacked by
    # DownloadAndUnpack()) to the given format. The original files do not need
    # to remain intact (i.e., files can be moved instead of copied).
    @abstractmethod
    def ConvertOriginalToFormat(self, dataset_format, unpack_dir_path,
                                metadata_dict, training_dir_path,
                                test_dir_path):
        raise NotImplementedError()
    
    
    # Must return whether the class supports creating a submission archive
    # from the given dataset format.
    @abstractmethod
    def CanCreateSubmissionFromFormat(self, dataset_format):
        raise NotImplementedError()
    
    
    # Must create the submission archive for the results of the given method.
    # The base path to the archive to be created is given by archive_base_path
    # (to be extended by the archive file format extension). The function must
    # return the final (full) path to the archive (usually, the base path
    # extended by .zip). training_datasets and test_datasets are lists of tuples
    # (benchmark_and_dataset_name, original_dataset_name) of datasets belonging
    # to this benchmark, where original_dataset_name is the original dataset
    # name as in the benchmark (i.e., without the benchmark name prefix that is
    # added by the ROB script). The training or test dataset lists may be empty,
    # for example if a training-only submission is created (given that
    # SupportsTrainingDataOnlySubmissions() returned true) then test_datasets
    # will be empty. pack_dir_path is the path of a temporary directory that
    # can be used to create the file system structure required in the submission
    # archive. When the method finishes, this directory must be empty again.
    @abstractmethod
    def CreateSubmission(self, task_name, dataset_format, method, pack_dir_path,
                         metadata_dict, training_dir_path, training_datasets,
                         test_dir_path, test_datasets, archive_base_path):
        raise NotImplementedError()
