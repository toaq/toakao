# -*- coding: utf-8 -*-

# In a nutshell, this script takes the unofficial toadaı.json dictionary as input, then download the official dictionary and the example sentence spreadsheet, then merges them under a new JSON template and outputs the result in a separate file `toatuq.json` (the input files are not modified).

# USAGE: $ python unify.py
# OUTPUT: toatuq.json

import sys, io, requests, json, csv, unicodedata, random, time, datetime
from collections import OrderedDict

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
    response = requests.get('https://docs.google.com/spreadsheet/ccc?key=1bCQoaX02ZyaElHiiMcKHFemO4eV1MEYmYloYZgOAhac&output=csv&gid=1395088029')
    assert response.status_code == 200, 'Wrong status code'
    csv_a = response.content
    response = requests.get('https://docs.google.com/spreadsheet/ccc?key=1bCQoaX02ZyaElHiiMcKHFemO4eV1MEYmYloYZgOAhac&output=csv&gid=574044693')
    assert response.status_code == 200, 'Wrong status code'
    csv_b = response.content
    
  except:
    print(
      "Unexpected error upon attempting to download the spreadsheet:",
      sys.exc_info()[0])
    sys.exit()
  
  csv_reader = csv.reader(io.StringIO(csv_a.decode("UTF8"), newline = None),
                          delimiter=',')
  a_sentences = []
  for row in csv_reader:
    a_sentences.append(row)
  
  csv_reader = csv.reader(io.StringIO(csv_b.decode("UTF8"), newline = None),
                          delimiter=',')
  b_sentences = []
  for row in csv_reader:
    b_sentences.append(row)
  
  with open(toadaı_path, "r", encoding="utf8") as toadaı_json, \
       open(toatuq_path, "wb")                 as toatuq_json:
    reformat(official_dict)
    toatuq = official_dict
    toatuq += json.loads(toadaı_json.read(),
                         object_pairs_hook=OrderedDict)
    # ⌵ Importing example sentences, ignoring the two first rows.
    toatuq += json_from_sentences(a_sentences[2:], toatuq)
    toatuq += json_from_sentences(b_sentences[2:], toatuq)
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

def json_from_sentences(sentences, dictionary):
  date = datetime.datetime.utcnow().isoformat()
  json = []
  for row in sentences:
    if len(row) < 3:
      return json
    if row[1] != "":
      id = new_unique_id(dictionary)
      e = {
        "id": id,
        "author": "examples",
        "toaq": row[1],
        "is_a_lexeme": False,
        "example_id": row[0],
        "target_language": "eng",
        "definition": row[2],
        "date": date,
        "tags": []
      }
      json.append(e)
  return json

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
    # Absent from official dict: id, date...
    if "author" not in entry:
      entry["author"] = "official"
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
      "id", "date", "author", "toaq", "is_a_lexeme", "example_id", "audio", "class", "namesake", "frame", "distribution", "generics", "noun_classes", "slot_tags", "tags", "examples", "target_language", "definition_type", "definition", "notes", "gloss", "short", "keywords", "segmentation", "etymology", "related", "derived", "synonyms", "antonyms", "hypernyms", "hyponyms", "comments", "score", "votes"
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
   

