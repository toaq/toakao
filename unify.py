# -*- coding: utf-8 -*-

# COPYRIGHT LICENSE: See LICENSE.md in the top level directory.
# SPDX-License-Identifier: ISC

# PURPOSE:
# In a nutshell, this script takes the unofficial toadaı.json dictionary as input, then download the official dictionary and the example sentence spreadsheet, then merges them under a new JSON template and outputs the result in a separate file `toatuq.json` (the input files are not modified).

# USAGE: $ python unify.py
# OUTPUT: toatuq.json

# ==================================================================== #

import sys, os, time, io, subprocess, requests
import json, csv, re, random
from datetime import datetime
from collections import OrderedDict
import dep.pytoaq.latin as pytoaq
from routines import *

# ==================================================================== #

EXAMPLES_ARE_LINKS = True
TOADUA_SCORE_THRESHOLD = 0

OFFICIAL_DICTIONARY_URL = "https://raw.githubusercontent.com/toaq/dictionary/master/dictionary.json"
TOADUA_DOWNLOAD_COMMAND = 'wget -O- https://toadua.uakci.pl/api --post-data \'{"action":"search","query":["term",""]}\' | jq .results'
A_SENTENCES_URL = 'https://docs.google.com/spreadsheet/ccc?key=1bCQoaX02ZyaElHiiMcKHFemO4eV1MEYmYloYZgOAhac&output=csv&gid=1395088029'
B_SENTENCES_URL = 'https://docs.google.com/spreadsheet/ccc?key=1bCQoaX02ZyaElHiiMcKHFemO4eV1MEYmYloYZgOAhac&output=csv&gid=574044693'
O_SENTENCES_URL = 'https://docs.google.com/spreadsheet/ccc?key=1bCQoaX02ZyaElHiiMcKHFemO4eV1MEYmYloYZgOAhac&output=csv&gid=1905610286'
COUNTRIES_URL = 'https://docs.google.com/spreadsheet/ccc?key=1P9p1D38p364JSiNqLMGwY3zDRPQ_f6Yob_OL-uku28Q&output=csv&gid=637793855'

# ==================================================================== #

def entrypoint(this_path):
  t1 = time.time()
  this_dir = os.path.dirname(os.path.abspath(this_path)) + os.path.sep
  toatuq_path = this_dir + "toatuq.json"
  orphanes_path = this_dir + "orphanes.json"
  print("Collecting remote vocabulary sources…")
  try:
    step_desc = "attempting to download the official dictionary"
    official_dict = dicts_from_json_url(OFFICIAL_DICTIONARY_URL)
    step_desc = "attempting to download the Toadua dictionary"
    if True:
      result = subprocess.run(
        TOADUA_DOWNLOAD_COMMAND,
        shell = True, capture_output = True, text = True
      )
      assert result.stdout not in {None, ""}
      toadua = json.loads(result.stdout)
    else:
      toadua = dicts_from_json_path("archives/toadua-test.json")
    step_desc = "attempting to download the spreadsheets"
    a_sentences = table_from_csv_url(A_SENTENCES_URL)
    b_sentences = table_from_csv_url(B_SENTENCES_URL)
    o_sentences = table_from_csv_url(O_SENTENCES_URL)
    countries   = table_from_csv_url(COUNTRIES_URL)
  except:
    print(
      f"Unexpected error upon {step_desc}: {str(sys.exc_info()[0])}")
    sys.exit()
  print("Download time: {:.3f} seconds.".format(time.time() - t1))
  print("Now unifying the data from these different sources…")
  reformat_official_dictionary(official_dict)
  toadua = reformated_toadua(toadua)
  toatuq = official_dict + toadua
  # ⌵ Importing country names, ignoring the two first rows.
  ## toatuq += dicts_from_countries(countries[2:])
  # ⌵ Importing example sentences, ignoring the two first rows.
  toatuq += dicts_from_sentences(a_sentences[2:], "examples")
  toatuq += dicts_from_sentences(b_sentences[2:], "examples")
  toatuq += dicts_from_sentences(o_sentences[2:], "official-examples")
  # ⌵ Merging duplicates.
  toatuq, orphanes = with_merged_entries(toatuq)
  # ⌵ Saving files.
  save_as_json_file(toatuq, toatuq_path)
  save_as_json_file(orphanes, orphanes_path)
  print(f"Toatuq entry count: {len(toatuq)}.")
  print("Total execution time:     {:.3f} seconds.".format(
    time.time() - t1))
  return

