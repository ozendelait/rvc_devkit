from __future__ import print_function

import os
import sys
import glob
import zipfile
import argparse
import shutil
import subprocess
import colmap_util
import numpy as np

if sys.version_info[0] == 2:
    import urllib2
else:
    import urllib.request


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", required=True,
                        help="Path to folder in which to store datasets")
    parser.add_argument("--action", required=True,
                        choices=["download", "submit"],
                        help="Whether to download or prepare submission")
    parser.add_argument("--dataset", default="",
                        choices=["", "ETH3D", "Middlebury"],
                        help="Desired dataset to download or submit")
    parser.add_argument("--format", default="",
                        choices=["", "ETH3D", "Middlebury"],
                        help="Desired format in which datasets are converted")
    args = parser.parse_args()
    return args


def mkdir_if_not_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)


# In part adapted from: https://stackoverflow.com/questions/22676
def download_file(url, dest_dir_path):
    file_name = url.split('/')[-1]
    dest_file_path = os.path.join(dest_dir_path, file_name)

    url_object = None
    if sys.version_info[0] == 2:
        url_object = urllib2.urlopen(url)
    else:
        url_object = urllib.request.urlopen(url)

    meta = url_object.info()
    file_size = 0
    if sys.version_info[0] == 2:
        file_size = int(meta.getheaders("Content-Length")[0])
    else:
        file_size = int(meta["Content-Length"])
    if os.path.isfile(dest_file_path) and \
            os.stat(dest_file_path).st_size == file_size:
        print("File already downloaded:", url)
        return dest_file_path

    with open(dest_file_path, 'wb') as outfile:
        print("Downloading: %s (size [bytes]: %s)" % (url, file_size))

        file_size_downloaded = 0
        block_size = 8192
        while True:
            buffer = url_object.read(block_size)
            if not buffer:
                break

            file_size_downloaded += len(buffer)
            outfile.write(buffer)

            sys.stdout.write("%d / %d (%3f%%)\r" % (
                file_size_downloaded, file_size,
                file_size_downloaded * 100. / file_size))
            sys.stdout.flush()

    return dest_file_path


def extract_zip(file_path, unzip_dir_path):
    zip_ref = zipfile.ZipFile(open(file_path, 'rb'))
    zip_ref.extractall(unzip_dir_path)
    zip_ref.close()


def extract_7z(file_path, target_dir_path):
    subprocess.call(["7z", "x", "-o" + target_dir_path, "-aos", file_path])


def zip_directory(archive_base_path, root_dir_path):
    return shutil.make_archive(archive_base_path, 'zip', root_dir_path)


def download_and_extract_zip(url, archive_dir_path, unzip_dir_path):
    archive_path = download_file(url, archive_dir_path)
    extract_zip(archive_path, unzip_dir_path)


def download_and_extract_7z(url, archive_dir_path, unzip_dir_path):
    archive_path = download_file(url, archive_dir_path)
    extract_7z(archive_path, unzip_dir_path)


def convert_eth3d_to_middlebury(eth3d_path, middlebury_path):
    mkdir_if_not_exists(middlebury_path)

    dataset = os.path.basename(middlebury_path)

    for image_path in glob.glob(os.path.join(eth3d_path, "*/*/*.JPG")):
        shutil.copyfile(
            image_path,
            os.path.join(middlebury_path, os.path.basename(image_path)))

    cameras = colmap_util.read_cameras_text(
        os.path.join(eth3d_path, "dslr_calibration_undistorted/cameras.txt"))
    images = colmap_util.read_images_text(
        os.path.join(eth3d_path, "dslr_calibration_undistorted/images.txt"))

    with open(os.path.join(middlebury_path, dataset + "_par.txt"), "w") as fid:
        fid.write("{}\n".format(len(images)))
        for image in images.values():
            camera = cameras[image.camera_id]
            K = np.eye(3)
            K[0, 0] = camera.params[0]
            K[1, 1] = camera.params[1]
            K[0, 2] = camera.params[2]
            K[1, 2] = camera.params[3]
            R = colmap_util.qvec2rotmat(image.qvec)
            T = image.tvec
            fid.write("{} ".format(os.path.basename(image.name)))
            fid.write(" ".join(map(str, K.ravel().tolist()
                                        + R.ravel().tolist()
                                        + T.ravel().tolist())))
            fid.write("\n")


