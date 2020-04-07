#!/bin/bash

# This tool downloads the KITTI and MPI Sintel Datasets
# Execute this script from the rvc_devkit/depth directory

### Default vars
clamprange=100


### End Default vars



### Functions ###

display_help()
{
    echo "This tool provides an easy way to download and arange the KITTI and MPI Sintel Datasets"
    echo "for the use in the benchmark"
    echo "For further information about the KITTI dataset please read the provided README."
    echo "Please note that this tool must be run from the rvc_devkit/depth directory in order to properly arange the datasets"
    echo "The RabbitAI dataset must be downloaded manually."
    echo "We additionally decided that this tool does not remove any data except in the "
    echo "raw_data_downloader.sh script that is provided by Kitti."
    echo "The Data provided by MPI Sintel is clamped at a range which can be specified by the "
    echo "--clamprange parameter (in m). The default is 100m."
    echo "This is in order to make the dataset resembling the KITTI dataset."
    echo "Options:"
    echo "--clamprange         Range in m at which to clamp the data"
    echo "You need to install the imageio python package."

}


download_kitti()
{
    echo "Downloading the Kitti Data"
    # Download the KITTI Dataset
    wget -nc -P datasets_KITTI https://s3.eu-central-1.amazonaws.com/avg-kitti/data_depth_annotated.zip
    unzip -d datasets_KITTI datasets_KITTI/data_depth_annotated.zip

    cd raw_data_KITTI && bash raw_data_downloader.sh && cd ..

    wget -nc -P datasets_KITTI https://s3.eu-central-1.amazonaws.com/avg-kitti/data_depth_selection.zip
    unzip datasets_KITTI/data_depth_selection.zip -d datasets_KITTI/
}

arange_kitti()
{
    echo "Aranging the Kitti Dataset"
    # Get the relevant data from the raw dataset to the datasets_KITTI directory
    mv datasets_KITTI/depth_selection/val_selection_cropped datasets_KITTI/val_selection
    mv datasets_KITTI/depth_selection/test_depth_prediction_anonymous datasets_KITTI/test
    python2 KITTI/gather_raw_images.py -d datasets_KITTI/train -r raw_data_KITTI/ -t copy -o kitti_train
    python2 KITTI/gather_raw_images.py -d datasets_KITTI/val -r raw_data_KITTI/ -t copy -o kitti_val
    rmdir datasets_KITTI/depth_selection
}

download_mpi_sintel()
{
    echo "Downloading the MPI Sintel Dataset"
    # Create a directory containing the raw dataset
    mkdir $(pwd)/raw_data_mpi_sintel

    wget -nc -P $(pwd)/raw_data_mpi_sintel http://files.is.tue.mpg.de/jwulff/sintel/MPI-Sintel-depth-training-20150305.zip
    unzip -d $(pwd)/raw_data_mpi_sintel/depth $(pwd)/raw_data_mpi_sintel/MPI-Sintel-depth-training-20150305.zip

    # Get the images of the training set
    wget -nc -P $(pwd)/raw_data_mpi_sintel http://files.is.tue.mpg.de/sintel/MPI-Sintel-training_images.zip
    unzip -d $(pwd)/raw_data_mpi_sintel/images $(pwd)/raw_data_mpi_sintel/MPI-Sintel-training_images.zip

}

arange_mpi_sintel()
{
    # Create a directory containing the structured dataset
    mkdir $(pwd)/datasets_mpi_sintel

    echo "Arranging the MPI Sintel Dataset"
    # Now copy the important data to the datasets folder
    cp -r $(pwd)/raw_data_mpi_sintel/depth/training $(pwd)/datasets_mpi_sintel/train
    cp -r $(pwd)/raw_data_mpi_sintel/images/training/final $(pwd)/datasets_mpi_sintel/train/images

    paths=$(find $(pwd)/datasets_mpi_sintel/train/depth -mindepth 1 -maxdepth 1 -type d -iname "*" )

    for path in $paths
    do
        echo $path
        scene=$(basename $path)
        mkdir $(pwd)/datasets_mpi_sintel/train/$scene
        mkdir -p $(pwd)/datasets_mpi_sintel/train/${scene}/proj_depth/groundtruth/image_01_dpt
        mkdir -p $(pwd)/datasets_mpi_sintel/train/${scene}/proj_depth/groundtruth/image_01
        mv $path/*.dpt $(pwd)/datasets_mpi_sintel/train/${scene}/proj_depth/groundtruth/image_01_dpt/
        rmdir $path
        mv $(pwd)/datasets_mpi_sintel/train/images/$scene $(pwd)/datasets_mpi_sintel/train/${scene}/image_01
        mv $(pwd)/datasets_mpi_sintel/train/camdata_left/$scene $(pwd)/datasets_mpi_sintel/train/${scene}/camdata_left
        mv $(pwd)/datasets_mpi_sintel/train/depth_viz/$scene $(pwd)/datasets_mpi_sintel/train/${scene}/depth_viz

    done

    rmdir $(pwd)/datasets_mpi_sintel/train/depth
    rmdir $(pwd)/datasets_mpi_sintel/train/images
    rmdir $(pwd)/datasets_mpi_sintel/train/depth_viz
    rmdir $(pwd)/datasets_mpi_sintel/train/camdata_left


}


main()
{
    if [ ! $(basename $(pwd)) = "depth" ]
    then
        echo "Run this program from the /rvc_devkit/depth directory"
    fi

    download_kitti

    arange_kitti

    download_mpi_sintel

    arange_mpi_sintel

    python3 convert_dpt_to_png.py $clamprange

    echo "Done"
}




### END Functions


while [ "$1" != "" ]; do
    case $1 in
        --clamprange )          shift
                                clamprange=$1
                                ;;
        -h | --help )           shift
                                display_help
                                exit
                                ;;
        * )                     echo "Unknown Command line Option $1, Use -h to view help"
                                exit 1
                                ;;
    esac
    shift
done

main