list_from_table = lambda table: [item for row in table for item in row]

def assert_words_uniqueness(new_words, toatuq):
  intersection = new_words.intersection(
    set(tuple(list_from_table([e["toaq"] for e in toatuq]))))
  if intersection != set():
    print(f"COMPETING DEFINITION(S) FOUND FOR: {intersection}")
  return

# TODO: Use a prioritization scheme (date, vote count…) and log discarded items.
def append_if_unique(d1, d2):
  s = set(tuple(list_from_table([e["toaq"] for e in d2])))
  assert_words_uniqueness(s, d1)
  d1.extend(d2)
  return d1

def is_official_author(author):
  return author in {
    "official", "Hoemai", "solpahi", "official-examples"
  }

# ==================================================================== #

### PROCESSING SPREADSHEETS ###

def dicts_from_sentences(sentences, author):
  # date = datetime.utcnow().isoformat()
  ds = []
  for row in sentences:
    if len(row) < 3:
      return ds
    example_id, toaq, definition = row[:3]
    if row[1] != "" and row[2] != "":
      e = entry_from_toaq_and_def(
        toaq, definition, "eng", [], author, "example:" + example_id
      )
      e["example_id"] =  example_id
      ds.append(e)
  return ds

def dicts_from_countries(countries):
  templates = {
    ("culture", "", "▯ pertains to the culture of {}."),
    ("country", "gua", "▯ is the country {}."),
    ("language", "zu", "▯ is (one of) the language(s) spoken in {}."),
    ("citizenship", "poq", "▯ is a citizen, inhabitant or person originating from {}.")
  }
  ds = []
  for row in countries:
    if len(row) < 2:
      continue
    culture_word = normalized_with_report(row[1])
    if culture_word != "":
      country_name = format_country_name(row[0])
      for kind, suffix, template in templates:
        id ="countries:" + str(countries.index(row) + 1) + ":" + kind
        ds.append(entry_from_toaq_and_def(
          culture_word + suffix, "eng", template.format(country_name),
          [kind], "countries", id))
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
  toaq, definition, language, tags, author, id
):
  return {
    "translations": [{
      "language": language,
      "definition_type": "informal",
      "definition": definition,
      "notes": "",
      "gloss": "",
      "author": author
    }],
    "toaq_forms": [{
      "id": id,
      "is_official": is_official_author(author),
      "author": author,
      "toaq": [normalized_with_report(toaq)],
      "is_a_lemma": pytoaq.is_a_lemma(toaq),
      "audio": [],
      "class": ""
    }],
    "distribution": "",
    "slot_tags": [],
    "tags": tags
  }

# ==================================================================== #

DATE_TEMPLATE = '%Y-%m-%dT%H:%M:%S.%fZ'

def timestamp_from_date_text(date_text):
  try:
    return datetime.strptime(date_text, DATE_TEMPLATE).timestamp()
  except:
    return 0

WINNER_SELECTION_FUNCTIONS = [
  lambda _: 1 if is_official_author(_["author"]) else 0,
  lambda _: _["score"] if "score" in _ else 0,
  lambda _: -timestamp_from_date_text(_.get("date", None))
]

