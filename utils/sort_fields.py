
# ============================================================ #

import sys, os, time
from collections import OrderedDict
from common import edit_json_from_path

SELF_PATH = os.path.dirname(os.path.realpath(__file__))

# ============================================================ #

def entrypoint():
	start_time = time.time()
	path = SELF_PATH + "/../toakao.json"
	edit_json_from_path(
		path, sorted_from, output_path = path)
	print("Execution time: {:.3f}s.".format(
		time.time() - start_time))

FIELD_ORDER = (
    "lemma", "discriminator", "is_official", "dialect", "type", "frame", "distribution", "pronominal_class", "subject", "sememe", "tags", "examples", "synonyms", "etymology", "etymological_notes", "langdata", "definition_type", "eng_definition", "eng_notes", "eng_lem", "eng_gloss"
  )

def sorted_from(toakao):
	foreign_keys = set()
	i = 0
	while i < len(toakao):
		j = i
		i += 1
		if not isinstance(toakao[j], (dict, OrderedDict)):
			print(f"⚠ the type of ⟦toakao[{j}]⟧ is ⟦{type(toakao[j])}⟧")
			if type(toakao[j]) == list:
				print(f"  len = {len(toakao[j])}; first = ⟪{toakao[j][0]}⟫.")
		# assert(all(map(lambda key: key in order, list(entry.keys()))))
		diff = set(toakao[j].keys()) - set(FIELD_ORDER)
		if diff != set():
			foreign_keys &= diff
		entry = toakao[j]
		toakao[j] = OrderedDict(
			(key, entry[key]) for key in FIELD_ORDER if key in entry)
		for k in entry:
			if not k in FIELD_ORDER:
				toakao[j][k] = entry[k]
	if len(foreign_keys) > 0:
		print("FOREIGN KEYS: " + str(foreign_keys))
	return toakao

def tag_rank_of_row(row, tags_col_id):
	tags = row[tags_col_id]
	l = tags.split(" ")
	first = "" if l == [] else l[0]
	if first in HIERARCHY:
		return HIERARCHY.index(first)
	else:
		return len(HIERARCHY)


# ==================================================================== #

# === ENTRY POINT === #

entrypoint()

