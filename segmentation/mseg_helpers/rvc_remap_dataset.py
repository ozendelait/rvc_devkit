#!/usr/bin/python3
#based on https://github.com/mseg-dataset/mseg-api/blob/master/mseg/label_preparation/remap_dataset.py

import argparse, os, sys, subprocess, json
import imageio
import numpy as np
import torch
from typing import Any, List, Mapping, Tuple


from mseg.utils.multiprocessing_utils import send_list_to_workers
from mseg.utils.txt_utils import generate_all_img_label_pair_relative_fpaths
from mseg.utils.dir_utils import create_leading_fpath_dirs
from mseg.taxonomy.taxonomy_converter import TaxonomyConverter

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


def remap_dataset(
	dname: str,
	tsv_fpath: str,
	old_dataroot: str,
	remapped_dataroot: str,
	panoptic_json: str,
	num_processes: int = 4,
    create_symlink_cpy = False):
	"""
	Given path to a dataset, given names of _names.txt
	Remap according to the provided tsv.
	(also account for the fact that 255 is always unlabeled)

		Args:
		-	dname: string representing name of taxonomy for original dataset
		-	tsv_fpath: string representing path to a .tsv file
		-	old_dataroot: string representing path to original dataset
		-	remapped_dataroot: string representing path at which to new dataset
		-   panoptic_json: string representing path to coco-style json file
		-	num_processes: integer representing number of workers to exploit
		-   create_symlink_cpy: adds symbolic links for images in the same folder structure as annotations

		Returns:
		-	None
	"""
	# form one-way mapping between IDs
	tconv = TaxonomyConverter(train_datasets=[dname],test_datasets=[],tsv_fpath=tsv_fpath)
	for split in ['train', 'val']:
		orig_relative_img_label_pairs = generate_all_img_label_pair_relative_fpaths(dname, split)
		basedir = 'images/' + split + '/' + dname
		img_subdirs = list(set([os.path.dirname(p[0]) for p in orig_relative_img_label_pairs]))
		img_dir_remapping = {}
		for d in img_subdirs:
			img_dir_remapping[d] = basedir if len(img_subdirs) == 1 else basedir + '/' + d.replace('/color','')
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
			old_dataroot=old_dataroot,
			new_dataroot=remapped_dataroot,
			dname = dname)

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

	chunk_sz = end_idx - start_idx
	# process each image between start_idx and end_idx
	for idx in range(start_idx, end_idx):
		if idx % 1000 == 0:
			pct_completed = (idx-start_idx)/chunk_sz*100
			print(f'Completed {pct_completed:.2f}%')
		orig_pair = orig_pairs[idx]
		remapped_pair = remapped_pairs[idx]
		relabel_pair(old_dataroot, new_dataroot, orig_pair, remapped_pair, dname, tax_converter)


def relabel_pair(
	old_dataroot: str,
	new_dataroot: str, 
	orig_pair: Tuple[str,str], 
	remapped_pair: Tuple[str,str],
	dname: str,
	tax_converter: TaxonomyConverter):
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

	label_img = imageio.imread(old_label_fpath)
	labels = torch.tensor(label_img, dtype= torch.int64)
	remapped_img = tax_converter.transform_label(labels, dname)

	new_label_fpath = f'{new_dataroot}/{remapped_rel_label_fpath}'
	create_leading_fpath_dirs(new_label_fpath)
	remapped_img  = remapped_img.numpy().astype(dtype=np.uint8)
	imageio.imwrite(new_label_fpath, remapped_img)

#tool called once per dataset and is added to mseg repo
def json_to_namestxt(json_path, new_name, trg_root_dir, count_classes = True):
	with open(json_path, 'r') as ifile:
		loadedj = json.load(ifile)

	if count_classes:
		colors = {}
		names = {}
		for id0, lab0 in enumerate(loadedj["categories"]):
			id0 = int(lab0["id"])
			names[id0] = lab0["name"]
			colors[id0] = lab0["color"]
		maxnum = max(names.keys())+1
		if not "unlabeled" in names.values():
			maxnum+=1 #add one entry for unlabeled
		trg_dir = os.path.join(trg_root_dir, new_name+"-%i"%maxnum)
		if not os.path.exists(trg_dir):
			os.makedirs(trg_dir)
		names = [names.get(i,"unlabeled") for i in range(maxnum)]
		colors = [colors.get(i,[0,0,0]) for i in range(maxnum)]
		with open(os.path.join(trg_dir, new_name+"-%i_names.txt"%maxnum),'w', newline='\n') as savename:
			savename.write('\n'.join(names) + '\n')
		with open(os.path.join(trg_dir, new_name+"-%i_colors.txt"%maxnum),'w', newline='\n') as savecol:
			savecol.write('\n'.join(['%i %i %i'%(c[0],c[1],c[2]) for c in colors]) + '\n')
	else:
		trg_dir = trg_root_dir

	fn_images = {i['id']: i['file_name'] for i in loadedj["images"]}
	annots = {}
	subdirs_total = json_path.replace('\\','/').split('/')[:-1]
	subdir_add_both = "" if subdirs_total[-1] == new_name else '/'.join(subdirs_total[subdirs_total.index(new_name)+1:])+'/'
	subdir_annot = subdir_add_both+os.path.basename(json_path).replace(".json","")+'/'
	subdir_img = subdir_add_both+'images/'
	needs_added_folder = (new_name == "viper") #needs folder before underscore
	if not os.path.exists(subdir_img):
		subdir_img = subdir_add_both + 'img/'
	for a in loadedj["annotations"]:
		added_folder = ""
		if needs_added_folder:
			added_folder = a["file_name"].split('_')[0]+'/'
		a_fn = subdir_annot+added_folder+a["file_name"]
		i_fn = subdir_img+added_folder+fn_images[a["image_id"]]
		annots[i_fn] = a_fn

	trg_name = "train.txt" if "train" in json_path else "val.txt"
	trg_path = os.path.join(trg_dir, "list", trg_name)
	if not os.path.exists(os.path.dirname(trg_path)):
		os.makedirs(os.path.dirname(trg_path))

	with open(trg_path, 'w', newline='\n') as savelist:
		savelist.write('\n'.join(['%s %s'% (p, annots[p]) for p in sorted(annots.keys())]) + '\n')

if __name__ == '__main__':
	"""
	For PASCAL-Context-460, there is an explicit unlabeled class
	(class 0) so we don't include unlabeled=255 from source.
	"""
	#trg_dir = json_to_namestxt(os.path.join(os.environ['RVC_DATA_DIR'], "viper", "train" ,"pano.json"), "viper",
	#				 segmentation_rvc_subfolder + "/../mseg_api/mseg/dataset_lists")
	#trg_dir = json_to_namestxt(os.path.join(os.environ['RVC_DATA_DIR'], "viper", "val", "pano.json"), "viper",
	#							  trg_dir)

	#json_to_namestxt(os.path.join(os.environ['RVC_DATA_DIR'],"wilddash","panoptic.json"), "wilddash2",
	#				segmentation_rvc_subfolder+"/../mseg_api/mseg/dataset_lists")
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

	args = parser.parse_args()

	print('Remapping Parameters: ', args)
	remap_dataset(
		args.orig_dname,
		args.mapping_tsv,
		args.orig_dataroot,
		args.remapped_dataroot,
		args.panoptic_json,
		args.num_processes,
		args.create_symlink_cpy
	)