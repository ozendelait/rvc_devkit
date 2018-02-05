from abc import ABCMeta
from abc import abstractmethod


# Virtual base class for dataset format implementations
class DatasetFormat(object):
    __metaclass__ = ABCMeta
    
    # Must return a user-visible format name.
    @abstractmethod
    def Name(self):
        raise NotImplementedError()
    
    
    # Must return a string used to identify the dataset format. On the one hand,
    # this is used to determine the datasets folder name as:
    # 'datasets_' + format.Identifier().
    # On the other hand, this is the name used to refer to the dataset format
    # in the command line interface.
    @abstractmethod
    def Identifier(self):
        raise NotImplementedError()
    
    
    # Must return an URL to a website where the format is described.
    @abstractmethod
    def Website(self):
        raise NotImplementedError()
    
    
    # Must list all available datasets of this format in the given (training or
    # test) folder.
    @abstractmethod
    def ListDatasets(self, dataset_folder_path):
        raise NotImplementedError()
    
    
    # Must return a list of the names of all methods for which a result file for
    # the given dataset exists. dataset_folder_path specifies the path to the
    # training or test folder in which the dataset lies.
    @abstractmethod
    def ListMethods(self, dataset_folder_path, dataset_name):
        raise NotImplementedError()
    
    
    # Must prepare for running the method on the given dataset (e.g., by
    # creating a suitable output folder, if necessary). Must return program
    # arguments for running the method as a list.
    def PrepareRunningMethod(self, method_name, dataset_folder_path, dataset_name):
        raise NotImplementedError()
    
    
    # Must return whether this class supports conversion of the datasets to the
    # given dataset format.
    def CanConvertInputToFormat(self, dataset_format):
        return False
    
    
    # Must convert the dataset to the given format. The original files must
    # remain intact (i.e., files must be copied, not moved).
    def ConvertInputToFormat(self, dataset_format, dataset_name, in_path, out_path):
        raise NotImplementedError()
    
    
    # Converts all datasets to the given format.
    def ConvertAllInputToFormat(self, dataset_format, in_path, out_path):
        for dataset_name in self.ListDatasets(in_path):
            self.ConvertInputToFormat(dataset_format, dataset_name, in_path, out_path)
    
    
    # Must return whether this class supports conversion of the result files to
    # the given dataset format.
    def CanConvertOutputToFormat(self, dataset_format):
        return False
    
    
    # Must convert the result files to the given dataset format. The original
    # files must remain intact (i.e., files must be copied, not moved).
    def ConvertOutputToFormat(self, dataset_format, method_name, dataset_name, in_path, out_path):
        raise NotImplementedError()
    
    
    # Converts the results of all datasets to the given format.
    def ConvertAllOutputToFormat(self, dataset_format, method_name, in_path, out_path):
        for dataset_name in self.ListDatasets(in_path):
            self.ConvertOutputToFormat(dataset_format, method_name, dataset_name, in_path, out_path)
