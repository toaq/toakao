# -*- coding: utf-8 -*-

# COPYRIGHT LICENSE: See LICENSE.md in the top level directory.
# SPDX-License-Identifier: ISC

# PURPOSE:
# In a nutshell, this script takes the unofficial toadaı.json dictionary as input, then download the official dictionary and the example sentence spreadsheet, then merges them under a new JSON template and outputs the result in a separate file `toatuq.json` (the input files are not modified).

# USAGE: $ python update.py
# OUTPUT: toakao.yaml, nonlemmas.yaml, muakao.yaml, orphanes.yaml, deleted.yaml

# ==================================================================== #

import sys, os, time, io, subprocess, requests, itertools
import json, csv, re
from datetime import datetime
import dep.pytoaq.latin as pytoaq
from routines import *

# ==================================================================== #

TOADUA_SCORE_THRESHOLD = 0

OFFICIAL_DICTIONARY_URL = "https://raw.githubusercontent.com/toaq/dictionary/master/dictionary.json"
TOADUA_DOWNLOAD_COMMAND = 'wget -O- https://toadua.uakci.space/api --post-data \'{"action":"search","query":["term",""]}\' | jq .results'


# ==================================================================== #

def entrypoint(this_path):
	t1 = time.time()
	this_dir = os.path.dirname(os.path.abspath(this_path)) + os.path.sep
	toakao_path = this_dir + "toakao.yaml"
	nonlemmas_path = this_dir + "nonlemmas.yaml"
	muakao_path = this_dir + "muakao.yaml"
	orphanes_path = this_dir + "orphanes.yaml"
	deleted_path = this_dir + "deleted.yaml"
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
	except:
		print(
			f"Unexpected error upon {step_desc}: {str(sys.exc_info()[0])}")
		sys.exit()
	print("Download time: {:.3f} seconds.".format(time.time() - t1))
	print("Opening the previous Toakao file…")
	t2 = time.time()
	old_toakao = object_from_yaml_path(toakao_path)
	print("Duration: {:.3f} seconds.".format(time.time() - t2))
	print("Now unifying the data from these different sources…")
	official_dict, muakao = reformat_official_dictionary(official_dict)
	toadua, muakao2 = reformated_toadua(toadua)
	muakao += muakao2
	toakao = official_dict + toadua
	# ⌵ Merging duplicates.
	toakao, orphanes = with_merged_entries(toakao)
	toakao, nonlemmas = postprocessed(toakao)
	print(f"toakao: {len(toakao)} entries.")
	print(f"muakao: {len(muakao)} entries.")
	print(f"nonlemmas: {len(nonlemmas)} entries.")
	print(f"orphanes: {len(orphanes)} entries.")
	toakao, deleted = sync_with(old_toakao, toakao)
	# ⌵ Saving files.
	print("Saving files…")
	t3 = time.time()
	save_as_yaml_file(toakao, toakao_path)
	save_as_yaml_file(muakao, muakao_path)
	save_as_yaml_file(nonlemmas, nonlemmas_path)
	save_as_yaml_file(orphanes, orphanes_path)
	save_as_yaml_file(deleted, deleted_path)
	print("Duration: {:.3f} seconds.".format(time.time() - t3))
	# print(f"Toakao entry count: {len(toakao)}.")
	print("Total execution time:     {:.3f} seconds.".format(
		time.time() - t1))
	return

