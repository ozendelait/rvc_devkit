import argparse
import json
import shutil
import subprocess
import sys
import time

from benchmark import *
from dataset_format import *
from util import *


def DatasetsPathForFormat(dataset_format):
    return 'datasets_' + dataset_format.Identifier()


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


def ChooseDatasetFormat(request_string, dataset_formats):
    format_index = 0
    if len(dataset_formats) > 1:
        print(request_string)
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
    
    return dataset_formats[format_index]


def ParseFormatNameOrExit(format_name, dataset_formats):
    for dataset_format in dataset_formats:
        if dataset_format.Identifier() == format_name:
            return dataset_format
    
    print('Format ' + format_name + ' not found.')
    print('List of supported formats:')
    for dataset_format in dataset_formats:
        print('  ' + dataset_format.Identifier())
    sys.exit(1)


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
    
    print('The datasets will be downloaded into this folder in the current working directory:')
    print('  ' + os.path.join(os.getcwd(), DatasetsPathForFormat(chosen_format)))
    print('')
    
    indexed_metadata = dict()
    
    # Get options for all benchmarks first (such that the downloads can run
    # without interruptions later).
    for (index, benchmark) in enumerate(benchmarks):
        indexed_metadata[index] = dict()
        benchmark.GetOptions(indexed_metadata[index])
    
    # Create directories.
    MakeDirsExistOk(archive_dir_path)
    # MakeCleanDirectory(unpack_dir_path)
    MakeCleanDirectory(metadata_dir_path)
    MakeCleanDirectory(training_dir_path)
    MakeCleanDirectory(os.path.join(training_dir_path, 'image_2'))
    MakeCleanDirectory(os.path.join(training_dir_path, 'instance'))
    MakeCleanDirectory(os.path.join(training_dir_path, 'semantic'))
    MakeCleanDirectory(test_dir_path)
    MakeCleanDirectory(os.path.join(test_dir_path, 'image_2'))
    
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
            MakeCleanDirectory(conversion_dir_path)
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


def DeterminePossibleSubmissions(task_name, training_dir_path, test_dir_path, dataset_format, benchmarks):
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
        methods_with_results = dataset_format.ListMethods(task_name, training_dir_path, benchmark_and_dataset_name)
        
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
        methods_with_results = dataset_format.ListMethods(task_name, test_dir_path, benchmark_and_dataset_name)
        
        # Keep only those methods in the full submission list which have
        # results on the dataset.
        full_submission_methods = keep_complete_methods_only(full_submission_methods, methods_with_results)
        
        # If this is the first dataset which is required for full
        # submission, collect the available methods.
        if not checked_required_full_dataset:
            full_submission_methods = methods_with_results
        
        checked_required_full_dataset = True
    
    return (training_submission_methods, full_submission_methods)


