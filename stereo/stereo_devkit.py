#!/usr/bin/env python

# Main file of devkit for the stereo task of the Robust Vision Challenge 2018.

import argparse
import os
import sys

from benchmark import *
from benchmark_eth3d import *
from benchmark_hci import *
from benchmark_kitti2015 import *
from benchmark_middlebury2014 import *
from util import *


def GetBenchmarkFromDatasetDirName(dir_name, benchmarks):
    benchmark = None
    for candidate in benchmarks:
        if dir_name.startswith(candidate.Prefix()):
            benchmark = candidate
            break
    if benchmark is None:
        raise Exception('Cannot determine the benchmark for dataset: ' + dir_name)
    return benchmark


def DeterminePossibleSubmissions(training_dir_path, test_dir_path, training_submission_methods, full_submission_methods, benchmarks):
    # Complete results must provide the following files for each relevant
    # dataset (according to the category, see above):
    # * disp0SUFFIX.pfm
    # * timeSUFFIX.txt
    # Here, SUFFIX is an arbitrary suffix that identifies the method.
    
    # Flags whether a dataset required for one of the categories above has
    # already been checked. If a flag is set, no method which only occurs
    # in subsequent datasets can be complete anymore.
    checked_required_training_dataset = False
    checked_required_full_dataset = False
    
    for benchmark_and_dataset_name in os.listdir(training_dir_path):
        dataset_path = os.path.join(training_dir_path, benchmark_and_dataset_name)
        if not os.path.isdir(dataset_path):
            continue
        
        benchmark = GetBenchmarkFromDatasetDirName(benchmark_and_dataset_name, benchmarks)
        
        # If results on this dataset are required for training submissions,
        # keep only those methods in the training submission list which
        # have results on the dataset.
        is_required_training_dataset = benchmark.SupportsTrainingDataOnlySubmissions()
        if is_required_training_dataset:
            training_submission_methods = [method for method in training_submission_methods
                                            if os.path.isfile(os.path.join(dataset_path, 'disp0' + method + '.pfm')) and
                                              os.path.isfile(os.path.join(dataset_path, 'time' + method + '.txt'))]
        
        # If results on this dataset are required for full submissions,
        # keep only those methods in the full submission list which
        # have results on the dataset.
        is_required_full_dataset = benchmark.SupportsTrainingDataInFullSubmissions()
        if is_required_full_dataset:
            full_submission_methods = [method for method in full_submission_methods
                                        if os.path.isfile(os.path.join(dataset_path, 'disp0' + method + '.pfm')) and
                                          os.path.isfile(os.path.join(dataset_path, 'time' + method + '.txt'))]
        
        # If this is the first dataset which is required for training or
        # full submission, collect the available methods.
        if ((is_required_training_dataset and not checked_required_training_dataset) or
            (is_required_full_dataset and not checked_required_full_dataset)):
            for filename in os.listdir(dataset_path):
                if filename.startswith('time') and filename.endswith('.txt'):
                    method = filename[4:-4]  # Strip 'time' and '.txt'
                    if os.path.isfile(os.path.join(dataset_path, 'disp0' + method + '.pfm')):
                        if is_required_training_dataset and not checked_required_training_dataset:
                            training_submission_methods.append(method)
                        if is_required_full_dataset and not checked_required_full_dataset:
                            full_submission_methods.append(method)
        
        if is_required_training_dataset:
            checked_required_training_dataset = True
        if is_required_full_dataset:
            checked_required_full_dataset = True
    
    for benchmark_and_dataset_name in os.listdir(test_dir_path):
        dataset_path = os.path.join(test_dir_path, benchmark_and_dataset_name)
        if not os.path.isdir(dataset_path):
            continue
        
        benchmark = GetBenchmarkFromDatasetDirName(benchmark_and_dataset_name, benchmarks)
        
        # Keep only those methods in the full submission list which have
        # results on the dataset.
        full_submission_methods = [method for method in full_submission_methods
                                    if os.path.isfile(os.path.join(dataset_path, 'disp0' + method + '.pfm')) and
                                        os.path.isfile(os.path.join(dataset_path, 'time' + method + '.txt'))]
        
        # If this is the first dataset which is required for full
        # submission, collect the available methods.
        if not checked_required_full_dataset:
            for filename in os.listdir(dataset_path):
                if filename.startswith('time') and filename.endswith('.txt'):
                    method = filename[4:-4]  # Strip 'time' and '.txt'
                    if os.path.isfile(os.path.join(dataset_path, 'disp0' + method + '.pfm')):
                        full_submission_methods.append(method)
        
        checked_required_full_dataset = True