def is_official_author(author):
	return author in {
		"official", "Hoemai", "solpahi", "official-examples"
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
	def winning_over(e, ε):
		for f in WINNER_SELECTION_FUNCTIONS:
			winner = the_most(e, ε, f)
			if winner == e:
				return True
			elif winner == ε:
				return False
			else:
				return None
	orphaned_definitions = []
	lex = dict()
	for i, e in enumerate(d):
		assert e is not None
		assert e["toaq"] != ""
		initial = e["toaq"][0]
		if initial in "NCSncs" and len(e["toaq"]) > 1:
			if e["toaq"][1] in "Hh":
				initial += e["toaq"][1]
		if initial not in lex.keys():
			lex[initial] = []
		if len(lex[initial]) == 0:
			lex[initial].append(e)
		else:
			is_found = False
			for ι, ε in enumerate(lex[initial]):
				if ε is None:
					continue
				if e["toaq"] == ε["toaq"]:
					is_found = True
					new_translation = e["translations"][0]
					j = 0
					lim = len(ε["translations"])
					while j < lim:
						if (
							ε["translations"][j]["language"]
							== new_translation["language"]
						):
							break
						j += 1
					if j == lim: # This is a translation in a new language.
						 ε["translations"].append(new_translation)
					elif True or not forall(
						lambda k: e[k] == ε[k],
						["toaq", "is_official", "type", "definition_type", "translations"]
					):
						# ⟦e⟧ and ⟦ε⟧ are have same-language definitions competing for the same lemma.
						# Of these two definitions, there must remain only one.
						lang = new_translation['language']
						ws = winning_over(
							new_translation, ε["translations"][j])
						if ws is None:
							if False:
								print(
									f"[⚠ WARNING ⚠] Resolution of competing definitions:\n"
									+ f"  Cannot satisfyingly break the tie between the following entries:\n"
									+ f"  • #{e['id']} {e['toaq']}\n"
									+ f"  • #{ε['id']} {ε['toaq']}\n"
									+ f"  By default, the entry with the lowest index is therefore selected."
								)
							ws = False
						if ws:
							kept = new_translation
							discarded = ε['translations'][j]
						else:
							kept = ε['translations'][j]
							discarded = new_translation
						# print(
						# 	f"◈ For lemma ⟪{e['toaq']}⟫, discarding ⟦{lang}⟧ "
						# 	+ f"translation ⟪{discarded}⟫ for ⟪{kept}⟫.")
						orphaned_definitions.append((ε["toaq"], discarded))
						ε["translations"][j] = kept
						assert isinstance(kept, dict)
					break
			if not is_found:
				lex[initial].append(e)
				# print(f"ADD {e['toaq']}")
	lex = [lex[initial] for initial in lex]
	lex = list(itertools.chain.from_iterable(lex))
	return (lex, orphaned_definitions)

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
		e = dictionary[i]
		if e["examples"] != []:
			examples.append((e["examples"], e["toaq"]))
	return (dictionary, examples)

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
		else:
			toadua[i] = None
			# ↑ ‘None’ entries will be removed from ⟦toadua⟧ at a latter step.
			# Deleting it now would mess with ‘enumerate’.
	toadua = [e for e in toadua if e is not None]
	return (toadua, examples)

def toadua_entry_shall_be_included(entry):
	return (
		entry["score"] >= TOADUA_SCORE_THRESHOLD
		and entry["user"] not in {
			"oldofficial", "oldexamples", "oldcountries"
		}
	)

LANGUAGE_CODE_MAP = {
	"toa": "qtq",
	"en": "eng", "es": "spa", "zh": "cmn", "ar": "ara", "hi": "hin",
	"ru": "rus", "pt": "por", "ms": "msa", "fr": "fra", "de": "deu",
	"bn": "ben", "ja": "jpn", "fa": "fas", "sw": "swa", "ta": "tam",
	"it": "ita", "jv": "jav", "te": "tel", "ko": "kor", "tr": "tur",
	"pl": "pol", "nl": "nld", "is": "isl", "tl": "tgl", "ch": "cha",
	"bg": "bul",
	"eo": "epo", "jbo": "jbo", "vo": "vol", "vp": "qpv", "qit": "qit"
}

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
		id = "official:" + toaq_item
		definition = entry.pop("english")
		author = "official"
		date = ""
		notes = "\n".join(entry.pop("notes"))
		comments = []
	elif "head" in entry:
		# Toadua dictionary
		toaq_item = entry.pop("head")
		definition = entry.pop("body")
		id = entry.pop("id")
		author = entry.pop("user")
		date = entry.pop("date")
		notes = ""
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
	two_letters_language_code = pop_else("scope", "en")
	language_code = LANGUAGE_CODE_MAP.get(
		two_letters_language_code, two_letters_language_code)
	if len(language_code) == 2:
		print(f"❖❖❖ [WARNING] Unknown 2-letter language code: "
					+ f"“{language_code}”")
	definition_type = "informal"
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
	is_a_lemma = (
		pytoaq.is_a_lemma(toaq_item) or pytoaq.is_a_lemma(
			with_replaced_chars(
				toaq_item, "áéíóúâêîôûäëïöü", "aeıouaeıouaeıou")
		)
	)
	r = {
		"id":               id,
		"toaq":             toaq_item,
		"is_a_lemma":       is_a_lemma,
		"is_official":      is_official_author(author),
		"type":             pop_else("type", ""),
		"frame":            pop_else("frame", ""),
		"distribution":     pop_else("distribution", ""),
		"pronominal_class": pop_else("pronominal_class", ""),
		"subject":          pop_else("subject", ""),
		"examples":         pop_else("examples", []),
		"etymology":        [],
		"etymological_notes": "",
		"sememe":           "",
		"definition_type":  definition_type,
		"translations":     [{
			"language":         language_code,
			"definition":       definition,
			"notes":            notes,
			"gloss":            pop_else("gloss", ""),
			"author":           author,
			"date":             date,
			"score":            pop_else("score", 0)
		}]
	}
	return with_toadua_note_fields(r, comments)

def with_toadua_note_fields(entry, notes):
	# We will walk the notes from the most recent one to the most ancient one,
	# looking for field-value expressions such as ⟪type: illocution⟫,
	# and for each field we will at most pick a single assignment, namely
	# the most recent one.
	notes = reversed(notes)
	ks = [k for k in entry.keys() if k not in [
		"id", "toaq", "is_official"]]
	for note in notes:
		for k in ks:
			t = note["content"]
			if t.startswith(k) or t.startswith(k.capitalize()):
				t = t[len(k):]
				if t.startswith(":") or t.startswith("s:"):
					entry[k] = t[t.index(":")+1:].strip()
					ks.remove(k)
					# TODO: Handle multiple notes each starting with ⟪example:⟫.
	if isinstance(entry["etymology"], str):
		entry["etymological_notes"] = entry["etymology"]
		entry["etymology"] = []
	return entry

def postprocessed(toakao):
	nonlemmas = []
	i = 0
	while i < len(toakao):
		if not toakao[i]["is_a_lemma"]:
			nonlemmas.append(toakao.pop(i))
			continue
		for k in ["is_a_lemma", "id"]:
			if k in toakao[i]:
				toakao[i].pop(k)
		for translation in toakao[i]["translations"]:
			lang = translation["language"]
			toakao[i][lang + "_definition"] = translation["definition"]
			toakao[i][lang + "_notes"] = translation["notes"]
			toakao[i][lang + "_gloss"] = translation["gloss"]
		toakao[i].pop("translations")
		toakao[i] = {
			key if key != 'toaq' else 'lemma': value
			for key, value in toakao[i].items()
		} # renaming the key ⟪toaq⟫ to ⟪lemma⟫
		i += 1
	toakao = sorted(toakao, key = lambda x: x["lemma"])
	return (toakao, nonlemmas)

def sync_with(old, new):
	# We assume that both are already sorted alphabetically.
	added = []
	deleted = []
	oi = 0
	ni = 0
	while oi < len(old) and ni < len(new):
		if old[oi]["lemma"] < new[ni]["lemma"]:
			deleted.append(old[oi])
			old[oi] = None
			oi += 1
		elif old[oi]["lemma"] > new[ni]["lemma"]:
			added.append(new[ni])
			ni += 1
		else:
			for k in new[ni].keys():
				if new[ni][k] not in ("", []):
					if k not in old[oi]:
						old[oi][k] = ""
					if old[oi][k] != new[ni][k]:
						print(
							f"❖ {old[oi]['lemma']}.{k}: "
							+ f"new ⟪{new[ni][k]}⟫ ≠ old ⟪{old[oi][k]}⟫."
						)
						old[oi][k] = new[ni][k]
			oi += 1
			ni += 1
	print(f"❖ ADDED: {[e['lemma'] for e in added]}")
	print(f"❖ REMOVED: {[e['lemma'] for e in deleted]}")
	old = [e for e in old if e != None]
	old += added
	old = sorted(old, key = lambda e: e["lemma"])
	return (old, deleted)


# ==================================================================== #

### MISCELLANEOUS ROUTINES ###

def forall(property, iterable):
	return all([property(e) for e in iterable])

def with_replaced_chars(s, srclist, dstlist):
	r = ""
	for c in s:
		for i, sc in enumerate(srclist):
			if c == sc:
				c = dstlist[i]
		r += c
	return r

# ==================================================================== #

# === ENTRY POINT === #

entrypoint(*sys.argv)

