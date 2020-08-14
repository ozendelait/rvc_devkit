#!/usr/bin/python3
#collects data directories by either copy, move or symlink operation
# this can be usefull to join subfolder trees into one folder
# the --template_dir call can be used to untangle result files into the original folder structure
# example for sintel files (which contain doublicate filenames in different folders) scaled to a fixed size:
# --src ./test --dst_root ./onefolder --type copy_files --collapse_depth 4 --collapse_char - --fix_dim 1216x352
# results can be mapped back with:
# --src ./onefolder --template_dir ./test --dst_root ./onefolder2 --type copy_files --collapse_depth 4 --collapse_char - --fix_dim 0x0

import argparse, os, sys, subprocess, glob, itertools, shutil
import cv2
import numpy as np
from itertools import chain

#creates a symbolic link / junction at dst pointing at directory src
def unpriv_symb_link(src, dst):
	if not os.path.exists(src) or os.path.exists(dst):
		return
	parent_dir = os.path.dirname(dst)
	if not os.path.exists(parent_dir):
		os.makedirs(parent_dir)
	if sys.platform.startswith('win'): #symlinks need admin rights, junctions don't
		ptr_needs_closing = False
		if sys.version_info.major > 2 and sys.version_info.minor > 2:
			subprocDEVNULL = subprocess.DEVNULL #introduced in 3.3
		else:
			subprocDEVNULL = open(os.devnull, 'w')
			ptr_needs_closing = True
		subprocess.check_call('mklink /J "%s" "%s"' % (dst, src), shell=True, stdout=subprocDEVNULL, stderr=subprocDEVNULL)
		if ptr_needs_closing:
			subprocDEVNULL.close()
	else:
		os.symlink(src, dst, target_is_directory=True)

#find leaf directories
def list_subdirs(path, depth=1):
	if depth < 2:
		return [path.replace('\\','/')+'/'+os.path.basename(x) for x in filter(os.path.isdir, glob.glob(os.path.join(path, '*')))]
	else:
		curr_subdirs = list_subdirs(path, 0)
		ret_subdirs = []
		for s in curr_subdirs:
			ret_subdirs += list_subdirs(s, depth-1)
		for c in curr_subdirs:
			if not any([s for s in ret_subdirs if c in s]):
				ret_subdirs.append(c)
		return ret_subdirs

def recursive_glob(root_folder, ext_glob):
	return list(itertools.chain.from_iterable(glob.iglob(os.path.join(root,ext_glob)) for root, dirs, files in os.walk(root_folder)))

def fix_folder_path(path):
	path = path.replace('\\','/') #fix windows path errors
	if '*' in path:
		path = '/'.join(path.split('/')[:-1])
	path = os.path.realpath(path).replace('\\','/')
	p_exists = os.path.exists(path)
	if (p_exists and os.path.isfile(path)) or (not p_exists and '.' in path.split('/')[-1]):
		path = os.path.dirname(path) #probably a file instead of a folder
	return path
		

#estimate a good name for this folder
def get_trg_dir_name(path):
	ignore_dirs = ["test", "image", "leftImg"]
	return [d for d in path.replace('\\','/').split('/') if not any([id for id in ignore_dirs if id in d])][-1]

def float_to_uint16(im0, scale_factor=256.0):
	im0 = im0 * scale_factor
	im0[im0 < 0] = 0
	im0[im0 > 65534] = 65534
	im0[np.isnan(im0)] = 65535  # handle invalids
	return im0.astype(np.uint16)

