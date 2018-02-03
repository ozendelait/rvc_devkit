import glob
import os
import shutil

scannet_base_dir = os.path.dirname(__file__)

training_scenes = []
validation_scenes = []
test_scenes = []
rob_test_scenes = []
with open(os.path.join(scannet_base_dir, "data_splits", "scannet_train.txt"), "r") as f:
    for line in f:
        training_scenes.append(line.strip())
with open(os.path.join(scannet_base_dir, "data_splits", "scannet_val.txt"), "r") as f:
    for line in f:
        validation_scenes.append(line.strip())
with open(os.path.join(scannet_base_dir, "data_splits", "scannet_test.txt"), "r") as f:
    for line in f:
        test_scenes.append(line.strip())
with open(os.path.join(scannet_base_dir, "data_splits", "scannet_rob_test.txt"), "r") as f:
    for line in f:
        rob_test_scenes.append(line.strip())

print "Found {} scenes in training split".format(len(training_scenes))
print "Found {} scenes in validation split".format(len(validation_scenes))
print "Found {} scenes in test split".format(len(test_scenes))
print "Found {} scenes in rob_test split".format(len(rob_test_scenes))

if len(training_scenes) < 1045 or len(validation_scenes) < 156 or len(test_scenes) < 312 \
   or len(rob_test_scenes) < 80:
    print "ERROR: Did not find data split information"
    exit()

data_base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             "datasets_ScanNet")
num_scenes = len(glob.glob(os.path.join(data_base_dir, "scene*_*/")))

print "Found {} downloaded scenes in \'datasets_ScanNet\'".format(num_scenes)

if num_scenes < (len(training_scenes) + len(validation_scenes) + 
                 len(test_scenes) + len(rob_test_scenes)):
    print "ERROR: Could not find all downloaded scenes. Did something go " \
          + "wrong with the download?"
    exit()


print "WARNING: Moving all scenes in datasets_ScanNet to their respective data splits. " \
      + "Press any key to continue."
raw_input()

for scene_dir in sorted(glob.glob(os.path.join(data_base_dir, "scene*_*/"))):
    if not os.path.isdir(scene_dir):
        continue
    scene_name = os.path.basename(os.path.dirname(scene_dir))
    print scene_dir, scene_name
    if scene_name in training_scenes:
        dst_dir = os.path.join(data_base_dir, "train")
    if scene_name in validation_scenes:
        dst_dir = os.path.join(data_base_dir, "val")
    if scene_name in test_scenes:
        dst_dir = os.path.join(data_base_dir, "test")
    if scene_name in rob_test_scenes:
        dst_dir = os.path.join(data_base_dir, "rob_test")
    if not os.path.isdir(dst_dir):
        os.makedirs(dst_dir)
    print "Moving {} to {}".format(scene_dir, dst_dir)
    shutil.move(scene_dir, dst_dir)
