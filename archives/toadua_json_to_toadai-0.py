# -*- coding: utf-8 -*-

# ==================================================================== #

'''
PURPOSE:
  In a nutshell, this script removes official and example entries from a Toadua JSON and change a little its structure by renaming some fields and adding new ones.

USAGE: $ python toadua_json_to_toadai.py toadua_api_snapshot.json
OUTPUT: toadai-0.json
'''

# ==================================================================== #

import sys, os, time, json, re, unicodedata, random
from collections import OrderedDict

def import_from_path(name, path):
  import importlib.util
  spec = importlib.util.spec_from_file_location(name, path)
  mod = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(mod)
  return mod

routines = import_from_path("routines", "../routines.py")

# ==================================================================== #

def entrypoint(this_path, toadua_json_path = None):
  if toadua_json_path is None:
    p = "200708-last-toadua-dump.json"
    if os.path.isfile(p):
      toadua_json_path = p
    else:
      print("Not enough parameters.")
      return
  t1 = time.time()
  this_dir = os.path.dirname(os.path.abspath(this_path)) + os.path.sep
  toadaı = routines.dicts_from_json_path(toadua_json_path)
  print(f"  Initial number of entries: {str(len(toadaı))}")
  i = 0
  l = len(toadaı)
  log = ""
  n_removed_donwvoted = 0
  extras = []
  excl = {
    "official":     0,
    "oldofficial":  0,
    "examples":     0,
    "oldexamples":  0,
    "countries":    0,
    "oldcountries": 0
  }
  t2 = time.time()
  while i < l:
    if ((not type(toadaı[i]) is OrderedDict)
        or ("head" not in toadaı[i]) or ("user" not in toadaı[i])):
      e = toadaı.pop(i)
      log += "Removing anomalous element \"" + str(e) + "\"...\n"
      l -= 1
    elif ("score" in toadaı[i] and toadaı[i]["score"] < 0
          and toadaı[i]["user"] not in ("official", "examples")):
      # Unofficial downvoted entry
      toadaı.pop(i)
      l -= 1
      n_removed_donwvoted += 1
    else:
      user = toadaı[i]["user"]
      if user in excl:
        excl[user] += 1
        extras.append(toadaı.pop(i))
        l -= 1
      else:
        process_entry(i, toadaı)
        i += 1
  d = time.time() - t2
  if log != "":
    print(log)
  def print_count(count, name):
    if count > 0:
      print("  " + str(count) + " " + name + " entr"
            + ("y has" if count == 1 else "ies have")
            + " been removed.")
  print_count(n_removed_donwvoted, "downvoted")
  for k in excl:
    print_count(excl[k], k)
  print("  New number of entries: " + str(len(toadaı)) + ".")
  print("  Dictionary processed in {:.3f} seconds.".format(d))
  routines.save_as_json_file(toadaı, this_dir + "toadai-0.json")
  routines.save_as_json_file(extras, this_dir + "feedback_on_imported_entries.json")
  print("  Total execution time:   {:.3f} seconds.".format(
    time.time() - t1))


def random_id():
  cs = (
    "0123456789-_abcdefghijklmnopqrstuvwxyzABCDERFGIJKLMNOPQRSTUVWXYZ"
  )
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
  return s

def normalized(s):
  s = re.sub(u'ı', u'i', s)
  s = re.sub(u'ȷ', u'j', s)
  s = re.sub(u"(?<=^)['’]", u'', s)
  s = re.sub(u'[x’]', u"'", s)
  if is_a_lexeme(s):
    s = unicodedata.normalize('NFD', s)
    # s = re.sub(u'(?!\u0304)[\u0300-\u030f]', u'', s)
    s = re.sub(u"[^0-9A-Za-zı\u0300-\u030f'_ ()«»,;.…!?]+", u' ', s)
    # ^ \u0300-\u030f are combining diacritics.
    s = s.lower()
  s = unicodedata.normalize('NFC', s)
  s = re.sub(u' +', u' ', s)
  # ⌵ Restoring missing macrons:
  p = u"([aeiıouyāēīōūȳáéíóúýäëïöüÿǎěǐǒǔảẻỉỏủỷâêîôûŷàèìòùỳãẽĩõũỹ][aeiıouy]*q?['bcdfghjklmnprstz]h?[aeiouy])(?![\u0300-\u030f])"
  s = re.sub(p , u'\\1\u0304', s)
  s = unicodedata.normalize('NFC', s)
  s = re.sub(u'i', u'ı', s)
  s = convert_caron_to_diaresis(s)
  return s.strip()

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