def CreateSubmissionArchives(task_name, chosen_format, dataset_formats, method,
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
            archive_name = benchmark.CreateSubmission(task_name,
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
            MakeCleanDirectory(conversion_dir_path)
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
            
            archive_name = benchmark.CreateSubmission(task_name,
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
    print('Finally, the submission must be completed by filling a short form on the Robust Vision Challenge website: http://www.robustvision.net/')  # TODO: Insert URL


def RunMethod(method, run_file_path, chosen_format, training_only, additional_arguments):
    datasets_dir_path = DatasetsPathForFormat(chosen_format)
    
    folders = [TrainingDatasetsPath(datasets_dir_path)]
    if not training_only:
        folders.append(TestDatasetsPath(datasets_dir_path))
    
    for folder in folders:
        datasets = chosen_format.ListDatasets(folder)
        for dataset_name in datasets:
            arguments = chosen_format.PrepareRunningMethod(method, folder, dataset_name)
            
            if run_file_path.endswith('.py'):
                # Use the same Python interpreter which runs this script to run
                # the run.py script.
                program_with_arguments = [sys.executable, run_file_path]
            else:
                program_with_arguments = [run_file_path]
            
            program_with_arguments.append(method)
            program_with_arguments.extend(arguments)
            program_with_arguments.extend(additional_arguments)
            print('Running: ' + ' '.join(program_with_arguments))
            proc = subprocess.Popen(program_with_arguments)
            return_code = proc.wait()
            del proc
            if return_code != 0:
                print('Algorithm call failed (return code: ' + str(return_code) + ')')
                return False


def DevkitMain(task_name, benchmarks, dataset_formats):
    # Validate setup.
    if len(dataset_formats) == 0:
        raise Exception('No dataset formats defined.')
    if len(benchmarks) == 0:
        raise Exception('No benchmarks defined.')
    
    # Parse arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['obtain', 'run', 'submit'], nargs='?')
    parser.add_argument("--keep_archives", action='store_true', help='Keep the downloaded archives instead of deleting them after extraction.')
    parser.add_argument('args', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    
    # Check for existing dataset and result files.
    format_info = dict()  # Indexed by the dataset_format.
    downloaded_dataset_formats = []
    for dataset_format in dataset_formats:
        format_info[dataset_format] = dict()
        datasets_dir = DatasetsPathForFormat(dataset_format)
        format_info[dataset_format]['datasets_dir'] = datasets_dir
        
        # Check whether all datasets were downloaded in this format.
        format_info[dataset_format]['downloaded'] = (
            os.path.isdir(datasets_dir) and
            all([os.path.isfile(os.path.join(MetadataPath(datasets_dir), GetMetaDataFilename(benchmark))) for benchmark in benchmarks]))
        if format_info[dataset_format]['downloaded']:
            downloaded_dataset_formats.append(dataset_format)
        
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
                DeterminePossibleSubmissions(task_name,
                                             TrainingDatasetsPath(format_info[dataset_format]['datasets_dir']),
                                             TestDatasetsPath(format_info[dataset_format]['datasets_dir']),
                                             dataset_format,
                                             benchmarks))
            format_info[dataset_format]['training_submission_methods'] = training_submission_methods
            format_info[dataset_format]['full_submission_methods'] = full_submission_methods
    
    # Command line interface:
    if args.command == 'obtain':
        if len(dataset_formats) == 1:
            chosen_format = dataset_formats[0]
        elif len(args.args) == 0:
            print('Please specify the dataset format.')
            sys.exit(1)
        else:
            chosen_format = ParseFormatNameOrExit(args.args[0], dataset_formats)
        
        if format_info[chosen_format]['downloaded']:
            print('Error: the datasets were already downloaded in this format. Delete the folder first in case you would like to re-download them.')
            sys.exit(1)
        
        datasets_dir_path = DatasetsPathForFormat(chosen_format)
        DownloadAndConvertDatasets(chosen_format,
                                   dataset_formats,
                                   args.keep_archives,
                                   MetadataPath(datasets_dir_path),
                                   TrainingDatasetsPath(datasets_dir_path),
                                   TestDatasetsPath(datasets_dir_path),
                                   benchmarks)
        sys.exit(0)
    elif args.command == 'run':
        arguments = args.args
        if len(arguments) < 2:
            print('Too few program arguments given.')
            sys.exit(1)
        elif len(downloaded_dataset_formats) == 0:
            print('Cannot run an algorithm since no datasets were downloaded yet.')
            sys.exit(1)
        elif len(downloaded_dataset_formats) == 1:
            chosen_format = downloaded_dataset_formats[0]
        elif len(downloaded_dataset_formats) > 1:
            chosen_format = ParseFormatNameOrExit(arguments[0], dataset_formats)
            arguments = arguments[1:]
        
        if len(arguments) < 2:
            print('Too few program arguments given.')
            sys.exit(1)
        
        run_file_path = arguments[0]
        method = arguments[1]
        training_only = len(arguments) >= 3 and arguments[2] == '--training'
        additional_arguments = arguments[(3 if training_only else 2):]
        
        if not os.path.isfile(run_file_path):
            print('Cannot find a file at the given runfile path: ' + run_file_path)
            sys.exit(1)
        
        RunMethod(method, run_file_path, chosen_format, training_only, additional_arguments)
        sys.exit(0)
    elif args.command == 'submit':
        arguments = args.args
        if len(arguments) < 1:
            print('Too few program arguments given.')
            sys.exit(1)
        elif len(downloaded_dataset_formats) == 0:
            print('Cannot create archives since no datasets were downloaded yet.')
            sys.exit(1)
        elif len(downloaded_dataset_formats) == 1:
            chosen_format = downloaded_dataset_formats[0]
        elif len(downloaded_dataset_formats) > 1:
            chosen_format = ParseFormatNameOrExit(arguments[0], dataset_formats)
            arguments = arguments[1:]

        method = arguments[0]
        is_training_submission = len(arguments) >= 2 and arguments[1] == '--training'
        if ((is_training_submission and not method in format_info[chosen_format]['training_submission_methods']) or
            (not is_training_submission and not method in format_info[chosen_format]['full_submission_methods'])):
            print('Cannot create archives for this method since not all required result files exist.')
            sys.exit(1)
        
        datasets_dir_path = format_info[chosen_format]['datasets_dir']
        CreateSubmissionArchives(task_name, chosen_format, dataset_formats, method,
                                 is_training_submission,
                                 MetadataPath(datasets_dir_path),
                                 TrainingDatasetsPath(datasets_dir_path),
                                 TestDatasetsPath(datasets_dir_path),
                                 benchmarks)
        sys.exit(0)
    
    
    # Interactive interface:
    
    # Output script information.
    print('--- ' + task_name.title() + ' devkit for the Robust Vision Challenge 2018 ---')
    print('')
    print('Includes the following %s segmentation benchmarks:' % task_name)
    for benchmark in benchmarks:
        print('* ' + benchmark.Name())
    print('')
    
    # If no datasets were downloaded yet, do this now.
    if not any([format_info[dataset_format]['downloaded'] for dataset_format in dataset_formats]):
        # If there is more than one format, let the user choose which one to work
        # with.
        chosen_format = ChooseDatasetFormat('Choose the dataset format to work with by entering its number:', dataset_formats)
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
        # NOTE: Offer changing options (e.g., download different resolution for Middlebury)?
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
        
        for item in os.listdir('.'):
            if os.path.isdir(item) and len(item) > len('alg-') + 1 and item.startswith('alg-'):
                method = item[len('alg-'):]
                print('  [' + str(counter) + '] Run algorithm: ' + method)
                actions.append(('run_algorithm', method, item))
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
            # NOTE: It would be more efficient to use existing downloaded files
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
            CreateSubmissionArchives(task_name, chosen_format, dataset_formats, method,
                                     is_training_submission,
                                     MetadataPath(datasets_dir_path),
                                     TrainingDatasetsPath(datasets_dir_path),
                                     TestDatasetsPath(datasets_dir_path),
                                     benchmarks)
        elif action[0] == 'run_algorithm':
            method = action[1]
            method_dir_path = action[2]
            
            # If more than one dataset format is downloaded, let the user choose which
            # format to run the method on.
            chosen_format = ChooseDatasetFormat('Choose the dataset format to run the algorithm on by entering its number:', downloaded_dataset_formats)
            datasets_dir_path = format_info[chosen_format]['datasets_dir']
            
            # Let the user choose whether to run the method on training datasets only,
            # or all datasets.
            print('Run the algorithm only on training datasets [t], or on all datasets [a]?')
            while True:
                response = GetUserInput("> ")
                if response == 't' or response == 'a':
                    print('')
                    training_only = (response == 't')
                    break
                else:
                    print('Please enter t or a.')
            
            print('Enter the method name (default if empty: ' + method + '):')
            response = GetUserInput("> ")
            if len(response) > 0:
                method = response
            
            print('Enter additional arguments to pass to the run file (if any):')
            additional_arguments = GetUserInput("> ").split(' ')
            
            run_file_path = os.path.join(method_dir_path, 'run')
            if not os.path.isfile(run_file_path):
                run_file_path = run_file_path + '.py'
                if not os.path.isfile(run_file_path):
                    raise Exception('Cannot find run or run.py in the algorithm\'s directory.')
            
            RunMethod(method, run_file_path, chosen_format, training_only, additional_arguments)
        else:
            raise Exception('Internal error: invalid action.')
