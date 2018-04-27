from PIL import Image
import glob
import os
import sys

w_depth = 640
h_depth = 480

color_img_files = sorted(glob.glob("datasets_ScanNet/scene*_*/color/*.jpg"))

for img_fn in color_img_files:
    print "\rProcessing file {}".format(img_fn),
    sys.stdout.flush()
    new_fn = img_fn.replace("color", "color_rob")
    if not os.path.isdir(os.path.dirname(new_fn)):
        os.makedirs(os.path.dirname(new_fn))
    Image.open(img_fn).resize([w_depth, h_depth]).save(new_fn)
