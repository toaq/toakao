# -*- coding: utf-8 -*-

# In a nutshell, this script takes the unofficial toadaı.json dictionary as input, then download the official dictionary and the example sentence spreadsheet, then merges them under a new JSON template and outputs the result in a separate file `toatuq.json` (the input files are not modified).

# USAGE: $ python unify.py
# OUTPUT: toatuq.json

# ==================================================================== #

import sys, io, requests, json, csv, unicodedata, random, time, datetime
from collections import OrderedDict
from routines import *

def entrypoint(this_path, toadaı_json_path = None):
  t1 = time.time()
  i = len(this_path) - 1
  while i >= 0 and this_path[i] not in "/\\":
     i -= 1
  this_path = this_path[: i + 1]
  if toadaı_json_path is None:
    toadaı_path = this_path + "toadai.json"
  toatuq_path = this_path + "toatuq.json"
  
  try:
    response = requests.get(
        "https://raw.githubusercontent.com/toaq/dictionary/master/"
        + "dictionary.json")
    assert response.status_code == 200, (
      "HTTP error: status code " + str(response.status_code))
  except:
    print(
      "Unexpected error upon attempting to download the official dictionary:",
      sys.exc_info()[0])
    sys.exit()
  official_dict = json.loads(response.content)

  try:
    a_sentences = table_from_csv_url(
      'https://docs.google.com/spreadsheet/ccc?key=1bCQoaX02ZyaElHiiMcKHFemO4eV1MEYmYloYZgOAhac&output=csv&gid=1395088029')
    b_sentences = table_from_csv_url(
      'https://docs.google.com/spreadsheet/ccc?key=1bCQoaX02ZyaElHiiMcKHFemO4eV1MEYmYloYZgOAhac&output=csv&gid=574044693')
    o_sentences = table_from_csv_url(
      'https://docs.google.com/spreadsheet/ccc?key=1bCQoaX02ZyaElHiiMcKHFemO4eV1MEYmYloYZgOAhac&output=csv&gid=1905610286')
    countries = table_from_csv_url(
      'https://docs.google.com/spreadsheet/ccc?key=1P9p1D38p364JSiNqLMGwY3zDRPQ_f6Yob_OL-uku28Q&output=csv&gid=637793855')
  except:
    print(
      "Unexpected error upon attempting to download the spreadsheet:",
      sys.exc_info()[0])
    sys.exit()
  
  with open(toadaı_path, "r", encoding="utf8") as toadaı_json, \
       open(toatuq_path, "wb")                 as toatuq_json:
    reformat(official_dict)
    toatuq = official_dict
    toatuq += json.loads(toadaı_json.read(),
                         object_pairs_hook=OrderedDict)
    # ⌵ Importing example sentences, ignoring the two first rows.
    toatuq += dicts_from_sentences(a_sentences[2:], toatuq, False)
    toatuq += dicts_from_sentences(b_sentences[2:], toatuq, False)
    toatuq += dicts_from_sentences(o_sentences[2:], toatuq, True)
    # ⌵ Importing country names, ignoring the two first rows.
    toatuq += dicts_from_countries(countries[2:], toatuq)
    print("  New dictionary entry count: " + str(len(toatuq)) + ".")
    toatuq_json.truncate()
    toatuq_json.write(
      bytes(
        json.dumps(toatuq, indent = 2, ensure_ascii = False),
        encoding = "utf8"
      )
    )
    print("  Total execution time:     {:.3f} seconds.".format(
      time.time() - t1))

def dicts_from_sentences(sentences, dictionary, is_official):
  # date = datetime.datetime.utcnow().isoformat()
  ds = []
  for row in sentences:
    if len(row) < 3:
      return ds
    if row[1] != "":
      id = new_unique_id(dictionary)
      e = {
        "id": id,
        "official": is_official,
        "author": "examples",
        "toaq": row[1],
        "is_a_lexeme": False,
        "example_id": row[0],
        "target_language": "eng",
        "definition": row[2],
        # "date": date,
        "tags": []
      }
      ds.append(e)
  return ds

def dicts_from_countries(countries, dictionary):
  ds = []
  for row in countries:
    if len(row) < 4:
      return ds
    if row[1] != "":
      # /!\ TODO: TO BE IMPLEMENTED /!\
      # TODO: rm [xx] from row[0].
      pass
  return ds

def random_id():
  cs = "0123456789-_abcdefghijklmnopqrstuvwxyzABCDERFGIJKLMNOPQRSTUVWXYZ"
  id = ""
  while len(id) < 0xA:
    id += random.choice(cs)
  return id

def new_unique_id(dictionary):
  while True:
    id = random_id()
    for e in dictionary:
      if isinstance(e, (dict, OrderedDict)) and "id" in e:
        if e["id"] == id:
          continue
    return id

def reformat(dictionary):
  i = 0
  l = len(dictionary)
  while i < l:
    entry = dictionary[i]
    entry["official"] = True
    # Absent from official dict: id, date...
    if "author" not in entry:
      entry["author"] = "Hoemai"
    if "type" in entry:
      entry["class"] = entry.pop("type")
    # if "frame" in entry:
    #   entry["serial_signature"]   = entry.pop("frame")
    if "fields" in entry:
      entry["tags"] = entry.pop("fields")
    entry["is_a_lexeme"]      = (
      set(" ảẻỉỏủỷáéíóúýàèìòùỳâêîôûŷäëïöüÿãẽĩõũỹ")
      .isdisjoint(entry["toaq"])
      or (entry["toaq"][0].islower() and not " " in entry["toaq"])
    )
    if "english" in entry:
      entry["definition"] = entry.pop("english")
    else:
      assert "definition" in d, (
        "Entry: " + entry["toaq"] + "\n" + str(entry))
    assert len(entry["definition"]) > 0
    entry["target_language"]  = "eng"
    entry["definition_type"]  = "informal"
    entry["audio"]            = []
    entry["generics"]         = ""
    entry["noun_classes"]     = ""
    entry["slot_tags"]        = []
    entry["segmentation"]     = ""
    entry["etymology"]        = []
    entry["related"]          = []
    entry["derived"]          = []
    entry["synonyms"]         = []
    entry["antonyms"]         = []
    entry["hypernyms"]        = []
    entry["hyponyms"]         = []
    # Reordering:
    order = (
      "id", "official", "date", "author", "toaq", "is_a_lexeme", "example_id", "audio", "class", "namesake", "frame", "distribution", "generics", "noun_classes", "slot_tags", "tags", "examples", "target_language", "definition_type", "definition", "notes", "gloss", "short", "keywords", "segmentation", "etymology", "related", "derived", "synonyms", "antonyms", "hypernyms", "hyponyms", "comments", "score", "votes"
    )
    # assert(all(map(lambda key: key in order, list(entry.keys()))))
    diff = set(entry.keys()) - set(order)
    if diff != set():
      print("FOREIGN KEYS: " + str(diff))
    dictionary[i] = OrderedDict(
      (key, entry[key]) for key in order if key in entry
    )
    i += 1


# === ENTRY POINT === #

entrypoint(*sys.argv)
   