def DownloadAndConvertDatasets(args, archive_dir_path, unpack_dir_path, datasets_dir_path, training_dir_path, test_dir_path, benchmarks):
    print('The datasets will be downloaded into the current working directory:')
    print('  ' + os.getcwd())
    print('')
    
    # TODO:
    #print('Choose the output dataset format by entering m or k:')
    #print('  [m] Middlebury 2014 Stereo format ( see http://vision.middlebury.edu/stereo/data/scenes2014/ )')
    #print('  [k] Kitti 2015 Stereo format ( see http://www.cvlibs.net/datasets/kitti/eval_scene_flow.php?benchmark=stereo )')
    #output_format = ''
    #while True:
        #response = GetUserInput("> ")
        #if response == 'm' or response == 'k':
            #output_format = response
            #break
        #else:
            #print('Please enter m or k.')
    
    # Get options
    for benchmark in benchmarks:
        benchmark.GetOptions()
    
    # Download and convert to Middlebury format
    MakeDirsExistOk(archive_dir_path)
    MakeCleanDirectory(unpack_dir_path)
    MakeDirsExistOk(datasets_dir_path)
    MakeDirsExistOk(training_dir_path)  
    MakeDirsExistOk(test_dir_path)  
    
    for benchmark in benchmarks:
        benchmark_archive_dir = os.path.join(archive_dir_path, benchmark.Prefix() + "archives")
        MakeDirsExistOk(benchmark_archive_dir)
        benchmark.DownloadAndConvert(benchmark_archive_dir, unpack_dir_path, datasets_dir_path, training_dir_path, test_dir_path)
    
    # Clean up unpack and archive directories
    shutil.rmtree(unpack_dir_path)
    if not args.keep_archives:
        shutil.rmtree(archive_dir_path)
    
    # If Kitti format was requested, convert all datasets from Middlebury to Kitti.
    # TODO
    
    print('')
    print('Done! The datasets are in:')
    print(training_dir_path)
    print('and')
    print(test_dir_path)


def CreateSubmissionArchives(method, training_only, datasets_dir_path, training_dir_path, test_dir_path, benchmarks):
    submission_dir_path = 'submission_archives'
    MakeDirsExistOk(submission_dir_path)
    
    pack_dir_path = 'temp_pack_dir'
    MakeCleanDirectory(pack_dir_path)
    
    archive_website_mapping = []
    
    for benchmark in benchmarks:
        if training_only and not benchmark.SupportsTrainingDataOnlySubmissions():
            continue
        
        # Determine the paths to the required datasets.
        training_dataset_names = []
        if ((training_only and benchmark.SupportsTrainingDataOnlySubmissions()) or
            (not training_only and benchmark.SupportsTrainingDataInFullSubmissions())):
            for benchmark_and_dataset_name in os.listdir(training_dir_path):
                if benchmark_and_dataset_name.startswith(benchmark.Prefix()):
                    training_dataset_names.append(benchmark_and_dataset_name)
        
        test_dataset_names = []
        if not training_only:
            for benchmark_and_dataset_name in os.listdir(test_dir_path):
                if benchmark_and_dataset_name.startswith(benchmark.Prefix()):
                    test_dataset_names.append(benchmark_and_dataset_name)
        
        archive_name = benchmark.CreateSubmissionArchive(
            method, training_dataset_names, test_dataset_names,
            datasets_dir_path, training_dir_path, test_dir_path, pack_dir_path,
            os.path.join(submission_dir_path, benchmark.Prefix() + method))
        archive_website_mapping.append((archive_name, benchmark.Website()))
    
    shutil.rmtree(pack_dir_path)
    
    print('')
    print('Done! The submission archives are in:')
    print(submission_dir_path)
    print('')
    print('As the next step, submit the archives on the following websites:')
    for pair in archive_website_mapping:
        print('  ' + pair[0] + ' on ' + pair[1])
    print('')
    print('Finally, the submission must be completed by filling a short form on the Robust Vision Challenge website: TODO')  # TODO: Insert URL