def download_eth3d(args):
    archives_path = os.path.join(args.path, "dataset_ETH3D/archives")
    training_path = os.path.join(
        args.path, "dataset_ETH3D/format_ETH3D/training")
    test_path = os.path.join(
        args.path, "dataset_ETH3D/format_ETH3D/test")

    mkdir_if_not_exists(archives_path)
    mkdir_if_not_exists(training_path)
    mkdir_if_not_exists(test_path)

    download_and_extract_7z(
        "https://www.eth3d.net/data/multi_view_training_dslr_undistorted.7z",
        archives_path, training_path)
    download_and_extract_7z(
        "https://www.eth3d.net/data/multi_view_test_dslr_undistorted.7z",
        archives_path, test_path)

    if args.format == "Middlebury":
        for dataset in os.listdir(training_path):
            convert_eth3d_to_middlebury(
                os.path.join(training_path, dataset),
                os.path.join(
                    args.path,
                    "dataset_ETH3D/format_Middlebury/training", dataset))
        for dataset in os.listdir(test_path):
            convert_eth3d_to_middlebury(
                os.path.join(test_path, dataset),
                os.path.join(
                    args.path,
                    "dataset_ETH3D/format_Middlebury/test", dataset))


def convert_middlebury_to_eth3d(middlebury_path, eth3d_path):
    mkdir_if_not_exists(eth3d_path)
    mkdir_if_not_exists(os.path.join(eth3d_path, "images"))
    mkdir_if_not_exists(os.path.join(eth3d_path, "sparse"))

    for image_path in glob.glob(os.path.join(middlebury_path, "*.png")):
        shutil.copyfile(
            image_path,
            os.path.join(eth3d_path, "images", os.path.basename(image_path)))

    cameras_file = open(os.path.join(eth3d_path, "sparse/cameras.txt"), "w")
    images_file = open(os.path.join(eth3d_path, "sparse/images.txt"), "w")
    points3D_file = open(os.path.join(eth3d_path, "sparse/points3D.txt"), "w")

    par_path = glob.glob(os.path.join(middlebury_path, "*par.txt"))[0]
    with open(par_path, "r") as fid:
        num_images = int(fid.readline())
        for image_id in range(num_images):
            data = fid.readline().strip().split()
            cameras_file.write("{} PINHOLE 640 480 {} {} {} {}\n".format(
                image_id, data[1], data[5], data[3], data[6]))
            rotmat = np.array(list(map(float, data[10:19]))).reshape(3, 3)
            qvec = colmap_util.rotmat2qvec(rotmat)
            images_file.write(" ".join(
                map(str, [image_id, qvec[0], qvec[1], qvec[2], qvec[3],
                          data[19], data[20], data[21], image_id, data[0]])))
            images_file.write("\n")
            images_file.write("\n")

    cameras_file.close()
    images_file.close()


def download_middlebury(args):
    archives_path = os.path.join(args.path, "dataset_Middlebury/archives")
    test_path = os.path.join(
        args.path, "dataset_Middlebury/format_Middlebury/test")

    mkdir_if_not_exists(archives_path)
    mkdir_if_not_exists(test_path)

    download_and_extract_zip(
        "http://vision.middlebury.edu/mview/data/data/temple.zip",
        archives_path, test_path)
    download_and_extract_zip(
        "http://vision.middlebury.edu/mview/data/data/templeRing.zip",
        archives_path, test_path)
    download_and_extract_zip(
        "http://vision.middlebury.edu/mview/data/data/templeSparseRing.zip",
        archives_path, test_path)
    download_and_extract_zip(
        "http://vision.middlebury.edu/mview/data/data/dino.zip",
        archives_path, test_path)
    download_and_extract_zip(
        "http://vision.middlebury.edu/mview/data/data/dinoRing.zip",
        archives_path, test_path)
    download_and_extract_zip(
        "http://vision.middlebury.edu/mview/data/data/dinoSparseRing.zip",
        archives_path, test_path)

    if args.format == "ETH3D":
        for dataset in os.listdir(test_path):
            convert_middlebury_to_eth3d(
                os.path.join(test_path, dataset),
                os.path.join(
                    args.path,
                    "dataset_Middlebury/format_ETH3D/test", dataset))


