#!/usr/bin/env python
# Downloads ScanNet public data release
# Run with ./download-scannet.py (or python download-scannet.py on Windows)
# -*- coding: utf-8 -*-
import argparse
import os, sys
from benchmark_viper import VIPER

if __name__ == "__main__":
    unpack_dir_path = archive_dir_path = sys.argv[1]
    if not os.path.exists(unpack_dir_path):
        os.makedirs(unpack_dir_path)
    v_downl = VIPER()
    v_downl.DownloadAndUnpack(archive_dir_path, unpack_dir_path, {})
