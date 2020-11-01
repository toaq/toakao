# -*- coding: utf-8 -*-

# ==================================================================== #

'''
PURPOSE:
  Regorganize the toadai-0.json data so as to disallow words to have more than one definition in a single language, and to group definitions in different languages into a single entry, as well as moving all the strict synonyms in the same entry.
'''

# ==================================================================== #

import sys, os, time
## from routines import *

def import_from_path(name, path):
  import importlib.util
  spec = importlib.util.spec_from_file_location(name, path)
  mod = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(mod)
  return mod

def import_from_module(module, names = []):
  if "__all__" in module.__dict__:
    all_names = module.__dict__["__all__"]
  else:
    all_names = [x for x in module.__dict__ if not x.startswith("_")]
  names = all_names if not names else (
    list(filter(lambda x: x in names, all_names)))
  globals().update({k: getattr(module, k) for k in names})

routines = import_from_path("routines", "../routines.py")
import_from_module(routines)

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
  at = table_from_csv_path(output_dir + "toadai-mono-0-actions.csv",
                           ";")
  official_dict_url = (
    "https://raw.githubusercontent.com/toaq/dictionary/master/dictionary.json"
  )
  official_words = set(e["toaq"] for e in dicts_from_json_url(official_dict_url))
  #official_words = set()
  orphs = []
  dels = []
  defs = []
  words = []
  odcs = []  # Official definition competitors
  toods = [] # Translations of official definitions
  i = 0
  while i < len(ds):
    de = ds[i]
    # EXECUTION OF ACTIONS
    action = None
    for a in at:
      if de["id"] == a[0]:
        action = a[1]
        break
    if de["toaq"] in official_words:
      if de["target_language"] == "eng":
        odcs.append(ds.pop(ds.index(de)))
      else:
        reformat(de)
        toods += de["translations"]
        ds.pop(ds.index(de))
      continue
    elif de["toaq"] in {"?", "???"} or action == "ORPHANE":
      orphs.append(ds.pop(ds.index(de)))
      continue
    elif action == "DELETE":
      dels.append(ds.pop(ds.index(de)))
      continue
    elif (isinstance(action, str) and len(action) >= 7
          and action[:7] == "RENAME:"):
      de["toaq"] = action[7:]
    assert "translations" not in ds[i]
    # MERGING SYNONYMS AND DEFINITIONS OF A SAME WORD IN DIFFERENT LANGUAGES
    de["toaq"] = [de["toaq"]]
    def f(dl, entry_name):
      di = dict_index_from_key_value(dl, "content", de[entry_name])
      if di != None:
        j = dl[di]["index"]
        assert i != j
        import datetime
        date_template = '%Y-%m-%dT%H:%M:%S.%fZ'
        d1 = datetime.datetime.strptime(ds[j]["date"], date_template)
        d2 = datetime.datetime.strptime(de["date"], date_template)
        if d2 < d1:
          dl[di]["index"] = i
          i_kept = i
          i_del = j
        else:
          i_kept = j
          i_del = i
        if entry_name == "definition":
          # Adding a new synonym:
          new_toaq = ds[i_del]["toaq"]
          ds[i_kept] = reformat(ds[i_kept])
          ds[i_kept] = reorder(ds[i_kept])
          ds[i_kept]["toaq"] += new_toaq
          ds[i_del] = reformat(ds[i_del])
          ds[i_kept]["translations"] = ds[i_del]["translations"]
          if i_kept > i_del:
            i_kept -= 1
          words.append({"content": [new_toaq], "index": i_kept})
        elif entry_name == "toaq":
          ds[i_kept] = reformat(ds[i_kept])
          ds[i_kept] = reorder(ds[i_kept])
          ds[i_del] = reformat(ds[i_del])
          if (ds[i]["translations"][0]["language"]
              in set(d["language"] for d in ds[j]["translations"])):
            print("COMPETING DEFINITION: " + str(ds[i]["id"] + " "
                  + str(ds[i]["toaq"][0]))
                  + " " + str(ds[i]["translations"][0]["language"]))
            print(
              f"  (competing with {ds[j]['id']} {ds[j]['toaq'][0]})")
          ds[i_kept]["translations"] += ds[i_del]["translations"]
          if i_kept > i_del:
            i_kept -= 1
          defs.append({
            "content": ds[i]["translations"][0]["definition"],
            "index": i_kept
          })
        else:
          assert False
        dl.append(ds.pop(i_del))
        return True
      else:
        ds[i] = reformat(ds[i])
        return False
    if f(defs, "definition") or f(words, "toaq"):
      # An entry has been deleted, i won't be increased.
      continue
    else:
      words.append({"content": de["toaq"], "index": i})
      defs.append({
        "content": de["translations"][0]["definition"], "index": i
      })
    ds[i] = reorder(de)
    i += 1
  save_dicts_as_csv_file(
    orphs, ";", output_dir + "toadai-0-orphane-entries.csv")
  save_dicts_as_csv_file(
    dels, ";", output_dir + "toadai-0-deleted-entries.csv")
  save_dicts_as_csv_file(
    odcs, ";", output_dir + "official-definition-competitors.csv")
  save_dicts_as_csv_file(
    toods, ";", output_dir + "translations-of-official-definitions.csv")
  save_dicts_as_csv_file(ds, ";", output_dir + "toadai-mono-0.csv")
  save_as_json_file(ds, output_dir + "toadai-mono-0.json")

def reformat(e):
  if "target_language" in e:
    e.pop("synonyms")
    e.pop("segmentation")
    e.pop("etymology")
    e["similar"] = []
    e["etymologies"] = []
    e["translations"] = [{
      "language": e.pop("target_language"),
      "definition_type": e.pop("definition_type"),
      "definition": e.pop("definition"),
      "notes": e.pop("notes"),
      "gloss": e.pop("gloss"),
      "keywords": e.pop("keywords")
    }]
  return e

def reorder(entry):
  # Reordering:
  order = (
    "id", "official", "date", "author", "toaq", "is_a_lexeme", "example_id", "audio", "class", "namesake", "frame", "distribution", "generics", "noun_classes", "slot_tags", "tags", "examples", "translations", "etymologies", "related", "derived", "similar", "antonyms", "hypernyms", "hyponyms", "comments", "score", "votes"
  )
  # assert(all(map(lambda key: key in order, list(entry.keys()))))
  diff = set(entry.keys()) - set(order)
  if diff != set():
    print("FOREIGN KEYS: " + str(diff))
  return OrderedDict(
    (key, entry[key]) for key in order if key in entry
  )


# === ENTRY POINT === #

entrypoint(*sys.argv)

