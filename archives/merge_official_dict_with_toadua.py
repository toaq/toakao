# -*- coding: utf-8 -*-

# In a nutshell, this script takes the official Toaq dictionary JSON and a Toadua API JSON as input and merges them under a new JSON template and outputs the result in a separate file (the input files are not modified).

# USAGE: $ python merge_official_dict_with_toadua.py dictionary.json toadua_api_snapshot.json
# OUTPUT: new_dict.json

import sys, json, re, unicodedata, random, time
from collections import OrderedDict

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

def convert_caron_to_diaresis(s):
  cs = "ǎěǐǒǔ"
  ds = "äëïöü"
  i = 0
  while i < len(s):
    if s[i] in cs:
      s = s[:i] + ds[cs.index(s[i])] + s[i+1:]
    i += 1

def normalized(s):
  s = re.sub(u'i', u'ı', s)
  s = unicodedata.normalize('NFD', s)
  s = re.sub(u'[x’]', u"'", s)
  # s = re.sub(u'(?!\u0304)[\u0300-\u030f]', u'', s)
  s = re.sub(u"[^0-9A-Za-zı\u0300-\u030f'_ ()«»,;.…!?]+", u' ', s)
  s = re.sub(u' +', u' ', s)
  s = unicodedata.normalize('NFC', s)
  convert_caron_to_diaresis(s)
  return s.strip().lower()

# key_from_head is unused.
def key_from_head(official_dict, head, key, default=None):
  for e in official_dict:
    if type(e) is dict and "head" in e:
      if e["head"] == head:
        if key in e:
          return e[key]
        else:
          return default
  return default

def entry_from_head(dictionary, head):
  for e in dictionary:
    if type(e) is dict and "toaq" in e:
      if e["toaq"] == head:
        return e
  return dict()

def iso_date_from_comment_date(d):
  if re.match("[0-9]{4}-[0-9]+-[0-9]+", d) != None:
    # It's already an ISO date.
    return d;
  res = re.match(
    "[A-Za-z]+, +([0-9]+) +([A-Za-z]+) +([0-9]+) +([0-9:.]+) +GMT", d)
  if res == None:
    print("UNKNOWN DATE FORMAT: " + d)
    return ""
  res = res.groups()
  assert(len(res) >= 4)
  ms = ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
       "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
  if res[1] not in ms:
    print("UNKNOWN MONTH CODE: " + str(res[1]))
    return ""
  m = ms.index(res[1]) + 1
  return (res[2] + "-" + "{:02d}".format(m) + "-" + res[0]
          + "T" + res[3] + "Z")

def process_entry(i, dict, official_dict):
  entry = dict[i]
  entry["author"] = entry.pop("user")
  is_official_entry = entry["author"] in ("official", "examples")
  def official_key(key, default = None):
    return entry_from_head(official_dict, entry["head"]) \
           .get(key, default) if is_official_entry else default
  # OK: id, date
  if not is_official_entry:
    if entry["head"] in ("@toacia", "?", "???"):
      entry["head"] = "???"
    else:
      entry["head"] = normalized(entry["head"])
  entry["is_a_lexeme"]       = (
    set(" ảẻỉỏủỷáéíóúýàèìòùỳâêîôûŷäëïöüÿãẽĩõũỹ")
    .isdisjoint(entry["head"])
    or entry["author"] != "examples"
    or (entry["head"][0].islower() and not " " in entry["head"])
  )
  entry["audio"]            = []
  entry["class"]            = official_key("type", "")
  entry["serial_signature"] = official_key("frame", "")
  entry["distribution"]     = official_key("distribution", "")
  entry["generics"]         = ""
  entry["noun_classes"]     = ""
  entry["slot_tags"]        = []
  entry["tags"]             = [l[0] for l in official_key("fields", "")]
  entry["examples"]         = []
  examples = official_key("examples", [])
  for ex in examples:
    id = new_unique_id(dict)
    ex = {
      "id": id,
      "author": "official_examples",
      "head": ex["toaq"],
      "is_a_lexeme": False,
      "target_language": "eng",
      "definition": ex["english"],
      "date": entry["date"],
      "tags": []
    }
    dict.append(ex)
    entry["examples"].append(id)
  lcs = {"en": "eng", "fr": "fra", "es": "spa", "de": "deu", "pl": "pol",
         "ja": "eng"}
         # No, "ja":"eng" is not a mistake: unfortunately in the Toadua database all the "ja"-labelled entries are actually in English and not in Japanese... :'(
  lc = entry.pop("scope")
  entry["target_language"]  = lcs.get(lc, lc)
  assert(len(entry["target_language"]) != 2)
  entry["def_type"]         = "informal"
  entry["definition"]       = entry.pop("body")
  assert(len(entry["definition"]) > 0)
  if entry["author"] in ("official", "examples"):
    d = entry["definition"]
    if len(d) >= 7 and d[0] == "(" and d[1] != " " and ") " in d:
      p = d.index(")") + 1
      entry["example_id"]   = d[:p]
      entry["definition"]   = d[p+1:]
      entry["is_a_lexeme"]  = False
  entry["gloss"]            = official_key("gloss", "")
  entry["keywords"]         = official_key("keywords", "")
  entry["segmentation"]     = ""
  entry["etymology"]        = []
  entry["related"]          = []
  entry["derived"]          = []
  entry["synonyms"]         = []
  entry["antonyms"]         = []
  entry["hypernyms"]        = []
  entry["hyponyms"]         = []
  entry["comments"]         = [
    {
      "content": com["content"],
      "date": iso_date_from_comment_date(com["date"]),
      "author": com["user"]
    } for com in entry["notes"]
  ]
  entry["notes"]            = official_key("notes", [])
  m = re.match("(\(fork of #[^ )]+\))", entry["definition"])
  if m:
    fn = m.groups()[0]
    entry["definition"] = entry["definition"][len(fn) + 1 :]
    entry["notes"] += [fn]
  # OK: score, votes
  # Reordering:
  order = (
    "id", "date", "author", "head", "is_a_lexeme", "example_id", "audio", "class", "serial_signature", "distribution", "generics", "noun_classes", "slot_tags", "examples", "tags", "target_language", "def_type", "definition", "notes", "gloss", "keywords", "segmentation", "etymology", "related", "derived", "synonyms", "antonyms", "hypernyms", "hyponyms", "comments", "score", "votes"
  )
  # assert(all(map(lambda key: key in order, list(entry.keys()))))
  diff = set(entry.keys()) - set(order)
  if diff != set():
    print("FOREIGN KEYS: " + str(diff))
  dict[i] = OrderedDict((key, entry[key]) for key in order if key in entry)