def with_merged_entries(d):
  def ε_target(e, ε, k1, k2):
    l = [x[k2] for x in ε[k1]]
    return l.index(e[k1][0][k2])
  def winner_of(e, ε, k1, n):
    for f in WINNER_SELECTION_FUNCTIONS:
      winner = the_most(
        e[k1][0],
        ε[k1][n],
        f
      )
      if winner != None:
        break
    if winner is None:
      def φ(l, i, key):
        return l["toaq_forms"][i].get(key, '∅')
      print(
        f"[⚠ WARNING ⚠] Resolution of competing definitions:\n"
        + f"  Cannot satisfyingly break the tie between the following entries:\n"
        + f"  • #{φ(e, 0, 'id')} {φ(e, 0, 'toaq')}\n"
        + f"  • #{φ(ε, n, 'id')} {φ(ε, n, 'toaq')}\n"
        + f"  By default, the entry with the lowest index is therefore selected."
      )
      winner = ι
    return winner
  def ω(a, b, k1, k2):
    for x in b[k1]:
      if a[k1][0][k2] == x[k2]:
        return True
    return False
  orphaned_definitions = []
  for i, e in enumerate(d):
    if i % 500 == 0:
      print(f"◇◈◇ #{i}")
    assert d[i] is not None
    for ι, ε in enumerate(d[:i]):
      if ι >= i:
        break
      if ε is None:
        continue
      if ω(e, ε, "toaq_forms", "toaq"):
        if ω(e, ε, "translations", "language"):
          # ⟦e⟧ and ⟦ε⟧ are have same-language definitions competing for the same head words.
          # Of these two definitions, there must remain only one.
          n = ε_target(e, ε, "toaq_forms", "toaq")
          w = winner_of(e, ε, "toaq_forms", n)
          if w == i:
            print(f"◈ #{i} STEALS {ε['toaq_forms'][n]['toaq']} FROM #{ι}.")
            ε["toaq_forms"][:n] + ε["toaq_forms"][n + 1:]
            if len(ε["toaq_forms"]) == 0:
              print(f"◈ #{ι} is now orphaned!")
            orphaned_definitions.append(d[ι])
            d[ι] = None
          else:
            j = ε_target(e, ε, "translations", "language")
            w = winner_of(e, ε, "translations", j)
            if w == i:
              print(f"◈ #{i}'s definition overwrites the same-language one in #{ι}.")
              ε["translations"][n] = e["translations"][0]
              d[i] = None
            else:
              orphaned_definitions.append(d[i])
              d[i] = None
        else: # not ω(e, ε, "translations", "language")
          print(f"❖ Adding to {[x['toaq'] for x in ε['toaq_forms']]} in languages {[x['language'] for x in ε['translations']]} a new translation in language '{e['translations'][0]['language']}'.")
          ε["translations"] += e["translations"]
          d[i] = None
      else: # not (ω(e, ε, "toaq_forms", "toaq")
        if equal(e, ε, lambda _: _["distribution"]):
          for ɛt in ε["translations"]:
            et = e["translations"][0]
            if forall(lambda α: equal(et, ɛt, lambda β: β[α]),
                      {"language", "definition"}):
              # ⟦e⟧ and ⟦ε⟧ are synonyms and will be merged.
              # Specifically, the ⟦toaq_forms⟧ of the former will be added to that of the latter, and then the former will be replaced by a null value.
              #def φ(i, j, k):
              #  return d[i]['toaq_forms'][j][k]
              #print(
              #  f"◇ SYNONYM MERGER:\n"
              #  + f"  • #{i}: {φ(i, 0, 'id')} {φ(i, 0, 'toaq')}\n"
              #  + f"  • #{ι}: {φ(ι, 0, 'id')} {φ(ι, 0, 'toaq')}"
              #)
              ε["toaq_forms"] += e["toaq_forms"]
              d[i] = None
      if d[i] is None:
        break
  return ([x for x in d if x is not None], orphaned_definitions)

def equal(α, β, f):
  return f(α) == f(β)

def the_most(α, β, f):
  if f(α) > f(β):
    return α
  elif f(α) < f(β):
    return β
  else:
    return None


# ==================================================================== #

### PROCESSING THE OFFICIAL DICTIONARY ###

def reformat_official_dictionary(dictionary):
  examples = []
  for i, e in enumerate(dictionary):
    dictionary[i] = reformated_entry(dictionary[i])
    if EXAMPLES_ARE_LINKS:
      tf = dictionary[i]["toaq_forms"][0]
      examples += examples_as_new_entries(tf["examples"], tf["toaq"])
  return dictionary + examples

