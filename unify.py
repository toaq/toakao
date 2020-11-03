# -*- coding: utf-8 -*-

# In a nutshell, this script takes the unofficial toadaı.json dictionary as input, then download the official dictionary and the example sentence spreadsheet, then merges them under a new JSON template and outputs the result in a separate file `toatuq.json` (the input files are not modified).

# USAGE: $ python unify.py
# OUTPUT: toatuq.json

# ==================================================================== #

import sys, os, io, requests, json, csv, re, unicodedata, random, time
import datetime
from collections import OrderedDict
from routines import *

EXAMPLES_ARE_LINKS = True

def entrypoint(this_path, toadaı_json_path = None):
  t1 = time.time()
  this_dir = os.path.dirname(os.path.abspath(this_path)) + os.path.sep
  if toadaı_json_path is None:
    toadaı_path = this_dir + "toadai.json"
  toatuq_path = this_dir + "toatuq.json"
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
  toatuq = dicts_from_json_path(toadaı_path)
  reformat(official_dict, toatuq)
  toatuq += official_dict
  # ⌵ Importing example sentences, ignoring the two first rows.
  append_if_unique(toatuq, dicts_from_sentences(
    a_sentences[2:], "a-sentences", False))
  append_if_unique(toatuq, dicts_from_sentences(
    b_sentences[2:], "b-sentences", False))
  append_if_unique(toatuq, dicts_from_sentences(
    o_sentences[2:], "toaq-org-examples", True))
  # ⌵ Importing country names, ignoring the two first rows.
  append_if_unique(toatuq, dicts_from_countries(
    countries[2:]))
  save_as_json_file(toatuq, toatuq_path)
  print(f"Toatuq entry count: {len(toatuq)}.")
  print("Total execution time:     {:.3f} seconds.".format(
    time.time() - t1))

flatten = lambda table: [item for row in table for item in row]

def append_if_unique(d1, d2):
  s = set(tuple(flatten([e["toaq"] for e in d2])))
  assert_words_uniqueness(s, d1)
  d1.extend(d2)
  return d1

def dicts_from_sentences(sentences, name, is_official):
  # date = datetime.datetime.utcnow().isoformat()
  ds = []
  for row in sentences:
    if len(row) < 3:
      return ds
    example_id, toaq, definition = row[:3]
    if row[1] != "" and row[2] != "":
      e = {
        "id": name + ":" + example_id,
        "official": is_official,
        "author": "examples",
        "toaq": [normalized_r(toaq)],
        "is_a_lexeme": False,
        "example_id": example_id,
        "target_language": "eng",
        "definition": definition,
        # "date": date,
        "tags": []
      }
      ds.append(e)
  return ds

def dicts_from_countries(countries):
  import enum
  #Col = enum.IntEnum("Col", "NAME CULTURE COUNTRY LANGUAGE")
  templates = {
    ("culture", "", "▯ pertains to the culture of {}."),
    ("country", "gūa", "▯ is the country {}."),
    ("language", "zū", "▯ is (one of) the language(s) spoken in {}."),
    ("citizenship", "pōq", "▯ is a citizen, inhabitant or person originating from {}.")
  }
  ds = []
  for row in countries:
    if len(row) < 2:
      continue
    culture_word = normalized_r(row[1])
    if culture_word != "":
      country_name = format_country_name(row[0])
      for kind, suffix, template in templates:
        ds.append(entry_from_toaq_and_def(
          culture_word + suffix, "eng", 
          template.format(country_name),
          [kind], "countries",
          str(countries.index(row) + 1) + ":" + kind))
  return ds

def format_country_name(name):
  original_name = name
  name = name.replace(" → ", " / ")
  name = re.sub("\[[^\]]*\]", "", name)
  l = re.split("( [/–] )", name)
  i = 0
  while i < len(l):
    l[i] = re.sub("([^,]+), ([^–]+)( – .+)*", "\\2 \\1\\3", l[i])
    if i >= 2:
      if l[i] == l[i - 2]:
        l[i - 2] = l[i - 1] = ""
    i += 2
  name = "".join(l)
  if original_name != name:
    print(f"format_country_name(): {original_name} -> {name}")
  return name

def entry_from_toaq_and_def(
  toaq, definition, language, tags, author, id):
  return {
    "id": author + ":" + id,
    "official": False,
    "author": author,
    "toaq": [normalized_r(toaq)],
    "is_a_lexeme": True,
    "translations": [{
      "language": language,
      "definition_type": "informal",
      "definition": definition
    }],
    "tags": tags
  }

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