def submit_eth3d(args):
    submission_path = os.path.join(args.path, "dataset_ETH3D/submission")
    high_res_multi_view_path = os.path.join(
        submission_path, "high_res_multi_view")

    mkdir_if_not_exists(submission_path)
    mkdir_if_not_exists(high_res_multi_view_path)

    for dataset_type in ("training", "test"):
        path = os.path.join(args.path,
            "dataset_ETH3D/format_{}".format(args.format), dataset_type)
        for dataset_name in sorted(os.listdir(path)):
            result_paths = glob.glob(os.path.join(
                path, dataset_name, "{}.*".format(dataset_name)))
            result_file_exts = [os.path.splitext(p)[1] for p in result_paths]
            if ".txt" and ".ply" in result_file_exts:
                for result_path in result_paths:
                    shutil.copyfile(result_path, os.path.join(
                        high_res_multi_view_path,
                        os.path.basename(result_path)))
            else:
                print("Warning: Incomplete submission for dataset {} - "
                      "expected files {}.txt and {}.ply".format(
                          dataset_name, dataset_name, dataset_name))

    subprocess.call(["7za", "a", "-t7z", "high_res_multi_view.7z",
                     "high_res_multi_view"], cwd=submission_path,
                     stdout=open(os.devnull, 'w'))

    shutil.rmtree(high_res_multi_view_path)

    print("ETH3D submission files at", submission_path)
    print(" => This .7z archive must be uploaded to https://www.eth3d.net/")


def submit_middlebury(args):
    submission_path = os.path.join(args.path, "dataset_Middlebury/submission")

    mkdir_if_not_exists(submission_path)

    path = os.path.join(
        args.path, "dataset_Middlebury/format_{}".format(args.format), "test")

    for dataset_name in sorted(os.listdir(path)):
        result_path = os.path.join(
            path, dataset_name, "{}.ply".format(dataset_name))
        if os.path.exists(result_path):
            shutil.copyfile(result_path, os.path.join(
                submission_path, os.path.basename(result_path)))
        else:
            print("Warning: No results found for", dataset_name,
                  "- expected file {}.ply".format(dataset_name))


    print("Middlebury submission files at", submission_path)
    print(" => You must add your last name as a prefix to the PLY files, e.g.,")
    print("    `author_dino.ply` and then send the zipped submission folder ")
    print("    to scharr (at) middlebury.edu. If possible, please post your ")
    print("    zip file on the web in a publicly readable directory, and ")
    print("    provide the URL of this directory in your email. For ")
    print("    preliminary results, we can create a private results page, ")
    print("    but we ask that you eventually submit your results to the ")
    print("    official results page. Once you do, please let us know, for ")
    print("    each data set, the run-time, processor type, and CPU speed. ")
    print("    Also please provide the bibliographical reference information ")
    print("    of the accompanying paper so we can properly cite your method. ")
    print("    If you want to post the results of an anonymous conference ")
    print("    submission, we will cite the method as anonymous and refer ")
    print("    to it by the title of the paper. However, please still follow ")
    print("    the above naming scheme for your files - but rest assured that ")
    print("    your name will remain hidden. :) Once you know the official ")
    print("    status of your paper, please let us know and we will update ")
    print("    the results page.")


def main():
    args = parse_args()

    if args.action == "download":
        if args.dataset in ("", "ETH3D"):
            download_eth3d(args)
        if args.dataset in ("", "Middlebury"):
            download_middlebury(args)
    elif args.action == "submit":
        if args.dataset in ("", "ETH3D"):
            if args.format == "":
                reset_format = True
                args.format = "ETH3D"
            else:
                reset_format = False
            submit_eth3d(args)
            if reset_format:
                args.format = ""
        if args.dataset in ("", "Middlebury"):
            if args.format == "":
                reset_format = True
                args.format = "Middlebury"
            else:
                reset_format = False
            submit_middlebury(args)
            if reset_format:
                args.format = ""


if __name__ == "__main__":
    main()