# ==================================================================== #

### PROCESSING THE TOADUA DICTIONARY ###

def reformated_toadua(toadua):
  print(f"  [Toadua] Initial number of entries: {str(len(toadua))}")
  d = []
  examples = []
  for i, e in enumerate(toadua):
    assert(forall(
      lambda α: α in e,
      {"id", "head", "scope", "body", "date", "score"}
    ))
    if toadua_entry_shall_be_included(e):
      toadua[i] = reformated_entry(e)
      if EXAMPLES_ARE_LINKS:
        tf = toadua[i]["toaq_forms"][0]
        examples += examples_as_new_entries(tf["examples"], tf["toaq"])
    else:
      toadua[i] = None
      # ↑ ‘None’ entries will be removed from ⟦toadua⟧ at a latter step.
      # Deleting it now would mess with ‘enumerate’.
  toadua += examples
  return [e for e in toadua if e is not None]

def toadua_entry_shall_be_included(entry):
  return (
    entry["score"] >= TOADUA_SCORE_THRESHOLD
    and entry["user"] not in {
      "oldofficial", "oldexamples", "oldcountries"
    }
  )

LANGUAGE_CODE_MAP = {
  "toa": "toa", "en": "eng", "fr": "fra", "es": "spa", "de": "deu",
  "pl": "pol", "is": "isl", "ja": "jpn", "zh": "cmn", "ch": "cha"}

def reformated_entry(entry):
  def pop_else(key, default):
    return entry.pop(key) if key in entry else default
  def check_key(key, default):
    if key not in entry:
      entry[key] = default
  def check_keys(keys, default):
    for key in keys:
      check_key(key, default)
  if "toaq" in entry:
    # Official dictionary
    toaq_item = entry.pop("toaq")
    definition = entry.pop("english")
    id = "official:" + toaq_item
    author = "official"
    date = ""
    notes = entry.pop("notes")
    comments = []
  elif "head" in entry:
    # Toadua dictionary
    toaq_item = entry.pop("head")
    definition = entry.pop("body")
    id = entry.pop("id")
    author = entry.pop("user")
    date = entry.pop("date")
    notes = []
    comments = pop_else("notes", [])
  else:
    # Unsupported dictionary
    raise Exception(
      "[Error] reformated_toadua_entry:\nNeither key ⟪head⟫ nor ⟪toaq⟫ were found.\n"
      + f"Content of the entry:\n{str(entry)}"
    )
  if toaq_item in ("@toacia", "?", "???"):
    print(f"❖❖❖ [Toadua] Discarding entry headed as ⟪{entry['toaq']}⟫: "
          + f"⟪{entry['body']}⟫.")
    return
  comments = [
    {
      "content": comment["content"],
      "date": iso_date_from_toadua_comment_date(comment["date"]),
      "author": comment["user"]
    } for comment in comments
  ]
  
  two_letters_language_code = pop_else("scope", "en")
  language_code = LANGUAGE_CODE_MAP.get(
    two_letters_language_code, two_letters_language_code)
  if len(language_code) == 2:
    print(f"❖❖❖ [WARNING] Unknown 2-letter language code: "
          + f"“{language_code}”")
  definition_type = "informal"
  fork_of = []
  if (len(definition) > 0x10 and definition[0] == '('):
    m = re.match("(fork of #[^ )]+)\) ", definition)
    if m:
      fork_message = m.groups()[0]
      definition = definition[len(fork_message) + 3 :]
      if "fork_of" in entry:
        fork_of = entry["fork_of"]
      fork_of += [fork_message[9:]]
      print(f"❖❖❖ #{id}: fork of {fork_message[9:]}.")
  match language_code:
    case "eng":
       definition = definition.replace("◌", "▯")
    case "toa":
      if len(definition) >= 2:
        match definition[:2]:
          case "⚙ ":
            definition      = definition[2:]
            definition_type = "meta"
          case "= ":
            definition      = definition[2:]
            definition_type = "formal"
          case "≈ ":
            definition = definition[2:]
            # ⟦definition_type⟧ remains set to "informal".
  assert(len(definition) > 0)
  keywords = []
  toadua_etymologies = []
  for comment in comments:
    content = comment["content"]
    m = re.match("([Kk]eywords?: )", content)
    if m is not None:
      if content[-1] == '.':
        content = content[:-1]
      keywords += [e.strip() for e in content[m.end():].split(",")]
    else:
      m = re.match("([Ee]tymology: )", content)
      if m is not None:
        toadua_etymologies += content[m.end():]
  # === Toaq Form map === #
  toaq_forms = [{
    "id":               id,
    "is_official":      is_official_author(author),
    "author":           author,
    "date":             date,
    "toaq":             toaq_item,
    "is_a_lemma":       pytoaq.is_a_lemma(toaq_item),
    "audio":            [],
    "class":            pop_else("type", ""),
    "is_namesake":      pop_else("namesake", None),
    "frame":            pop_else("frame", ""),
    "generics":         "",
    "noun_classes":     "",
    "examples":         pop_else("examples", []),
    "segmentations":    [],
    "etymology":        [],
    "toadua_etymologies": toadua_etymologies,
    "comments":         comments,
    "score":            pop_else("score", 0)
  }]
  # === Treanslation map === #
  translations = [{
    "language":         language_code,
    "definition_type":  definition_type,
    "definition":       definition,
    "notes":            notes,
    "keywords":         keywords,
    "gloss":            pop_else("gloss", ""),
    "fork_of":          fork_of,
    "author":           author,
    "date":             date,
    "score":            pop_else("score", 0)
  }]
  # === Main map === #
  entry = {
    "predilex_id":      "",
    "translations":     translations,
    "toaq_forms":       toaq_forms,
    "distribution":     pop_else("distribution", ""),
    "slot_tags":        pop_else("fields", []),
    "tags":             [],
  }
  for e in (
    "related", "derived", "similar", "synonyms", "antonyms",
    "hypernyms", "hyponyms"
  ):
    check_key(e, [])
  ## pop_else("votes", None)
  ## return reordered_entry(entry)
  return entry