def reformat(dictionary, toatuq):
  i = 0
  l = len(dictionary)
  while i < l:
    entry = dictionary[i]
    entry["official"] = True
    # Absent from official dict: id, date...
    def check_key(key, default):
      if key not in entry:
        entry[key] = default
    check_key("author", "Hoemai")
    if isinstance(entry["toaq"], str):
      entry["toaq"] = [normalized_r(entry["toaq"])]
    elif isinstance(entry["toaq"], (list, set)):
      entry["toaq"] = [normalized_r(e["toaq"]) for e in entry["toaq"]]
    else:
      raise Exception(
        f"Unexpected type for `toaq` key: {type(entry['toaq'])}")
    assert_words_uniqueness(set(tuple(entry["toaq"])), toatuq)
    check_key("id", "official:" + entry["toaq"][0])
    check_key("is_a_lexeme", is_a_lexeme(entry["toaq"][0]))
    if "type" in entry:
      entry["class"] = entry.pop("type")
    check_key("namesake", False)
    # if "frame" in entry:
    #   entry["serial_signature"]   = entry.pop("frame")
    if "fields" in entry:
      entry["tags"] = entry.pop("fields")
    check_key("examples", [])
    if EXAMPLES_ARE_LINKS:
      add_examples_as_new_entries(dictionary, entry)
    if "translations" in entry:
      for e in entry["translations"]:
        assert None not in {e["language"], e["definition"]}
    elif "english" in entry:
      assert len(entry["english"]) > 0
      def pop_else(key, default):
        return entry.pop(key) if key in entry else default
      entry["translations"]     = [{
        "language": "eng",
        "definition_type": "informal",
        "definition": entry.pop("english"),
        "notes": pop_else("notes", ""),
        "gloss": pop_else("gloss", ""),
        "short": pop_else("short", ""),
        "keywords": pop_else("keywords", "")
      }]
    else:
      raise Exception(
        "ERROR: No definition found in official dictionary for "
         + str(entry["toaq"]))
    check_key("audio",         [])
    check_key("generics",      "")
    check_key("noun_classes",  "")
    check_key("slot_tags",     [])
    check_key("segmentations", "")
    check_key("etymologies",   [])
    check_key("related",       [])
    check_key("derived",       [])
    check_key("synonyms",      [])
    check_key("antonyms",      [])
    check_key("hypernyms",     [])
    check_key("hyponyms",      [])
    # Reordering:
    order = (
      "id", "official", "date", "author", "toaq", "is_a_lexeme", "example_id", "audio", "class", "namesake", "frame", "distribution", "generics", "noun_classes", "slot_tags", "tags", "examples", "translations", "target_language", "definition_type", "definition", "notes", "gloss", "short", "keywords", "segmentations", "etymologies", "related", "derived", "synonyms", "antonyms", "hypernyms", "hyponyms", "comments", "score", "votes"
    )
    # assert(all(map(lambda key: key in order, list(entry.keys()))))
    diff = set(entry.keys()) - set(order)
    if diff != set():
      print("FOREIGN KEYS: " + str(diff))
    dictionary[i] = OrderedDict(
      (key, entry[key]) for key in order if key in entry
    )
    i += 1

def add_examples_as_new_entries(dictionary, entry):
  i = 0
  while i < len(entry["examples"]):
    ex = entry["examples"][i]
    new_id = "official:" + entry["toaq"][0] + ":" + str(i + 1)
    entry["examples"][i] = new_id
    dictionary.append({
      "id": new_id,
      "official": True,
      "author": "Hoemai",
      "toaq": [ex["toaq"]],
      "is_a_lexeme": False,
      "example_id": new_id,
      "translations": [
        {
          "language": language,
          "definition_type": "informal",
          "definition": definition
        } for language, definition in [
          (k, ex[k]) for k in ex if k != "toaq"]
      ],
      "tags": "example"
    })
    i += 1

def assert_words_uniqueness(new_words, toatuq):
  intersection = new_words.intersection(
    set(tuple(flatten([e["toaq"] for e in toatuq]))))
  if intersection != set():
    print(f"COMPETING DEFINITION(S) FOUND FOR: {intersection}")

def normalized_r(s):
  r = normalized(s)
  if r != s:
    print(f"NORMALIZED: {s} -> {r}")
  return r

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
   

