#!/usr/bin/python3
#collects dataq directories by either copy, move or symlink operation

import argparse, os, sys, subprocess, glob, shutil

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

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("--src", type=str, required=True, 
		help="source folder(s) seperated by semicolon")
	parser.add_argument("--dst_root", type=str, default='./', 
		help="destination folder")
	parser.add_argument("--collapse_depth", type=int, default=0,
		help="automatically collapses directory structure to use only leaf subfolder up to depth collapse_depth")
	parser.add_argument("--type", default='dryrun', choices=('symlink', 'copy', 'move', 'copy_files', 'move_files', 'dryrun', 'dryrun_files', 'dryrun_symlink'),
		help="type of collection operation; possible values: copy, move, copy_files, move_files and symlink ; *_files will use a single dst subfolder")
	args = parser.parse_args()
	dst_real = fix_folder_path(args.dst_root)
	
	all_srcs = args.src.split(';')
	if "dryrun" in args.type:
		print("No action; showing dryrun results only. Restart script with a different --type to execute.")
	for src in all_srcs:
		glob_sel = "*.*"
		if '*' in src:
			glob_sel = src.replace('\\','/').split('/')[-1]
		src_dir = fix_folder_path(src)
		if dst_real in src_dir:
			print("Warning: your destination root directory is a parent folder of your src directory. Skipping src dir "+ src_dir)
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
				src_files = glob.glob(src_real+'/**/'+glob_sel)
			elif glob_sel != '*.*' and not "symlink" in args.type:
				src_files = glob.glob(src_real+'/'+glob_sel)
			else:
				src_files = [src_real]
				
			dst_folder = dst_real
			if not skip_subfolder:
				dst_folder = fix_folder_path(os.path.join(dst_real,trg_dir1))
			for src_file in src_files:
				if not skip_subfolder and os.path.isdir(src_file) and os.path.isdir(dst_folder):
					print("Warning: directory "+dst_folder+ " already exists; skipping!")
					continue
				if args.type == "symlink":
					unpriv_symb_link(src_file, dst_folder)
				elif "dryrun" in args.type:
					print("collecting %s to %s"%(src_file, dst_folder))
				else:
					if skip_subfolder:
						parent_dir = dst_folder
					else:
						parent_dir = os.path.dirname(dst_folder)
					if not os.path.exists(parent_dir):
						os.makedirs(parent_dir)
					shutil.copy2(src_file, dst_folder)
					if "move" in args.type and os.path.isfile(src_file):
						os.remove(src_file) #TODO: cleanup empty folders as well
