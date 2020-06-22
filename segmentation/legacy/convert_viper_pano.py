import csv
import json
import argparse
import pathlib
import numpy as np
import imageio

def bbox(segment_mask):
	r, c = np.nonzero(segment_mask)
	x = np.amin(c)
	y = np.amin(r)
	w = np.amax(c)-x+1
	h = np.amax(r)-y+1
	return [int(x),int(y),int(w),int(h)]

def image_id(subset, filename):
	s = pathlib.Path(filename).stem
	sequence = int(s[:3])
	frame    = int(s[4:])
	return {'train':0, 'val':1, 'test':2}[subset] * 1000000 + sequence * 10000 + frame

def coco_img(labelmap):
	cr = labelmap % 256
	labelmap = (labelmap - cr) / 256
	cg = labelmap % 256
	labelmap = (labelmap - cg) / 256
	cb = labelmap
	coco_img = np.dstack((cr, cg, cb))
	return coco_img.astype(np.uint8)

if __name__ == '__main__':

	p = argparse.ArgumentParser()
	p.add_argument('dataset_dir', type=str, help='Root directory of VIPER dataset.')
	p.add_argument('subset', type=str, choices=['train', 'val', 'test'], help='Subset to be converted.')
	p.add_argument('--label_definition', type=str, help='Path to label definitions (e.g., classes.csv from https://playing-for-benchmarks.org/download/)')
	args = p.parse_args()

	categories = []
	with open(args.label_definition, newline='') as csvfile:
		csv = csv.DictReader(csvfile)
		for row in csv:
			c = {'id':int(row['id']), 'name':row['classname'], 'supercategory':'', 'isthing': int(row['instance_eval'])==1, 'color':[int(row['red']), int(row['green']), int(row['blue'])]}
			categories.append(c)
			pass
		pass

	annotations = []
	imageid_paths = {}
	cls_path  = pathlib.Path(args.dataset_dir) / args.subset / 'cls'
	inst_path = pathlib.Path(args.dataset_dir) / args.subset / 'inst'
	pano_path = pathlib.Path(args.dataset_dir) / args.subset / 'pano'
	pano_path.mkdir(parents=False, exist_ok=True)
	
	for sequence_path in inst_path.iterdir():

		if not sequence_path.is_dir():
			continue

		(pano_path / sequence_path.name).mkdir(parents=False, exist_ok=True)

		for inst_label_path in sequence_path.iterdir():

			if not inst_label_path.suffix == '.png':
				continue

			# corresponding class map
			cls_label_path  = cls_path  / sequence_path.name / inst_label_path.name
			pano_label_path = pano_path / sequence_path.name / inst_label_path.name

			segments_info = []

			# instance maps contain class id (red) and instance id (256 * green + blue), stuff is 0 here
			# combining class id and original instance id makes a unique segment id as required for coco
			inst_img   = imageio.imread(inst_label_path).astype(np.uint32)			
			stuff_mask = inst_img[:,:,0].ravel() == 0
			coco_map   = (inst_img[:,:,0] * 256 * 256 + inst_img[:,:,1] * 256 + inst_img[:,:,2]).flatten()

			# we can keep class ids for stuff
			cls_map    = imageio.imread(cls_label_path, pilmode='P').astype(np.uint32).ravel()
			coco_map[stuff_mask] = cls_map[stuff_mask]
			coco_map = coco_map.reshape(inst_img.shape[:2])

			segment_ids, segment_idx, segment_areas = np.unique(coco_map, return_index=True, return_counts=True)
			for id, idx, area in zip(segment_ids, segment_idx, segment_areas):

				# ignore unlabeled
				if id == 0:
					continue

				segment_mask = coco_map == id

				# stuff gets 'iscrowd' = 1
				segment_info = {'id':int(id), 'category_id': int(cls_map[idx]), 'area': int(area), 'bbox': bbox(segment_mask), 'iscrowd':(1 if id < 65536 else 0)}
				segments_info.append(segment_info)
				pass

			imageio.imwrite(pano_label_path, coco_img(coco_map))
			img_id = int(image_id(args.subset, inst_label_path.name))
			imageid_paths[img_id] = inst_label_path.name
			annotation = {'image_id':img_id, 'file_name':inst_label_path.name, 'segments_info':segments_info}
			annotations.append(annotation)
			pass
		pass

	#now create images array (one entry per intensity rgb input image)
	images = []
	for id in sorted(imageid_paths.keys()):
		images.append({'id': id, 'file_name':imageid_paths[id], 'width': 1920, 'height': 1080})
	d = {'annotations': annotations, 'categories': categories, 'images': images}

	pano_json_dir = pathlib.Path(args.dataset_dir) / args.subset
	with open(pano_json_dir /  'pano.json', 'w') as f:
		json.dump(d, f, ensure_ascii=False)
		pass
	pass
