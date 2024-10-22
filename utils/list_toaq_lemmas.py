# -*- coding: utf-8 -*-
# PYTHON 3.10

# COPYRIGHT LICENSE: ISC license. See LICENSE.md in the top level directory.
# SPDX-License-Identifier: ISC

# ============================================================ #

import sys, os, time

from common import edit_json_from_path

SELF_PATH = os.path.dirname(os.path.realpath(__file__))

# ============================================================ #

def entrypoint():
  start_time = time.time()
  edit_json_from_path(
    SELF_PATH + "/../toatuq.json",
    toaq_lemmas_from_toatuq,
    output_path = SELF_PATH + "/toaq_lemmas.json"
  )
  print("Execution time: {:.3f}s.".format(
    time.time() - start_time))

def toaq_lemmas_from_toatuq(toatuq):
  s = set()
  for e in toatuq:
    for tf in e["toaq_forms"]:
      if tf["is_a_lemma"]:
        ts = tf["toaq"]
        if isinstance(ts, str):
          ts = [ts]
        s |= set(ts)
  return list(s)

# ============================================================ #

# === ENTRY POINT === #

entrypoint()

