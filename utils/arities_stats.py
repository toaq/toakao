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
  f(routines.dicts_from_json_path(json_path))
  print("Total execution time: {:.3f} seconds.".format(
        time.time() - t1))

def f(ml):
  arities = multiset()
  for m in ml:
    if has_lemma(m) and "translations" in m:
      for t in m["translations"]:
        assert "language" in t
        if t["language"] == "eng":
          a = arity_of(t["definition"])
          arities.update(str(a))
  print("ARITIES:")
  maxlen = 0
  for a in arities.keys():
    l = len(a)
    if l > maxlen:
      maxlen = l
  lst = list(arities.items())
  lst.sort(key = lambda p: p[0], reverse = False)
  assert lst != None
  t = arities.total()
  for a, n in lst:
    a = f'{a}'
    r = "{:.2f}".format(n / t)
    print(f"  │ {a.ljust(maxlen)} │ {str(n).rjust(5)} │ {r} │")

def has_lemma(m):
  if "toaq_forms" in m:
    for e in m["toaq_forms"]:
      if e["is_a_lemma"]:
        return True
  return False

def arity_of(definition):
  assert isinstance(definition, str) and len(definition) > 0
  dl = definition.split(";")
  a = 0
  for d in dl:
    a = max(a, d.count("▯"))
  return a

# === ENTRY POINT === #

entrypoint(*sys.argv)

 
