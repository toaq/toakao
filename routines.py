# -*- coding: utf-8 -*-

import os, csv, json
from collections import OrderedDict

def edit_json_from_path(input_path, function, output_path = None):
  if output_path == None:
    output_path = (lambda t: t[0] + "-out" + t[1])(
      os.path.splitext(input_path)
    )
  # TODO: Handle the case where both paths are the same:
  # open the file in read-write mode, then inputf = outputf.
  with open(input_path,  "r", encoding="utf8") as inputf, \
       open(output_path, "wb")                 as outputf:
    ds = json.loads(inputf.read(), object_pairs_hook = OrderedDict)
    outputf.truncate()
    outputf.write(
      bytes(
        json.dumps(function(ds), indent = 2, ensure_ascii = False),
        encoding = "utf8"
      )
    )

def dicts_from_json_path(path):
  with open(path, "r", encoding = "utf-8") as f:
    return json.loads(f.read(), object_pairs_hook = OrderedDict)

def table_from_csv_path(path, delim):
  with open(path, "r", encoding = "utf-8") as f:
    r = csv.reader(f, delimiter = delim)
    t = []
    for row in r:
      t.append(row)
    return t

def table_gen_from_csv_path(path, delim):
  with open(path, "r", encoding = "utf-8") as f:
    return csv.reader(f, delimiter = delim)

def dicts_from_json_url(url):
  import requests
  response = requests.get(url)
  response.raise_for_status()
  assert response.status_code == 200, (
    'Wrong status code :' + str(response.status_code))
  return json.loads(response.content)

def table_from_csv_url(url):
  import requests, io
  response = requests.get(url)
  response.raise_for_status()
  assert response.status_code == 200, (
    'Wrong status code :' + str(response.status_code))
  content = io.StringIO(response.content.decode("UTF8"), newline = None)
  csv_reader = csv.reader(content, delimiter=',')
  table = []
  for row in csv_reader:
    table.append(row)
  return table

def edit_csv_from_path(path, delim, func, outp = None):
  if outp == None:
    outp = (lambda t: t[0] + "-out" + t[1])(os.path.splitext(path))
  # TODO: Handle the case where both paths are the same:
  # open the file in read-write mode, then path = outp.
  with open(path, "r", newline='', encoding='utf-8') as i, \
       open(outp, "w", newline='', encoding='utf-8') as o:
    r = csv.reader(i, delimiter = delim)
    w = csv.writer(o, delimiter = delim)
    t = []
    for row in r:
      t.append(row)
    t = func(t)
    w.writerows(t)

def save_as_csv_file(table, path):
  with open(path, "w", newline='', encoding='utf-8') as o:
    csv.writer(o, delimiter = ',').writerows(table)

def save_dicts_as_csv_file(dicts, path):
  with open(path, "w", newline='', encoding='utf-8') as o:
    keys, table = keys_and_table_from_dict(dicts)
    table.insert(0, keys)
    csv.writer(o, delimiter = ',').writerows(table)

def save_as_json_file(dicts, path, indent = 2):
  with open(path, "wb") as o:
    o.truncate()
    o.write(bytes(
      json.dumps(dicts, indent = indent, ensure_ascii = False),
      encoding = "utf8"
    ))

def keys_and_table_from_dict(dicts):
  keys = []
  table = []
  for d in dicts:
    assert isinstance(d, (dict, OrderedDict)), (
      f"keys_and_table_from_dict(): Wrong element type: {type(d)}")
    for k in d.keys():
      if k not in keys:
        keys.append(k)
  i = 0
  for d in dicts:
    table.append([])
    for k in keys:
      table[i].append(None if not k in d else d[k])
    i += 1
  return (keys, table)

def write_to_filepath(s, path):
  with open(path, "w", encoding = "utf-8") as out:
    out.truncate()
    out.write(s)

def dict_from_key_value(dictionaries, key, value):
  for d in dictionaries:
    if isinstance(d, (list, tuple, set, frozenset)):
      d = dict(d)
    if isinstance(d, (dict, OrderedDict)) and key in d:
      if d[key] == value:
        return d
  return None

def dict_index_from_key_value(dictionaries, key, value):
  i = 0
  l = len(dictionaries)
  while i < l:
    d = dictionaries[i]
    if isinstance(d, (list, tuple, set, frozenset)):
      d = dict(d)
    if isinstance(d, (dict, OrderedDict)) and key in d:
      if d[key] == value:
        return i
    i += 1
  return None

