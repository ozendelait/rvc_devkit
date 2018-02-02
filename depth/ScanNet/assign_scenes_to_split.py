import glob
import os
import shutil

scannet_base_dir = os.path.dirname(__file__)

training_scenes = []
validation_scenes = []
test_scenes = []
with open(os.path.join(scannet_base_dir, "data_splits", "scannet_train.txt"), "r") as f:
    for line in f:
        training_scenes.append(line.strip())
with open(os.path.join(scannet_base_dir, "data_splits", "scannet_val.txt"), "r") as f:
    for line in f:
        validation_scenes.append(line.strip())
with open(os.path.join(scannet_base_dir, "data_splits", "scannet_test.txt"), "r") as f:
    for line in f:
        test_scenes.append(line.strip())

print "Found {} scenes in training set".format(len(training_scenes))
print "Found {} scenes in validation set".format(len(validation_scenes))
print "Found {} scenes in test set".format(len(test_scenes))

if len(training_scenes) < 1045 or len(validation_scenes) < 156 or len(test_scenes) < 312:
    print "ERROR: Did not find data split information"
    exit()

data_base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             "datasets_ScanNet")
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
    if not os.path.isdir(dst_dir):
        os.makedirs(dst_dir)
    print "Moving {} to {}".format(scene_dir, dst_dir)
    raw_input()
    shutil.move(scene_dir, dst_dir)
