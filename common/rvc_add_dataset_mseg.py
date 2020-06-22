#!/usr/bin/python3
#based on https://github.com/mseg-dataset/mseg-api/blob/master/mseg/label_preparation/remap_dataset.py

import argparse, os, sys, json
import mseg.utils.txt_utils

mseg_api_datasetlists_folder = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(os.path.abspath(mseg.utils.txt_utils.__file__))), "../dataset_lists/"))

#tool called once per dataset and is added to mseg repo
def json_to_namestxt(json_path, new_name, trg_root_dir, img_subfolder, annot_subfolder, split = "train"):
	with open(json_path, 'r') as ifile:
		loadedj = json.load(ifile)

	if split == "train":
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
	if not img_subfolder[-1] == "/":
		img_subfolder+="/"
	if not annot_subfolder[-1] == "/":
		annot_subfolder+="/"
	for a in loadedj["annotations"]:
		a_fp = annot_subfolder.format(file_name=a["file_name"],split=split)+a["file_name"]
		i_fn = fn_images[a["image_id"]]
		i_fp = img_subfolder.format(file_name=i_fn,split=split)+i_fn
		annots[i_fp] = a_fp

	trg_path = os.path.join(trg_dir, "list", split+".txt")
	if not os.path.exists(os.path.dirname(trg_path)):
		os.makedirs(os.path.dirname(trg_path))

	with open(trg_path, 'w', newline='\n') as savelist:
		savelist.write('\n'.join(['%s %s'% (p, annots[p]) for p in sorted(annots.keys())]) + '\n')

	return trg_dir

if __name__ == '__main__':
	"""
	For PASCAL-Context-460, there is an explicit unlabeled class
	(class 0) so we don't include unlabeled=255 from source.
	"""
	parser = argparse.ArgumentParser()
	parser.add_argument("--panoptic_json", type=str, required=True,
		help="path to json containing the png segm. id -> class id mapping and categories")
	parser.add_argument("--orig_dname", type=str, required=True, 
		help="original dataset's name (without class numbers)")
	parser.add_argument("--img_subfolder", type=str, default = "images",
		help="relative path of image subfolder (from dataset root)")
	parser.add_argument("--annot_subfolder", type=str, default = "annotations",
		help="relative path of annotation png subfolder (from dataset root)")

	args = parser.parse_args()

	#add custom dataset to mseg
	trg_dir = mseg_api_datasetlists_folder
	for split_idx, split in enumerate(["train","val"]):
		trg_dir = json_to_namestxt(args.panoptic_json.format(split=split, split_idx=str(split_idx)),
								   args.orig_dname, trg_dir, args.img_subfolder, args.annot_subfolder, split = split)
	print("Added new dataset to "+trg_dir)


