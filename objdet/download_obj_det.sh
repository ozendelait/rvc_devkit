#!/bin/sh
# Downloads & extracts OID, COCO, and Obj365 datasets to RVC_DATA_DIR
# Full dataset sizes: COCO: ~26GB, Obj365: ~394GB, OID: ~527GB, MVD: ~25GB = 972GB

RVC_OBJ_DET_SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
${RVC_OBJ_DET_SCRIPT_DIR}/download_coco_boxable.sh
${RVC_OBJ_DET_SCRIPT_DIR}/download_obj365.sh
${RVC_OBJ_DET_SCRIPT_DIR}/download_oid_boxable.sh
RVC_OBJ_DET_SCRIPT_DIR =