# === ENTRY POINT === #

t1 = time.time()
if len(sys.argv) < 3:
  print("Not enough parameters.")
  sys.exit()
else:
  this_path = sys.argv[0]
  i = len(this_path) - 1
  while i >= 0 and this_path[i] not in "/\\":
     i -= 1
  this_path = this_path[: i + 1]
  new_dict_path = this_path + "new_dict.json"
  official_dict_path = sys.argv[1]
  toadua_dict_path = sys.argv[2]
  with open(official_dict_path, "r", encoding="utf8") as official_dict_json, \
       open(toadua_dict_path, "r", encoding="utf8") as toadua_dict_json, \
       open(new_dict_path, "wb") as new_dict_json:
    official_dict = json.loads(official_dict_json.read())
    new_dict = json.loads(toadua_dict_json.read(),
                          object_pairs_hook=OrderedDict)
    i = 0
    l = len(new_dict)
    log = ""
    n_removed_donwvoted = 0
    t2 = time.time()
    while i < l:
      if ((not type(new_dict[i]) is OrderedDict)
          or ("head" not in new_dict[i]) or ("user" not in new_dict[i])):
        e = new_dict.pop(i)
        log += "Removing anomalous element \"" + str(e) + "\"...\n"
        l -= 1
      elif ("score" in new_dict[i] and new_dict[i]["score"] < 0
            and new_dict[i]["user"] not in ("official", "examples")):
        # log += ("Removing downvoted entry \"" + new_dict[i]["head"] \
        #       + "\" from user \"" + new_dict[i]["user"] + "\".\n")
        new_dict.pop(i)
        l -= 1
        n_removed_donwvoted += 1
      else:
        process_entry(i, new_dict, official_dict)
        i += 1
    # Now checking for possible missing official entries
    missing_official_entries = set()
    for x in official_dict:
      found = False
      for y in new_dict:
        if y["head"] == x["toaq"]:
          found = True
          break
      if not found:
        missing_official_entries.add(x["toaq"])
    n = len(missing_official_entries)
    if n > 0:
      log += ("  " + str(n) + " MISSING OFFICIAL ENTR"
              + ("Y" if n == 1 else "IES") + ": "
              + str(missing_official_entries))
    d = time.time() - t2
    if log != "":
      print(log)
    if n_removed_donwvoted > 0:
      print("  " + str(n_removed_donwvoted) + " downvoted entr"
            + ("y has" if n_removed_donwvoted == 1 else "ies have")
            + " been removed.")
    print("  New dictionary entry count: " + str(len(new_dict)) + ".")
    print("  Dictionaries processed in {:.3f} seconds.".format(d))
    new_dict_json.truncate()
    new_dict_json.write(
      bytes(
        json.dumps(new_dict, indent = 2, ensure_ascii = False),
        encoding = "utf8"
      )
    )
    print("  Total execution time:     {:.3f} seconds.".format(
      time.time() - t1))
    