def process_entry(i, dict):
  entry = dict[i]
  entry["official"] = False
  entry["author"] = entry.pop("user")
  entry["toaq"]   = entry.pop("head")
  # OK: id, date
  if entry["toaq"] in ("@toacia", "?", "???"):
    entry["toaq"] = "???"
  else:
    entry["toaq"]           = normalized(entry["toaq"])
    entry["is_a_lexeme"]    = is_a_lexeme(entry["toaq"])
  entry["audio"]            = []
  entry["class"]            = ""
  entry["frame"]            = ""
  entry["distribution"]     = ""
  entry["generics"]         = ""
  entry["noun_classes"]     = ""
  entry["slot_tags"]        = []
  entry["tags"]             = []
  entry["examples"]         = []
  lcs = {"en": "eng", "fr": "fra", "es": "spa", "de": "deu",
         "pl": "pol", "ja": "eng"}
         # No, "ja":"eng" is not a mistake: unfortunately in the Toadua database all the "ja"-labelled entries are actually in English and not in Japanese... :'(
  lc = entry.pop("scope")
  entry["target_language"]  = lcs.get(lc, lc)
  assert len(entry["target_language"]) != 2
  entry["definition_type"]  = "informal"
  entry["definition"]       = entry.pop("body")
  if entry["target_language"] == "eng":
    entry["definition"] = entry["definition"].replace("◌", "▯")
  elif entry["target_language"] == "toa":
    if len(entry["definition"]) >= 2:
      if entry["definition"][:2] == "⚙ ":
        entry["definition"] = entry["definition"][2:]
        entry["definition_type"]         = "meta"
      elif entry["definition"][:2] == "= ":
        entry["definition"] = entry["definition"][2:]
        entry["definition_type"]         = "formal"
      elif entry["definition"][:2] == "≈ ":
        entry["definition"] = entry["definition"][2:]
  assert len(entry["definition"]) > 0
  entry["gloss"]            = ""
  entry["keywords"]         = []
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
  entry["notes"]            = []
  m = re.match("(\(fork of #[^ )]+\))", entry["definition"])
  if m:
    fn = m.groups()[0]
    entry["definition"] = entry["definition"][len(fn) + 1 :]
    entry["notes"] += [fn]
  # OK: score, votes
  # Reordering:
  order = (
    "id", "official", "date", "author", "toaq", "is_a_lexeme", "example_id", "audio", "class", "frame", "distribution", "generics", "noun_classes", "slot_tags", "tags", "examples", "target_language", "definition_type", "definition", "notes", "gloss", "keywords", "segmentation", "etymology", "related", "derived", "synonyms", "antonyms", "hypernyms", "hyponyms", "comments", "score", "votes"
  )
  # assert(all(map(lambda key: key in order, list(entry.keys()))))
  diff = set(entry.keys()) - set(order)
  if diff != set():
    print("FOREIGN KEYS: " + str(diff))
  dict[i] = OrderedDict(
    (key, entry[key]) for key in order if key in entry)

def is_a_contentive(s):
  return None != re.match(
    ( u"([bcdfghjklmnprstz]h?)?[aeiıouy]+q?"
    + u"((['bcdfghjklmnprstz]h?)[āēīōūȳ][aeiouy]*q?)*$"),
    s)

def is_a_lexeme(s):
  return (
    is_a_contentive(s) or None != re.match(
      u"[áéíóúýäëïöüÿǎěǐǒǔảẻỉỏủỷâêîôûŷàèìòùỳãẽĩõũỹ][aeiıouy]*$", s)
  )


# === ENTRY POINT === #

entrypoint(*sys.argv)
   

