import argparse
import json
import shutil
import time

from benchmark import *
from dataset_format import *
from util import *


def DatasetsPathForFormat(dataset_format):
    return 'datasets_' + dataset_format.FolderName()


def TrainingDatasetsPath(datasets_path):
    return os.path.join(datasets_path, 'training')


def TestDatasetsPath(datasets_path):
    return os.path.join(datasets_path, 'test')


def MetadataPath(datasets_path):
    return os.path.join(datasets_path, 'metadata')


def GetMetaDataFilename(benchmark):
    return benchmark.Prefix() + 'metadata.txt'


def WriteMetaDataDict(path, metadata_dict):
    with open(path, 'wb') as outfile:
        outfile.write(StrToBytes(json.dumps(metadata_dict, indent=2)))


def ReadMetaDataDict(path):
    with open(path, 'rb') as infile:
        text = infile.read().decode('UTF-8').strip()
        return json.loads(text)


def GetBenchmarkFromDatasetDirName(dir_name, benchmarks):
    benchmark = None
    for candidate in benchmarks:
        if dir_name.startswith(candidate.Prefix()):
            benchmark = candidate
            break
    if benchmark is None:
        raise Exception('Cannot determine the benchmark for dataset: ' + dir_name)
    return benchmark


def DownloadAndConvertDatasets(chosen_format, dataset_formats, keep_archives,
                               metadata_dir_path, training_dir_path,
                               test_dir_path, benchmarks):
    # Define temporary paths for downloading:
    # Folder for downloading archives into.
    archive_dir_path = 'archives'
    # Folder for unpacking archives into.
    unpack_dir_path = 'temp_unpack_dir'
    # Folder for performing conversions.
    conversion_dir_path = 'temp_conversion_dir'
    
    print('The datasets will be downloaded into the current working directory:')
    print('  ' + os.getcwd())
    print('')
    
    indexed_metadata = dict()
    
    # Get options for all benchmarks first (such that the downloads can run
    # without interruptions later).
    for (index, benchmark) in enumerate(benchmarks):
        indexed_metadata[index] = dict()
        benchmark.GetOptions(indexed_metadata[index])
    
    # Create directories.
    MakeDirsExistOk(archive_dir_path)
    MakeCleanDirectory(unpack_dir_path)
    MakeDirsExistOk(metadata_dir_path)
    MakeDirsExistOk(training_dir_path)  
    MakeDirsExistOk(test_dir_path)  
    
    # Download and convert all benchmark datasets.
    for (index, benchmark) in enumerate(benchmarks):
        metadata_dict = indexed_metadata[index]
        
        benchmark_archive_dir = os.path.join(archive_dir_path, benchmark.Prefix() + "archives")
        MakeDirsExistOk(benchmark_archive_dir)
        
        # Download.
        metadata_dict['download_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        benchmark.DownloadAndUnpack(benchmark_archive_dir, unpack_dir_path, metadata_dict)
        
        # Convert to the target format.
        if benchmark.CanConvertOriginalToFormat(chosen_format):
            # Convert to the target format directly.
            benchmark.ConvertOriginalToFormat(chosen_format, unpack_dir_path, metadata_dict, training_dir_path, test_dir_path)
        else:
            # Direct conversion is not implemented. Try to find a path of
            # supported conversions from the original to the target format.
            src_formats = dict()
            for dataset_format in dataset_formats:
                if benchmark.CanConvertOriginalToFormat(dataset_format):
                    src_formats[dataset_format] = None  # special value for conversion from original
            
            while True:
                found = False
                start_len = len(src_formats)
                for available_format, src_format in src_formats.copy().items():
                    for dataset_format in dataset_formats:
                        if available_format.CanConvertInputToFormat(dataset_format) and not dataset_format in src_formats:
                            src_formats[dataset_format] = available_format
                            if dataset_format == chosen_format:
                                found = True
                                break
                    if found:
                        break
                if found:
                    break
                if start_len == len(src_formats):
                    raise Exception('No conversion path to the requested format found')
            
            dest_formats = dict()
            dataset_format = chosen_format
            initial_format = None
            while True:
                if src_formats[dataset_format] is None:
                    initial_format = dataset_format
                    break
                dest_formats[src_formats[dataset_format]] = dataset_format
                dataset_format = src_formats[dataset_format]
            
            # Perform the conversions.
            src_training_dir_path = os.path.join(conversion_dir_path, '0', 'training')
            src_test_dir_path = os.path.join(conversion_dir_path, '0', 'test')
            MakeDirsExistOk(src_training_dir_path)
            MakeDirsExistOk(src_test_dir_path)
            benchmark.ConvertOriginalToFormat(initial_format, unpack_dir_path, metadata_dict, src_training_dir_path, src_test_dir_path)
            
            conversion_dir_index = 1
            dataset_format = initial_format
            while dataset_format in dest_formats:
                target_format = dest_formats[dataset_format]
                if target_format == chosen_format:
                    target_training_dir_path = training_dir_path
                    target_test_dir_path = test_dir_path
                else:
                    target_training_dir_path = os.path.join(conversion_dir_path, str(conversion_dir_index), 'training')
                    target_test_dir_path = os.path.join(conversion_dir_path, str(conversion_dir_index), 'test')
                MakeDirsExistOk(target_training_dir_path)
                MakeDirsExistOk(target_test_dir_path)
                
                dataset_format.ConvertAllInputToFormat(dest_formats[dataset_format], src_training_dir_path, target_training_dir_path)
                src_training_dir_path = target_training_dir_path
                dataset_format.ConvertAllInputToFormat(dest_formats[dataset_format], src_test_dir_path, target_test_dir_path)
                src_test_dir_path = target_test_dir_path
                
                dataset_format = dest_formats[dataset_format]
                
                shutil.rmtree(os.path.join(conversion_dir_path, str(conversion_dir_index - 1)))
                conversion_dir_index += 1
            
            shutil.rmtree(conversion_dir_path)
        
        WriteMetaDataDict(os.path.join(metadata_dir_path, GetMetaDataFilename(benchmark)), metadata_dict)
    
    # Clean up unpack and archive directories.
    shutil.rmtree(unpack_dir_path)
    if not keep_archives:
        shutil.rmtree(archive_dir_path)
    
    print('')
    print('Done! The datasets are in:')
    print('  ' + training_dir_path)
    print('and')
    print('  ' + test_dir_path)


def DeterminePossibleSubmissions(training_dir_path, test_dir_path, dataset_format, benchmarks):
    # Flags whether a dataset required for one of the categories above has
    # already been checked. If a flag is set, no method which only occurs
    # in subsequent datasets can be complete anymore.
    checked_required_training_dataset = False
    checked_required_full_dataset = False
    
    keep_complete_methods_only = lambda methods, methods_with_results : (
        [method for method in methods if method in methods_with_results])
    
    training_submission_methods = []
    full_submission_methods = []
    
    # Check training dataset results.
    for benchmark_and_dataset_name in dataset_format.ListDatasets(training_dir_path):
        benchmark = GetBenchmarkFromDatasetDirName(benchmark_and_dataset_name, benchmarks)
        methods_with_results = dataset_format.ListMethods(training_dir_path, benchmark_and_dataset_name)
        
        # If results on this dataset are required for training submissions,
        # keep only those methods in the training submission list which
        # have results on the dataset.
        is_required_training_dataset = benchmark.SupportsTrainingDataOnlySubmissions()
        if is_required_training_dataset:
            training_submission_methods = keep_complete_methods_only(training_submission_methods, methods_with_results)
        
        # If results on this dataset are required for full submissions,
        # keep only those methods in the full submission list which
        # have results on the dataset.
        is_required_full_dataset = benchmark.SupportsTrainingDataInFullSubmissions()
        if is_required_full_dataset:
            full_submission_methods = keep_complete_methods_only(full_submission_methods, methods_with_results)
        
        # If this is the first dataset which is required for training or
        # full submission, collect the available methods.
        if is_required_training_dataset and not checked_required_training_dataset:
            training_submission_methods = methods_with_results
        if is_required_full_dataset and not checked_required_full_dataset:
            full_submission_methods = methods_with_results
        
        if is_required_training_dataset:
            checked_required_training_dataset = True
        if is_required_full_dataset:
            checked_required_full_dataset = True
    
    # Check test dataset results.
    for benchmark_and_dataset_name in dataset_format.ListDatasets(test_dir_path):
        benchmark = GetBenchmarkFromDatasetDirName(benchmark_and_dataset_name, benchmarks)
        methods_with_results = dataset_format.ListMethods(test_dir_path, benchmark_and_dataset_name)
        
        # Keep only those methods in the full submission list which have
        # results on the dataset.
        full_submission_methods = keep_complete_methods_only(full_submission_methods, methods_with_results)
        
        # If this is the first dataset which is required for full
        # submission, collect the available methods.
        if not checked_required_full_dataset:
            full_submission_methods = methods_with_results
        
        checked_required_full_dataset = True
    
    return (training_submission_methods, full_submission_methods)


def CreateSubmissionArchives(chosen_format, dataset_formats, method,
                             training_only, metadata_dir_path,
                             training_dir_path, test_dir_path, benchmarks):
    submission_dir_path = 'submission_archives'
    MakeDirsExistOk(submission_dir_path)
    
    pack_dir_path = 'temp_pack_dir'
    MakeCleanDirectory(pack_dir_path)
    
    # Folder for performing conversions.
    conversion_dir_path = 'temp_conversion_dir'
    
    archive_website_mapping = []
    
    for benchmark in benchmarks:
        if training_only and not benchmark.SupportsTrainingDataOnlySubmissions():
            continue
        
        include_training_results = (
            (training_only and benchmark.SupportsTrainingDataOnlySubmissions()) or
            (not training_only and benchmark.SupportsTrainingDataInFullSubmissions()))
        include_test_results = not training_only
        
        # Determine the paths to the required datasets.
        training_datasets = []
        if include_training_results:
            for benchmark_and_dataset_name in chosen_format.ListDatasets(training_dir_path):
                if benchmark_and_dataset_name.startswith(benchmark.Prefix()):
                    original_dataset_name = benchmark_and_dataset_name[len(benchmark.Prefix()):]
                    training_datasets.append((benchmark_and_dataset_name, original_dataset_name))
        
        test_datasets = []
        if include_test_results:
            for benchmark_and_dataset_name in chosen_format.ListDatasets(test_dir_path):
                if benchmark_and_dataset_name.startswith(benchmark.Prefix()):
                    original_dataset_name = benchmark_and_dataset_name[len(benchmark.Prefix()):]
                    test_datasets.append((benchmark_and_dataset_name, original_dataset_name))
        
        metadata_dict = ReadMetaDataDict(os.path.join(metadata_dir_path, GetMetaDataFilename(benchmark)))
        
        if benchmark.CanCreateSubmissionFromFormat(chosen_format):
            # Create the submission archive directly.
            archive_name = benchmark.CreateSubmission(
                chosen_format, method, pack_dir_path, metadata_dict,
                training_dir_path, training_datasets, test_dir_path, test_datasets,
                os.path.join(submission_dir_path, benchmark.Prefix() + method))
        else:
            # Direct creation is not implemented. Try to find a path of
            # supported conversions from the result format to a supported
            # format.
            dest_formats = dict()
            for dataset_format in dataset_formats:
                if benchmark.CanCreateSubmissionFromFormat(dataset_format):
                    dest_formats[dataset_format] = None  # special value for ability to create submission
            
            while True:
                found = False
                start_len = len(dest_formats)
                for available_format, dest_format in dest_formats.copy().items():
                    for dataset_format in dataset_formats:
                        if dataset_format.CanConvertOutputToFormat(available_format) and not dataset_format in dest_formats:
                            dest_formats[dataset_format] = available_format
                            if dataset_format == chosen_format:
                                found = True
                                break
                    if found:
                        break
                if found:
                    break
                if start_len == len(dest_formats):
                    raise Exception('No conversion path to a format with the ability to create a submission archive found')
            
            # Perform the conversions.
            src_training_dir_path = training_dir_path
            src_test_dir_path = test_dir_path
            
            conversion_dir_index = 1
            dataset_format = chosen_format
            while dest_formats[dataset_format] is not None:
                target_format = dest_formats[dataset_format]
                target_training_dir_path = os.path.join(conversion_dir_path, str(conversion_dir_index), 'training')
                target_test_dir_path = os.path.join(conversion_dir_path, str(conversion_dir_index), 'test')
                MakeDirsExistOk(target_training_dir_path)
                MakeDirsExistOk(target_test_dir_path)
                
                if include_training_results:
                    dataset_format.ConvertAllOutputToFormat(dest_formats[dataset_format], method, src_training_dir_path, target_training_dir_path)
                src_training_dir_path = target_training_dir_path
                if include_test_results:
                    dataset_format.ConvertAllOutputToFormat(dest_formats[dataset_format], method, src_test_dir_path, target_test_dir_path)
                src_test_dir_path = target_test_dir_path
                
                dataset_format = dest_formats[dataset_format]
                
                if os.path.isdir(os.path.join(conversion_dir_path, str(conversion_dir_index - 1))):
                    shutil.rmtree(os.path.join(conversion_dir_path, str(conversion_dir_index - 1)))
                conversion_dir_index += 1
            
            archive_name = benchmark.CreateSubmission(
                dataset_format, method, pack_dir_path, metadata_dict,
                src_training_dir_path, training_datasets, src_test_dir_path, test_datasets,
                os.path.join(submission_dir_path, benchmark.Prefix() + method))
            
            shutil.rmtree(conversion_dir_path)
        
        archive_website_mapping.append((archive_name, benchmark.Website()))
    
    shutil.rmtree(pack_dir_path)
    
    print('')
    print('Done! The submission archives are in:')
    print(submission_dir_path)
    print('')
    print('As the next step, submit the archives on the following websites:')
    for pair in archive_website_mapping:
        print('  ' + os.path.basename(pair[0]) + ' on ' + pair[1])
    print('')
    print('Finally, the submission must be completed by filling a short form on the Robust Vision Challenge website: TODO')  # TODO: Insert URL


def DevkitMain(task_name, benchmarks, dataset_formats):
    # Validate setup.
    if len(dataset_formats) == 0:
        raise Exception('No dataset formats defined.')
    if len(benchmarks) == 0:
        raise Exception('No benchmarks defined.')
    
    # Parse arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument("--keep_archives", action='store_true', help='Keep the downloaded archives instead of deleting them after extraction.')
    args = parser.parse_args()
    
    # Output script information.
    print('--- ' + task_name.title() + ' devkit for the Robust Vision Challenge 2018 ---')
    print('')
    print('Includes the following benchmarks:')
    for benchmark in benchmarks:
        print('* ' + benchmark.Name())
    print('')
    
    # Check for existing dataset and result files.
    format_info = dict()
    for dataset_format in dataset_formats:
        format_info[dataset_format] = dict()
        datasets_dir = DatasetsPathForFormat(dataset_format)
        format_info[dataset_format]['datasets_dir'] = datasets_dir
        
        # Check whether all datasets were downloaded in this format.
        format_info[dataset_format]['downloaded'] = (
            os.path.isdir(datasets_dir) and
            all([os.path.isfile(os.path.join(MetadataPath(datasets_dir), GetMetaDataFilename(benchmark))) for benchmark in benchmarks]))
        
        # Check whether any submissions are possible with result files in this
        # format.
        format_info[dataset_format]['training_submission_methods'] = []
        format_info[dataset_format]['full_submission_methods'] = []
        if format_info[dataset_format]['downloaded']:
            # Check whether results exist which could be submitted, for two categories:
            # * training-only submissions (might only be supported by some benchmarks)
            # * full submissions
            # We do not offer test-data only submissions (some benchmarks even
            # require to submit both training and test results).
            (training_submission_methods, full_submission_methods) = (
                DeterminePossibleSubmissions(TrainingDatasetsPath(format_info[dataset_format]['datasets_dir']),
                                         TestDatasetsPath(format_info[dataset_format]['datasets_dir']),
                                         dataset_format,
                                         benchmarks))
            format_info[dataset_format]['training_submission_methods'] = training_submission_methods
            format_info[dataset_format]['full_submission_methods'] = full_submission_methods
    
    # If no datasets were downloaded yet, do this now.
    if not any([format_info[dataset_format]['downloaded'] for dataset_format in dataset_formats]):
        # If there is more than one format, let the user choose which one to work
        # with.
        format_index = 0
        if len(dataset_formats) > 1:
            print('Choose the dataset format to work with by entering its number:')
            for (index, dataset_format) in enumerate(dataset_formats):
                print('  [' + str(index + 1) + '] ' + dataset_format.Name())
                print('   ' + (' ' * len(str(index + 1))) + '  ( see ' + dataset_format.Website() + ' )')
            
            while True:
                response = GetUserInput("> ")
                if not response.isdigit():
                    print('Please enter a number.')
                elif int(response) <= 0 or int(response) > len(dataset_formats):
                    print('Pleaser enter a valid number.')
                else:
                    print('')
                    format_index = int(response) - 1
                    break
        
        chosen_format = dataset_formats[format_index]
        datasets_dir_path = format_info[chosen_format]['datasets_dir']
        
        DownloadAndConvertDatasets(chosen_format,
                                   dataset_formats,
                                   args.keep_archives,
                                   MetadataPath(datasets_dir_path),
                                   TrainingDatasetsPath(datasets_dir_path),
                                   TestDatasetsPath(datasets_dir_path),
                                   benchmarks)
    else:
        # Let the user choose an action.
        # TODO: Offer changing options (e.g., download different resolution for Middlebury)?
        print('Please choose an action by entering its number. The action list includes creating submission archives for all methods with complete result sets. If a method is missing, make sure that all required result files for this method exist.')
        
        actions = []
        counter = 1
        for dataset_format in dataset_formats:
            if not format_info[dataset_format]['downloaded']:
                print('  [' + str(counter) + '] Obtain datasets in format: ' + dataset_format.Name())
                print('   ' + (' ' * len(str(counter))) + '  ( see ' + dataset_format.Website() + ' )')
                actions.append(('obtain_format', dataset_format))
                counter += 1
            else:
                full_submission_methods = format_info[dataset_format]['full_submission_methods']
                for method in full_submission_methods:
                    print('  [' + str(counter) + '] Create full submission for: ' + method)
                    actions.append(('full_submission', dataset_format, method))
                    counter += 1
                
                training_submission_methods = format_info[dataset_format]['training_submission_methods']
                for method in training_submission_methods:
                    print('  [' + str(counter) + '] Create training submission for: ' + method)
                    actions.append(('training_submission', dataset_format, method))
                    counter += 1
        
        if len(actions) == 0:
            print('> No action possible, exiting.')
            return
        
        print('')
        choice = 0
        while True:
            response = GetUserInput("> ")
            if not response.isdigit():
                print('Please enter a number.')
            else:
                choice = int(response)
                if choice < 1 or choice >= counter:
                    print('Please enter a valid number.')
                else:
                    print('')
                    break
        
        action = actions[choice - 1]
        
        if action[0] == 'obtain_format':
            # Download / convert the datasets.
            chosen_format = action[1]
            datasets_dir_path = format_info[chosen_format]['datasets_dir']
            # TODO: It would be more efficient to use existing downloaded files
            #       as source files for the conversion in case the required
            #       conversions are implemented (and the same options are
            #       requested).
            DownloadAndConvertDatasets(chosen_format,
                                       dataset_formats,
                                       args.keep_archives,
                                       MetadataPath(datasets_dir_path),
                                       TrainingDatasetsPath(datasets_dir_path),
                                       TestDatasetsPath(datasets_dir_path),
                                       benchmarks)
        elif action[0] == 'full_submission' or action[0] == 'training_submission':
            method = action[2]
            chosen_format = action[1]
            is_training_submission = action[0] == 'training_submission'
            datasets_dir_path = format_info[chosen_format]['datasets_dir']
            CreateSubmissionArchives(chosen_format, dataset_formats, method,
                                     is_training_submission,
                                     MetadataPath(datasets_dir_path),
                                     TrainingDatasetsPath(datasets_dir_path),
                                     TestDatasetsPath(datasets_dir_path),
                                     benchmarks)
        else:
            raise Exception('Internal error: invalid action.')