def main():
    # Parse arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument("--keep_archives", action='store_true', help='Keep the downloaded archives instead of deleting them after extraction.')
    args = parser.parse_args()
    
    # Define the list of benchmarks supported by this script (in the order in
    # which they are listed on http://www.robustvision.net/index.php).
    benchmarks = [Middlebury2014(), Kitti2015(), ETH3D2017(), HCI2016()]
    
    # Define paths.
    datasets_dir_path = 'datasets'                                  # Folder containing the training and test folders
    training_dir_path = os.path.join(datasets_dir_path, 'training') # All training datasets are placed here
    test_dir_path = os.path.join(datasets_dir_path, 'test')         # All test datasets are placed here
    
    archive_dir_path = 'archives'                                   # Folder for downloading archives into
    unpack_dir_path = 'temp_unpack_dir'                             # Folder for unpacking archives into
    
    
    # Output script information.
    print('--- Stereo devkit for the Robust Vision Challenge 2018 ---')
    print('')
    print('Includes the following benchmarks:')
    for benchmark in benchmarks:
        print('  ' + benchmark.Name())
    print('')
    
    # Check whether the datasets were downloaded already.
    datasets_exist = os.path.isdir(training_dir_path) and os.path.isdir(test_dir_path)
    training_submission_methods = []
    full_submission_methods = []
    if datasets_exist:
        # Check whether results exist which could be submitted, for two categories:
        # * training-only submissions (might only be supported by some benchmarks)
        # * full submissions
        # We do not offer test-data only submissions (some benchmarks even
        # require to submit both training and test results).
        DeterminePossibleSubmissions(training_dir_path, test_dir_path,
                                     training_submission_methods,
                                     full_submission_methods,
                                     benchmarks)
    
    # Choose an action.
    if not datasets_exist:
        DownloadAndConvertDatasets(args, archive_dir_path, unpack_dir_path, datasets_dir_path, training_dir_path, test_dir_path, benchmarks)
    else:
        # TODO: Offer dataset conversion to another format?
        # TODO: Offer changing options (download different resolution for Middlebury)?
        if len(training_submission_methods) == 0 and len(full_submission_methods) == 0:
            print('No complete training or full submission to all benchmarks is possible given the existing result files.')
            print('Make sure that all required files exist.')
        else:
            method = ''
            submission_type = ''
            if len(training_submission_methods) + len(full_submission_methods) == 1:
                if len(training_submission_methods) > 0:
                    submission_type = 'training'
                    method = training_submission_methods[0]
                else:
                    submission_type = 'full'
                    method = full_submission_methods[0]
                
                print('Complete results are available for a ' + submission_type + ' submission of method "' + method + '"')
                print('Please confirm creating these submission archives by entering y:')
                while True:
                    response = GetUserInput("> ")
                    if response == 'y':
                        break
            else:
                print('Choose a method to create submission archives for:')
                counter = 1
                if len(full_submission_methods) > 0:
                    print('Full submissions:')
                    for method in full_submission_methods:
                        print('  [' + str(counter) + ']' + method)
                        counter += 1
                if len(training_submission_methods) > 0:
                    print('Training submissions:')
                    for method in training_submission_methods:
                        print('  [' + str(counter) + ']' + method)
                        counter += 1
                
                print('Enter the number of the submission to create:')
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
                            break
                
                if choice <= len(full_submission_methods):
                    method = full_submission_methods[choice - 1]
                    submission_type = 'full'
                else:
                    method = training_submission_methods[choice - 1 - len(full_submission_methods)]
                    submission_type = 'training'
            
            CreateSubmissionArchives(method, submission_type == 'training', datasets_dir_path, training_dir_path, test_dir_path, benchmarks)


if __name__ == '__main__':
    main()