def examples_as_new_entries(examples, item):
  item = item.replace(' ', '_')
  example_entries = []
  for i, ex in enumerate(examples):
    new_id = "official:" + item + ":" + str(i + 1)
    examples[i] = new_id
    example_entries.append({
      "translations": [
        {
          "language": language,
          "definition_type": "informal",
          "definition": definition,
          "notes": "",
          "gloss": "",
          "author": "official"
        } for language, definition in [
          (k, ex[k]) for k in ex if k != "toaq"
        ]
      ],
      "toaq_forms": [{
        "id": new_id,
        "is_official": True,
        "author": "official",
        "toaq": [ex["toaq"]],
        "is_a_lemma": False,
        "example_id": new_id,
        "audio": [],
        "class": ""
      }],
      "distribution": "",
      "slot_tags": [],
      "tags": ["example"]
    })
  return example_entries

def follows_iso_date(d1, d2):
  f = lambda x: filtered_string(x, lambda c: c in "0123456789")
  d1, d2 = f(d1), f(d2)
  l = min(len(d1), len(d2))
  i = 0
  while i < l:
    n1, n2 = int(d1[i]), int(d2[i])
    if n1 > n2:
      return True
    elif n1 < n2:
      return False
    i += 1
  return False # Same date

def filtered_string(s, p):
  r = ""
  for c in s:
    if p(c):
      r += c
  return r

def iso_date_from_toadua_comment_date(d):
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

# ==================================================================== #

### MISCELLANEOUS ROUTINES ###

def normalized_with_report(s):
  r = pytoaq.normalized(s)
  if r != s:
    print(f"NORMALIZED: {s}\n         -> {r}")
  return r

def random_id():
  cs = ("0123456789-_abcdefghijklmnopqrstuvwxyz"
        + "ABCDERFGIJKLMNOPQRSTUVWXYZ")
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

def forall(property, iterable):
  return all([property(e) for e in iterable])

# ==================================================================== #

# === ENTRY POINT === #

entrypoint(*sys.argv)

