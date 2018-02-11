#!/usr/bin/env python
# Collects left and right RGB images for all KITTI depth maps (training split)

import argparse
import os
import glob
import shutil
import sys


def main():
    parser = argparse.ArgumentParser(description='Downloads ScanNet public data release.')
    parser.add_argument('-d', '--depth_map_base', default='../datasets_KITTI/train',
                        help='directory in which to search for generated depth maps')
    parser.add_argument('-r', '--raw_kitti_base', default='../raw_data_KITTI',
                        help='directory in which to search for KITTI raw RGB images')
    parser.add_argument('-t', '--type', required=True, choices=('move', 'copy', 'softlink', 'txt'),
                        help='select the way RGB images are gathered, e.g. copy raw RGB images to '
                             + 'their corresponding location (image_02, image_03) in KITTI depth '
                             + 'or generate a txt file containing matching names for depth maps and'
                             + 'images (\'move\',\'copy\',\'softlink\',\'txt\')')
    parser.add_argument('-o', '--out_txt_prefix', default='kitti_train',
                        help='if \'txt\' selected as type, this defines the prefix of the output')
    parser.add_argument('-f', '--force_override', action='store_true',
                        help='override existing links or files at new location')
    args = parser.parse_args()

    # search for depth maps
    depth_search = "2011_*_*_drive_*_sync/proj_depth/groundtruth/image_0[2,3]/*.png"
    depth_files = sorted(glob.glob(os.path.join(args.depth_map_base, depth_search)))
    num_depth_files = len(depth_files)
    num_train_files = 85898
    num_val_files = 6852
    if num_depth_files != num_train_files and num_depth_files != num_val_files and \
       num_depth_files != num_train_files + num_val_files:
        print "WARNING: Found {} depth maps, which is not a usual number ".format(num_depth_files) \
            + "of files, e.g. {} for train and {} ".format(num_train_files, num_val_files) \
            + "for val or {} for both".format(num_train_files + num_val_files)
        print "You most likely have an incomplete dataset. Press any key to continue anyway."
        raw_input()
    else:
        print "INFO: Found {} depth maps.".format(len(depth_files))

    # search for RGB images
    image_search = "2011_*_*/2011_*_*_drive_*_sync/image_0[2,3]/data/*.png"
    image_files = sorted(glob.glob(os.path.join(args.raw_kitti_base, image_search)))
    if len(image_files) == 0:
        # peoply might have split the data into city, residential, campus, ...
        image_files = sorted(glob.glob(os.path.join(args.raw_kitti_base, "*", image_search)))
    if len(image_files) == 0:
        # ..and still have the drives' dates appended ;)
        image_files = sorted(glob.glob(os.path.join(args.raw_kitti_base, "*", "2011_*_*",
                                                    image_search)))
    num_image_files = len(image_files)
    num_raw_image_files = 95778
    if num_image_files < num_depth_files or num_image_files < num_raw_image_files:
        print "WARNING: Found {} images and {} depth ".format(num_image_files, num_depth_files) \
            + "maps. KITTI raw contains {} images (left and right).".format(num_raw_image_files)
        print "You will most likely have an incomplete dataset. Press any key to continue anyway."
        raw_input()
    else:
        print "INFO: Found {} images.".format(len(image_files))

    # search for calibration files
    calib_search = "2011_*_*/calib_cam_to_cam.txt"
    calib_files = sorted(glob.glob(os.path.join(args.raw_kitti_base, calib_search)))
    if len(calib_files) == 0:
        # peoply might have split the data into city, residential, campus, ...
        calib_files = sorted(glob.glob(os.path.join(args.raw_kitti_base, "*", calib_search)))

    num_calib_files = len(calib_files)
    num_raw_calib_files = 5
    if num_calib_files < num_raw_calib_files:
        print "WARNING: Found {} calibration files. ".format(num_calib_files) \
            + "KITTI raw contains {} day-based calibrations.".format(num_raw_calib_files)
        print "You will most likely have an incomplete dataset. Press any key to continue anyway."
        raw_input()
    else:
        print "INFO: Found {} calibration files.".format(num_calib_files, calib_files)

    if args.type == "move":
        print "INFO: Moving all files from {} to {}".format(
            args.raw_kitti_base, args.depth_map_base)
    elif args.type == "copy":
        print "INFO: Copying all files from {} to {}".format(
            args.raw_kitti_base, args.depth_map_base)
    elif args.type == "softlink":
        print "INFO: Linking all files from {} to {}".format(
            args.raw_kitti_base, args.depth_map_base)
    elif args.type == "txt":
        print "INFO: Writing all files from {} and {} into {}_*.txt".format(
            args.raw_kitti_base, args.depth_map_base, args.out_txt_prefix)
        txt_out_depth = args.out_txt_prefix + "_depth_maps.txt"
        txt_out_imgs = args.out_txt_prefix + "_images.txt"
        txt_out_intrinsics = args.out_txt_prefix + "_intrinsics.txt"
        if (os.path.isfile(txt_out_depth) or os.path.isfile(txt_out_imgs)) \
           and not args.force_override:
            print "WARNING: Output text files {}, {} or ".format(txt_out_depth, txt_out_imgs) \
                  + "{} already exist. ".format(txt_out_intrinsics) \
                  + "Use -f option to override or -o to change output name."
            exit()
        txt_depth_files = []
        txt_images_files = []
        txt_intrinsic_files = []
    else:
        print "ERROR: Found unrecognized type {}".format(args.type)
        exit()

    # Iterate all depth files and find corresponding RGB images
    for img_idx, depth_fn in enumerate(depth_files):
        print "\rProgress: {0:<5}% (image: {1})".format(
            round(100. * (img_idx + 1.) / num_depth_files, 2), depth_fn),
        sys.stdout.flush()

        drive, _, _, image, frame = depth_fn.split("/")[-5:]
        date = drive[:len("yyyy_mm_dd")]
        matching_img_fn = [img_fn for img_fn in image_files if "/" + drive + "/" in img_fn
                           and "/" + image + "/" in img_fn and "/" + frame in img_fn]
        matching_calib_fn = [calib_fn for calib_fn in calib_files
                             if "/" + date + "/" + "calib_cam_to_cam.txt" in calib_fn]
        if len(matching_img_fn) <= 0:
            print "\nERROR: Could not find a corresponding RGB image for depth map " + depth_fn
            exit()
        elif len(matching_img_fn) > 1:
            print "\nWARNING: Found multiple corresponding RGB images for depth map " \
                  + "{}: {}".format(depth_fn, matching_img_fn)
        else:
            matching_img_fn = matching_img_fn[0]
        if len(matching_calib_fn) <= 0:
            print "\nERROR: Could not find a corresponding intrinsics file for {}".format(depth_fn)
            exit()
        else:
            matching_calib_fn = matching_calib_fn[0]

        with open(matching_calib_fn, "r") as f:
            for line in f:
                matrix_str = line.split(" ")[0].replace(":", "")
                if image == "image_02" and matrix_str != "P_rect_02":
                    continue
                elif image == "image_03" and matrix_str != "P_rect_03":
                    continue
                p_rect = map(float, line.strip().split(" ")[1:])
                f_x, _, o_x, _, _, f_y, o_y = p_rect[:7]

        out_intrinsic_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
                os.path.dirname(depth_fn)))), "intrinsics", image)
        if not os.path.isdir(out_intrinsic_dir):
            os.makedirs(out_intrinsic_dir)
        out_intrinsic_file = os.path.join(out_intrinsic_dir, frame.replace(".png", ".txt"))
        if os.path.isfile(out_intrinsic_file) and not args.force_override:
            print "WARNING: The intrinsic file \'{}\' already exists. ".format(out_intrinsic_file) \
                  + "Use -f option if desired."
            exit()
        with open(out_intrinsic_file, "w") as f:
            f.write("{} 0.0 {} 0.0 {} {} 0.0 0.0 1.0\n".format(f_x, o_x, f_y, o_y))

        if args.type == "txt":
            txt_depth_files.append(os.path.abspath(depth_fn))
            txt_images_files.append(os.path.abspath(matching_img_fn))
            txt_intrinsic_files.append(os.path.abspath(out_intrinsic_file))
        else:
            out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
                os.path.dirname(depth_fn)))), image)
            if not os.path.isdir(out_dir):
                os.makedirs(out_dir)
            out_file = os.path.join(out_dir, frame)
            if os.path.isfile(out_file):
                if args.force_override:
                    os.remove(out_file)
                else:
                    print "WARNING: The file/link \'{}\' already exists. ".format(out_file) + \
                          "Use -f option if desired."
                    exit()
            if args.type == "softlink":
                os.symlink(matching_img_fn, out_file)
            elif args.type == "copy":
                shutil.copyfile(matching_img_fn, out_file)
            elif args.type == "move":
                shutil.move(matching_img_fn, out_file)

    if args.type == "txt":
        with open(txt_out_depth, "w") as f:
            for depth_fn in txt_depth_files:
                f.write(depth_fn + "\n")
        with open(txt_out_imgs, "w") as f:
            for img_fn in txt_images_files:
                f.write(img_fn + "\n")
        with open(txt_out_intrinsics, "w") as f:
            for intrinsics_fn in txt_intrinsic_files:
                f.write(intrinsics_fn + "\n")


if __name__ == "__main__":
    main()
