import argparse
import os
import sys

from SensorData import SensorData

# params
parser = argparse.ArgumentParser()
# data paths
parser.add_argument('--filename', required=True, help='path to sens file to read')
parser.add_argument('--output_path', required=True, help='path to output folder')
parser.add_argument('--export_depth_images', dest='export_depth_images', action='store_true')
parser.add_argument('--export_color_images', dest='export_color_images', action='store_true')
parser.add_argument('--export_poses', dest='export_poses', action='store_true')
parser.add_argument('--export_intrinsics', dest='export_intrinsics', action='store_true')
parser.add_argument('--rob', dest='rob_representation', action='store_true')
parser.add_argument('--full_res', dest='full_resolution', action='store_true')

opt = parser.parse_args()
print(opt)


def main():
    if not os.path.exists(opt.output_path):
        os.makedirs(opt.output_path)
    # load the data
    sys.stdout.write('loading %s...' % opt.filename)
    sd = SensorData(opt.filename)
    sys.stdout.write('loaded!\n')
    if opt.export_depth_images:
        if opt.rob_representation:
            sd.export_depth_images_rob(os.path.join(opt.output_path, 'depth_rob'))
        else:
            sd.export_depth_images(os.path.join(opt.output_path, 'depth_ScanNet'))
    if opt.export_color_images:
        if opt.rob_representation:
            if opt.full_resolution:
                sd.export_color_images_rob(os.path.join(opt.output_path, 'color_rob'))
            else:
                sd.export_color_images_rob(os.path.join(opt.output_path, 'color_rob_full_res'))
        else:
            sd.export_color_images(os.path.join(opt.output_path, 'color_ScanNet'))
    if opt.export_poses:
        sd.export_poses(os.path.join(opt.output_path, 'pose'))
    if opt.export_intrinsics:
        if opt.rob_representation:
            sd.export_intrinsics_rob(os.path.join(opt.output_path, 'intrinsic_rob'),
                                     opt.full_resolution)
        else:
            sd.export_intrinsics(os.path.join(opt.output_path, 'intrinsic_ScanNet'))


if __name__ == '__main__':
    main()
