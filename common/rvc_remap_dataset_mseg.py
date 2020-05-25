#!/usr/bin/python3
#based on https://github.com/mseg-dataset/mseg-api/blob/master/mseg/label_preparation/remap_dataset.py

import argparse, os, sys, subprocess, json
import imageio
import numpy as np
import torch
from typing import Any, List, Mapping, Tuple, Optional


from mseg.utils.multiprocessing_utils import send_list_to_workers
from mseg.utils.txt_utils import generate_all_img_label_pair_relative_fpaths
from mseg.utils.dir_utils import create_leading_fpath_dirs
from mseg.taxonomy.taxonomy_converter import TaxonomyConverter
from mseg.utils.names_utils import load_dataset_colors_arr
from mseg.utils.cv2_utils import cv2_imread_rgb
from mseg.utils.mask_utils import rgb_img_to_obj_cls_img

segmentation_rvc_subfolder = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(os.path.abspath(__file__))),"../segmentation/"))
RVC_TRAIN_DATASETS = ["ade20k-151", "kitti-34"]

#creates a symbolic link / junction at dst pointing at directory src
def unpriv_symb_link(src, dst):
	if not os.path.exists(src) or os.path.exists(dst):
		return
	parent_dir = os.path.dirname(dst)
	if not os.path.exists(parent_dir):
		os.makedirs(parent_dir)
	if sys.platform.startswith('win'): #symlinks need admin rights, junctions don't
		subprocess.check_call('mklink /J "%s" "%s"' % (dst, src), shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
	else:
		os.symlink(src, dst, target_is_directory=True)

#rvc uses in-place coco transformation
def fix_path_coco_inplace(path0):
	return path0.replace('semantic_annotations201/','annotations/panoptic_')

def remap_dataset(
	dname: str,
	tsv_fpath: str,
	old_dataroot: str,
	remapped_dataroot: str,
	panoptic_json_path: str,
	num_processes: int = 4,
	create_symlink_cpy:bool = False,
	convert_label_from_rgb: bool = False):
	"""
	Given path to a dataset, given names of _names.txt
	Remap according to the provided tsv.
	(also account for the fact that 255 is always unlabeled)

		Args:
		-	dname: string representing name of taxonomy for original dataset
		-	tsv_fpath: string representing path to a .tsv file
		-	old_dataroot: string representing path to original dataset
		-	remapped_dataroot: string representing path at which to new dataset
		-   panoptic_json_path: string representing path to coco-style json file
		-	num_processes: integer representing number of workers to exploit
		-   create_symlink_cpy: adds symbolic links for images in the same folder structure as annotations

		Returns:
		-	None
	"""
	# form one-way mapping between IDs
	tconv = TaxonomyConverter(train_datasets=[dname],test_datasets=[],tsv_fpath=tsv_fpath)
	dataset_colors = load_dataset_colors_arr(dname) if convert_label_from_rgb else None

	for split_idx,split in enumerate(['train', 'val']):
		panoptic_json_content = None
		orig_relative_img_label_pairs = generate_all_img_label_pair_relative_fpaths(dname, split)
		if not panoptic_json_path is None:
			with open(panoptic_json_path.format(split=split, split_idx=str(split_idx)), 'r') as ifile:
				json_cont = json.load(ifile)
			panoptic_json_content = {a["file_name"]:a for a in json_cont["annotations"]}
			if dname[:4] == "coco": #hacky  needed for inplace coco support
				orig_relative_img_label_pairs = [[fix_path_coco_inplace(p[0]),fix_path_coco_inplace(p[1])] for p in orig_relative_img_label_pairs]
		basedir = 'images/' + split + '/' + dname
		img_subdirs = list(set([os.path.dirname(p[0]) for p in orig_relative_img_label_pairs]))
		img_dir_remapping = {}
		for d in img_subdirs:
			img_dir_remapping[d] = basedir if len(img_subdirs) == 1 else basedir + '/' + d.replace('/color','').replace('/leftImg8bit','')
			if create_symlink_cpy:
				unpriv_symb_link(old_dataroot + '/' + d, remapped_dataroot + '/' + img_dir_remapping[d])
		remapped_relative_img_label_pairs = [
			(img_dir_remapping[os.path.dirname(p[0])]+'/'+os.path.basename(p[0]), img_dir_remapping[os.path.dirname(p[0])].replace('images','annotations')+'/'+os.path.basename(p[0]).replace('.jpg','.png')) for p in
			orig_relative_img_label_pairs]

		send_list_to_workers(
			num_processes=num_processes, 
			list_to_split=orig_relative_img_label_pairs, 
			worker_func_ptr=relabel_pair_worker,
			remapped_relative_img_label_pairs=remapped_relative_img_label_pairs,
			tax_converter=tconv,
			panoptic_json_content = panoptic_json_content,
			old_dataroot=old_dataroot,
			new_dataroot=remapped_dataroot,
			dname = dname,
			dataset_colors=dataset_colors)

def relabel_pair_worker(
	orig_pairs: List[Tuple[str,str]], 
	start_idx: int, 
	end_idx: int, 
	kwargs: Mapping[str, Any] ) -> None:
	"""	Given a list of (rgb image, label image) pairs to remap, call relabel_pair()
		on each one of them.

		Args:
		-	orig_pairs: list of strings
		-	start_idx: integer
		-	end_idx: integer
		-	kwargs: dictionary with argument names mapped to argument values

		Returns:
		-	None
	"""
	old_dataroot = kwargs['old_dataroot']
	new_dataroot = kwargs['new_dataroot']
	remapped_pairs = kwargs['remapped_relative_img_label_pairs']
	dname = kwargs['dname']
	tax_converter  = kwargs['tax_converter']
	dataset_colors = kwargs['dataset_colors']
	panoptic_json_content  = kwargs['panoptic_json_content']

	chunk_sz = end_idx - start_idx
	# process each image between start_idx and end_idx
	for idx in range(start_idx, end_idx):
		if idx % 1000 == 0:
			pct_completed = (idx-start_idx)/chunk_sz*100
			print(f'Completed {pct_completed:.2f}%')
		orig_pair = orig_pairs[idx]
		remapped_pair = remapped_pairs[idx]
		segm_to_class = None
		if not panoptic_json_content is None:
			entry =  panoptic_json_content.get(orig_pair[1], panoptic_json_content[os.path.basename(orig_pair[1])])
			segm_to_class = {s['id']:s['category_id'] for s in entry["segments_info"]}
		relabel_pair(old_dataroot, new_dataroot, orig_pair, remapped_pair, dname, tax_converter, segm_to_class, dataset_colors)

def relabel_pair(
	old_dataroot: str,
	new_dataroot: str, 
	orig_pair: Tuple[str,str], 
	remapped_pair: Tuple[str,str],
	dname: str,
	tax_converter: TaxonomyConverter,
	segm_to_class: Mapping[int, int],
	dataset_colors: Optional[np.ndarray] = None):
	"""
	No need to copy the RGB files again. We just update the label file paths.

		Args:
		-	old_dataroot:
		-	new_dataroot: 
		-	orig_pair: Tuple containing relative path to RGB image and label image
		-	remapped_pair: Tuple containing relative path to RGB image and label image
		-	label_mapping_arr: 
		-	dataset_colors:

		Returns:
		-	None
	"""
	_, orig_rel_label_fpath = orig_pair
	_, remapped_rel_label_fpath = remapped_pair

	old_label_fpath = f'{old_dataroot}/{orig_rel_label_fpath}'
	if not os.path.exists(old_label_fpath):
		print("Warning: File "+old_label_fpath+" not found!")
		return

	if dataset_colors is None:
		label_img = imageio.imread(old_label_fpath)
	else:
		# remap from RGB encoded labels to 1-channel class indices
		label_img_rgb = cv2_imread_rgb(old_label_fpath)
		label_img = rgb_img_to_obj_cls_img(label_img_rgb, dataset_colors)

	if not segm_to_class is None:
		label_img_id = label_img[:, :, 0] + (label_img[:, :, 1] * 256) + (label_img[:, :, 2] * 256 ** 2)
		label_img = np.ones(label_img.shape[:2],dtype=np.uint8)*255 #initialize with unlabeled
		for src, dst in segm_to_class.items():
			label_img[label_img_id == src] = dst

	labels = torch.tensor(label_img, dtype= torch.int64)
	remapped_img = tax_converter.transform_label(labels, dname)

	new_label_fpath = f'{new_dataroot}/{remapped_rel_label_fpath}'
	create_leading_fpath_dirs(new_label_fpath)
	remapped_img  = remapped_img.numpy().astype(dtype=np.uint8)
	imageio.imwrite(new_label_fpath, remapped_img)

if __name__ == '__main__':
	"""
	For PASCAL-Context-460, there is an explicit unlabeled class
	(class 0) so we don't include unlabeled=255 from source.
	"""
	parser = argparse.ArgumentParser()
	parser.add_argument("--orig_dname", type=str, required=True, 
		help="original dataset's name")
	parser.add_argument("--orig_dataroot", type=str, required=True, 
		help="path to original data root")
	parser.add_argument("--remapped_dataroot", type=str, required=True, 
		help="data root where remapped dataset will be saved")
	parser.add_argument("--panoptic_json", type=str, default=None,
		help="path to json containing the png segm. id -> class id mapping")
	parser.add_argument("--num_processes", type=int, default=4,
		help="Number of cores available on machine (more->faster remapping)")
	parser.add_argument("--mapping_tsv", type=str, default=os.path.join(segmentation_rvc_subfolder,'ss_mapping_uint8_mseg.tsv'),
		help="data root where remapped dataset will be saved")
	parser.add_argument("--create_symlink_cpy", action="store_true",
		help="Create symlink copy of images for relabeled dataset.")
	parser.add_argument("--convert_label_from_rgb", action="store_true",
		help="If original dataset labels are stored as RGB images.")

	args = parser.parse_args()

	print('Remapping Parameters: ', args)
	remap_dataset(
		args.orig_dname,
		args.mapping_tsv,
		args.orig_dataroot,
		args.remapped_dataroot,
		args.panoptic_json,
		args.num_processes,
		args.create_symlink_cpy,
		args.convert_label_from_rgb
	)