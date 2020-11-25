# -*- coding: utf-8 -*-

# SPDX-License-Identifier: ISC

import sys, os, json, time
from collections import OrderedDict, Counter as multiset

def import_from_path(name, path):
  import importlib.util
  spec = importlib.util.spec_from_file_location(name, path)
  mod = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(mod)
  return mod

routines = import_from_path("routines", "../routines.py")

def entrypoint(this_path, json_path):
  t1 = time.time()
  ds = routines.dicts_from_json_path(json_path)
  authors = multiset()
  for d in ds:
    if "author" in d:
      authors.update([d["author"]])
    else:
      authors.update(None)
  print("AUTHORS:")
  maxlen = 0
  for a in authors.keys():
    l = len(a)
    if l > maxlen:
      maxlen = l
  lst = list(authors.items())
  lst.sort(key = lambda p: p[1], reverse = True)
  assert lst != None
  for a, n in lst:
    a = f'"{a}"'
    print(f"  {a.ljust(maxlen + 2)} : {n}")
  print("Total execution time: {:.3f} seconds.".format(
        time.time() - t1))


# === ENTRY POINT === #

entrypoint(*sys.argv)

