from PIL import Image
import glob
import os
import sys

color_img_files = sorted(glob.glob("datasets_ScanNet/scene*_*/color/*.png"))
depth_img_files = sorted(glob.glob("datasets_ScanNet/scene*_*/depth/*.png"))

for img_fn, depth_fn in zip(color_img_files, depth_img_files):
    print "\rProcessing file {}".format(img_fn),
    sys.stdout.flush()
    w_depth, h_depth = Image.open(depth_fn).size
    new_fn = img_fn.replace("color", "color_rob")
    if not os.path.isdir(os.path.dirname(new_fn)):
        os.makedirs(os.path.dirname(new_fn))
    Image.open(img_fn).resize([w_depth, h_depth]).save(new_fn)
