# ============================================================ #

import sys, os, time, json

from common import table_from_csv_path, save_as_json_file

from fields import FIELD_ORDER

SELF_PATH = os.path.dirname(os.path.realpath(__file__))

# ============================================================ #

def entrypoint():
	start_time = time.time()
	def normalized(path):
		return path.replace("/", os.path.sep)
	table = table_from_csv_path(
		SELF_PATH + normalized("/../toakao.csv"),
		delimiter = ",")
	header, content = table[0], table[1:]
	s = {"lemma", "discriminator", "type", "eng_definition"} - set(header)
	if s != set():
		n = "s" if len(s) != 1 else ""
		print(f"⚠ ERROR: Mandatory column{n} headers {s} missing!")
	else:
		data = [
			transformed({header[i] : e for i, e in enumerate(row)})
			for row in content
		]
		save_as_json_file(
			data, SELF_PATH + normalized("/../toakao.json"))
	print("Execution time: {:.3f}s.".format(
		time.time() - start_time))

def transformed(entry):
	def f(l):
		return [] if l == [""] else l
	entry["is_official"] = (
		entry["is_official"] in ("True", "true"))
	for k in ("examples", "langdata"):
		entry[k] = json.loads(entry.get(k, "[]"))
	for k in ("synonyms",):
		entry[k] = f(entry.get(k, "").split("; "))
	return reordered(entry)

def reordered(entry):
	def validated(key, entry):
		is_langkey = (
			not key == "etymological_notes"
			and any(
				[key.endswith(s) for s in (
					"_definition", "_notes", "_gloss")
				])
		)
		return key in entry and (not is_langkey or entry[key] != "")
	return dict(
		(key, entry[key]) for key in FIELD_ORDER if validated(key, entry))

# ============================================================ #

# === ENTRY POINT === #

entrypoint()


