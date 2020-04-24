#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Load/ Save json efficiently TODO: with a progress bar

#ujson can be installed via pip install ujson
try:
    import hyperjson as json
except:
    import json

def load_json(inp_path):
    with open(inp_path, 'r') as ifile:
        loadedj = json.load(ifile)
    return loadedj

def save_json(savej, outp_path):
    with open(outp_path, 'w', newline='\n') as ofile:
        json.dump(savej, ofile, ensure_ascii=True)
