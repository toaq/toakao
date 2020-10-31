# -*- coding: utf-8 -*-

from routines import *
import sys, os, time

# ==================================================================== #

def entrypoint(this_path, toadai_path = None):
  t1 = time.time()
  this_dir = os.path.dirname(os.path.abspath(this_path)) + os.path.sep
  if toadai_path is None:
    toadai_path = this_dir + "toadai-0.json"
  proceed(toadai_path, this_dir)
  print("  Total execution time:     {:.3f} seconds.".format(
    time.time() - t1))

def proceed(toadai_path, output_dir):
  ds = dicts_from_json_path(toadai_path)
  at = table_from_csv_path(output_dir + "toadai-0b-actions.csv", ";")
  orphs = []
  dels = []
  for de in ds:
    action = None
    for ae in at:
      if de["id"] == ae[0]:
        action = ae[1]
        break
    if de["toaq"] in {"?", "???"} or action == "ORPHANE":
      orphs.append(ds.pop(ds.index(de)))
    elif action == "DELETE":
      dels.append(ds.pop(ds.index(de)))
    elif (isinstance(action, str) and len(action) >= 7
          and action[:7] == "RENAME:"):
      de["toaq"] = action[7:]
  save_dicts_as_csv_file(
    orphs, ";", output_dir + "toadai-0-orphane-entries.csv")
  save_dicts_as_csv_file(
    dels, ";", output_dir + "toadai-0-deleted-entries.csv")
  save_dicts_as_csv_file(ds, ";", output_dir + "toadai-0b.csv")
  save_as_json_file(ds, output_dir + "toadai-0b.json")
  
  # TODO: `translations`
  # TODO: synonyms, etymologies…


# === ENTRY POINT === #

entrypoint(*sys.argv)