def main(argv=sys.argv[1:]):
	parser = argparse.ArgumentParser()
	parser.add_argument("--src", type=str, required=True, 
		help="source folder(s) seperated by semicolon")
	parser.add_argument("--dst_root", type=str, default='./', 
		help="destination folder")
	parser.add_argument("--collapse_depth", type=int, default=0,
		help="automatically collapses directory structure to use only leaf subfolder up to depth collapse_depth")
	parser.add_argument('--collapse_char', type=str, default=None,
						help="puts files in dst_root, collapse_char is used to create a unique filename.")
	parser.add_argument("--type", default='dryrun', choices=('symlink', 'copy', 'move', 'copy_files', 'move_files', 'dryrun', 'dryrun_files', 'dryrun_symlink'),
		help="type of collection operation; possible values: copy, move, copy_files, move_files and symlink ; *_files will use a single dst subfolder")
	parser.add_argument("--template_dir", type=str, default=None,
						help="apply collection op to files found in template folder structure; also rearrange to fit template")
	parser.add_argument("--fix_dim", type=str, default=None,
						help="Resize images to this dimension in WxH (e.g. 640x480); use 0x0 to read and apply template_dir file dims")
	parser.add_argument("--fix_ext", type=str, default=None,
						help="Change image file extension (e.g. jpg)")
	parser.add_argument("--fix_chan", type=int, default=-1,
						help="Fix number of channels for images (e.g. 1 for result label masks/depth values)")
	parser.add_argument("--inter_nn", action='store_true',
						help="Use Nearest Neighbor Interpolation for scaling (e.g. for result label masks/depth values)")
	args = parser.parse_args(argv)
	dst_real = fix_folder_path(args.dst_root)
	num_collected_total = 0
	all_srcs = args.src.split(';')
	if "dryrun" in args.type:
		print("No action; showing dryrun results only. Restart script with a different --type to execute.")
	if not args.fix_ext is None and args.fix_ext[0] != '.':
		args.fix_ext = '.'+args.fix_ext
	if not args.template_dir is None:
		args.template_dir = (args.template_dir.replace('\\','/')+'/').replace('//','/')
	for src in all_srcs:
		num_collected = 0
		glob_sel = "*.*"
		if '*' in src:
			glob_sel = src.replace('\\','/').split('/')[-1]
		src_dir = fix_folder_path(src)
		templ_mapping = None
		if not args.template_dir is None:
			templ_subdirs = list_subdirs(args.template_dir, depth=args.collapse_depth)
			if len(templ_subdirs) == 0:
				templ_subdirs = [args.template_dir]
			templ_files = list(chain(*[recursive_glob(fix_folder_path(s), "*.*") for s in templ_subdirs]))
			templ_files = [t.replace('\\', '/') for t in templ_files]
			path_templ_root = [p.strip() for p in args.template_dir.split('/') if len(p.strip()) > 0]
			templ_mapping = {}
			for f in templ_files:
				path_f = [p.strip() for p in f.split('/') if len(p.strip()) > 0]
				rel_p = '/'.join(path_f[len(path_templ_root):])
				if not args.collapse_char is None:
					templ_f = args.collapse_char.join(path_f[len(path_templ_root):])
				else:
					templ_f = path_f[-1]
				templ_f = os.path.splitext(templ_f)[0]
				templ_mapping[templ_f] = rel_p
			if len(templ_mapping) != len(templ_files):
				print("Warning: template dir contains multiple files with the same file name. Use a correct collapse_char option!")
				continue
		if not args.fix_dim is None:
			args.fix_dim = [int(d) for d in args.fix_dim.split('x')]
		if dst_real in src_dir:
			print("Warning: your destination root directory "+dst_real+" is a parent folder of your src. \n Skipping src dir "+ src_dir)
			continue
		trg_dir0 = get_trg_dir_name(src_dir)
		skip_subfolder = '_files' in args.type
		all_subdirs = []
		if args.collapse_depth > 0 and not skip_subfolder:
			all_subdirs = list_subdirs(src_dir, depth=args.collapse_depth)
		if len(all_subdirs) == 0:
			all_subdirs = [src_dir]
		for s in all_subdirs:
			src_real = fix_folder_path(s)
			trg_dir1 = get_trg_dir_name(s)
			if trg_dir1 != trg_dir0:
				trg_dir1 = trg_dir0+'_'+trg_dir1
			if skip_subfolder:
				src_files = recursive_glob(src_real,glob_sel)
			elif glob_sel != '*.*' and not "symlink" in args.type:
				src_files = glob.glob(src_real+'/'+glob_sel)
			else:
				src_files = [src_real]
				
			dst_folder = dst_real
			if args.collapse_char is None and not skip_subfolder:
				dst_folder = fix_folder_path(dst_real+ '/' + trg_dir1)
			for src_file in src_files:
				dst_path = dst_folder
				tmpl_file = None
				if not templ_mapping is None:
					fname = os.path.splitext(os.path.basename(src_file))[0]
					if not fname in templ_mapping:
						continue
					tmpl_file = os.path.realpath(args.template_dir + '/' + templ_mapping[fname])
					dst_path = dst_real + '/' + templ_mapping[fname]
				elif not args.collapse_char is None:
					path_root = src_real.split('/')
					path_src = src_file.replace('\\', '/').split('/')
					dst_path = dst_folder+'/'+args.collapse_char.join(path_src[len(path_root):])
				if not skip_subfolder and os.path.isdir(src_file) and os.path.isdir(dst_path):
					print("Warning: directory "+dst_path+ " already exists; skipping!")
					continue
				num_collected += 1
				if args.type == "symlink":
					unpriv_symb_link(src_file, dst_path)
				elif "dryrun" in args.type:
					print("collecting %s to %s"%(src_file, dst_path))
				else:
					if skip_subfolder and args.collapse_char is None:
						parent_dir = dst_path
					else:
						parent_dir = os.path.dirname(dst_path)
					if not os.path.exists(parent_dir):
						os.makedirs(parent_dir)
					apply_resizing = False
					if not args.fix_ext is None and not dst_path.endswith(args.fix_ext):
						dst_path = dst_path[:dst_path.rfind('.')]+args.fix_ext
						apply_resizing = True
					if args.fix_dim or apply_resizing:
						if src_file.endswith('.npz'): #floats *256 -> uint 16bit == KITTI depth scale
							im0 = np.load(src_file)
							if isinstance(im0,dict) and 'depth' in im0: #loads output of packnet-sfm correctly
								im0 = im0['depth']
							if im0.dtype == np.float32:
								im0 = float_to_uint16(im0, 256.0)
						elif args.fix_chan == 1:
							im0 = cv2.imread(src_file, cv2.IMREAD_ANYDEPTH)
						elif args.fix_chan == 3:
							im0 = cv2.imread(src_file, cv2.IMREAD_COLOR)
						else:
							im0 = cv2.imread(src_file)
						trg_dim = (args.fix_dim[0],args.fix_dim[1])
						if trg_dim[0] == 0:
							im1 = cv2.imread(tmpl_file)
							trg_dim = (im1.shape[1], im1.shape[0])
						img_sz_mismatch =  im0.shape[0] != trg_dim[1] or im0.shape[1] != trg_dim[0]
						if img_sz_mismatch:
							apply_resizing = True
						if args.inter_nn and img_sz_mismatch:
							im0 = cv2.resize(im0, trg_dim, interpolation=cv2.INTER_NEAREST)
						if im0.shape[0] <= trg_dim[1] and  im0.shape[1] <= trg_dim[0]:
							im0 = cv2.resize(im0,trg_dim,interpolation = cv2.INTER_AREA)
						elif img_sz_mismatch:
							im0 = cv2.resize(im0, trg_dim, interpolation=cv2.INTER_CUBIC)
					if apply_resizing:
						cv2.imwrite(dst_path, im0)
					else:
						shutil.copy2(src_file, dst_path)
					if "move" in args.type and os.path.isfile(src_file):
						os.remove(src_file) #TODO: cleanup empty folders as well
						
		print("Collection for "+src+" finished after %i items."%num_collected)
		num_collected_total +=  num_collected
	if len(all_srcs) > 1:
		print("Total number of items collected: %i" % num_collected_total)
						
if __name__ == '__main__':
	sys.exit(main())