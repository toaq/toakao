# -*- coding: utf-8 -*-

from routines import *
import sys, os, time

# ==================================================================== #

def entrypoint(this_path, json_path = None):
  t1 = time.time()
  this_dir = os.path.dirname(os.path.abspath(this_path)) + os.path.sep 
  if json_path is None:
    json_path = this_dir + "toadai-0.json"
  compare_with_gaqmekao(json_path, this_dir)
  print("  Total execution time:     {:.3f} seconds.".format(
    time.time() - t1))

def compare_with_gaqmekao(json_path, output_dir):
  json_name, ext = os.path.splitext(os.path.basename(json_path))
  if ext != ".json":
    json_name += ext
  ds = dicts_from_json_path(json_path)
  g = gaqmekao()
  #g = dicts_from_json_path("gaqmekao-201029.json")
  if g == None:
    print("/!\\ Unable to perform comparison with Gaqmekao.")
    return
  with open(
    "list_of_official_words_201019.txt", "r", encoding = "utf8"
  ) as owlf:
    official_words = set(owlf.read().split(", "))
    missing_from_gaqmekao = set()
    missing_from_toadai = set()
    def f(d1, d2, s):
      def_keys = ("english", "definition")
      for d1e in d1:
        is_found = False
        def1 = dict_elem_from_any_key(d1e, def_keys)
        for d2e in d2:
          def2 = dict_elem_from_any_key(d2e, def_keys)
          if (d1e["toaq"] == d2e["toaq"]
              and {def1, def1 + "."}.intersection({def2, def2 + "."})):
            is_found = True
            break
        if not is_found and d1e["toaq"] not in official_words:
          if not ("target_language" in d1e
                  and d1e["target_language"] != "eng"):
            s.add((d1e["toaq"], def1))
    f(ds, g, missing_from_gaqmekao)
    f(g, ds, missing_from_toadai)
    save_as_csv_file(missing_from_gaqmekao, ";",
                     output_dir + "missing_from_gaqmekao.csv")
    save_as_csv_file(missing_from_toadai, ";",
                     output_dir + f"missing_from_{json_name}.csv")
    dws = [normalized(e["toaq"]) for e in ds]
    gws = [normalized(e["toaq"]) for e in g]
    dus = (set(dws) - set(gws)) - official_words
    gus = (set(gws) - set(dws)) - official_words
    write_to_filepath(str(dus), "words_unique_to_toadai-0.txt")
    write_to_filepath(str(gus), "words_unique_to_gaqmekao.txt")

def gaqmekao():
  import requests
  url = (
    "https://raw.githubusercontent.com/robintown/gaqmekao/main/dictionary.json"
  )
  try:
    response = requests.get(url)
    response.raise_for_status()
  except Exception as err:
    print(f'Unable to load Gaqmekao. Error occurred: {err}')
    r = None
  else:
    r = json.loads(response.content.decode("UTF8"),
                   object_pairs_hook = OrderedDict)
  finally:
    return r

def dict_elements_from_any_key(dictionary, possible_keys):
  r = set()
  for k in possible_keys:
    if k in dictionary:
      r.add(dictionary[k])
  return r

def dict_elem_from_any_key(dictionary, possible_keys):
  r = None
  is_found = False
  for k in possible_keys:
    if k in dictionary:
      if not is_found:
        r = dictionary[k]
        is_found = True
      else:
        if r != dictionary[k]:
          raise Exception(
            "dict_elem_from_any_key(): more than one element found!")
  return r

def convert_caron_to_diaresis(s):
  cs = "ǎěǐǒǔ"
  ds = "äëïöü"
  i = 0
  while i < len(s):
    if s[i] in cs:
      s = s[:i] + ds[cs.index(s[i])] + s[i+1:]
    i += 1

def normalized(s):
  import re, unicodedata
  s = re.sub(u'ı', u'i', s)
  s = re.sub(u"(?<=^)['’]", u'', s)
  s = unicodedata.normalize('NFD', s)
  s = re.sub(u'[x’]', u"'", s)
  # s = re.sub(u'(?!\u0304)[\u0300-\u030f]', u'', s)
  s = re.sub(u"[^0-9A-Za-zı\u0300-\u030f'_ ()«»,;.…!?]+", u' ', s)
  # ^ \u0300-\u030f are combining diacritics.
  s = re.sub(u' +', u' ', s)
  # ⌵ Restoring missing macrons:
  p = u"([aeiıouyāēīōūȳáéíóúýäëïöüÿǎěǐǒǔảẻỉỏủỷâêîôûŷàèìòùỳãẽĩõũỹ][aeiıouy]*q?['bcdfghjklmnprstz]h?[aeiouy])(?![\u0300-\u030f])"
  s = re.sub(p , u'\\1\u0304', s)
  s = unicodedata.normalize('NFC', s)
  s = re.sub(u'i', u'ı', s)
  convert_caron_to_diaresis(s)
  return s.strip().lower()


# === ENTRY POINT === #

entrypoint(*sys.argv)

