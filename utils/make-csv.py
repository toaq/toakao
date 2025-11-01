# ============================================================ #

import sys, os, time, json

from common import object_from_json_path, save_dicts_as_csv_file

from fields import FIELD_ORDER

SELF_PATH = os.path.dirname(os.path.realpath(__file__))

# ============================================================ #

def entrypoint():
	start_time = time.time()
	def normalized(path):
		return path.replace("/", os.path.sep)
	data = object_from_json_path(
		SELF_PATH + normalized("/../toakao.json"))
	keys = sorted(
		sorted(all_keys_of(data)),
		key = lambda x: FIELD_ORDER.index(x)
			if x in FIELD_ORDER else len(FIELD_ORDER)
	)
	data = [transformed(e, keys) for e in data]
	save_dicts_as_csv_file(
		data, SELF_PATH + normalized("/../toakao.csv"),
		delimiter = ',')
	print("Execution time: {:.3f}s.".format(
		time.time() - start_time))

def all_keys_of(maplist):
	keys = set()
	for e in maplist:
		keys = keys.union(set(e.keys()))
	return keys

def transformed(entry, keys):
	entry["langdata"] = dict(entry.get("langdata", dict()))
	for k in ("examples", "etymology", "toadua_ids"):
		entry[k] = json.dumps(
				entry.get(k, []),
				ensure_ascii = False)
	for k in ("synonyms",):
		entry[k] = "; ".join(entry.get(k, []))
	return reordered(entry, keys)

def reordered(entry, keys):
	return dict(
		(key, entry.get(key, "")) for key in keys)

# ============================================================ #

# === ENTRY POINT === #

entrypoint()
 
