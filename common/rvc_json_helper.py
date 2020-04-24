#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Load/ Save json efficiently with a progress bar

import os, sys, json

def load_json(inp_path):
    with open(inp_path, 'r') as ifile:
        loadedj = json.load(ifile)
    return loadedj

def save_json(savej, outp_path):
    with open(outp_path, 'w', newline='\n') as ofile:
        json.dump(savej, ofile)
