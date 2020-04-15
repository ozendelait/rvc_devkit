import numpy as np
import imageio
import glob
import os
from raw_data_mpi_sintel.depth.sdk.python.sintel_io import depth_read
from pathlib import Path
import argparse

""" Convert the dpt files of the mpi_sintel dataset to pngs resembling
    the KITTI dataset.
"""


def parse_args():
    """ Parse the command line arguments."""
    parser = argparse.ArgumentParser(
        description='Convert the MPI Sintel dpt data to pngs')
    parser.add_argument('clamprange', type=int, default=100)
    args = parser.parse_args()
    return args


if __name__ == '__main__':

    args = parse_args()
    clamprange = args.clamprange

    print('Convert dpt to png')

    paths = glob.glob(os.getcwd(
    ) + '/datasets_mpi_sintel/train/*/proj_depth/groundtruth/image_01_dpt/*.dpt')
    for path in paths:
        depth = depth_read(path)
        depth = np.clip(depth, 0, clamprange)
        depth = depth * 256.
        depth = depth.astype(np.uint16)
        in_path = Path(path)

        new_name = int(in_path.stem.split('frame_')[-1])
        new_name = "{:0>10}".format(new_name) + '.png'
        out_path = str(in_path.parent).split('_dpt')[0] + '/' + new_name
        print('Save to', out_path)
        imageio.imwrite(out_path, depth)

    # Also rename the images
    print('Rename images')
    paths = glob.glob(
        os.getcwd() + '/datasets_mpi_sintel/train/*/image_01/frame_*.png')
    for path in paths:
        in_path = Path(path)
        new_name = int(in_path.stem.split('frame_')[-1])
        new_name = "{:0>10}".format(new_name) + '.png'

        new_path = str(in_path.parent) + '/' + new_name

        print('Rename to', new_path)
        os.rename(path, new_path)
