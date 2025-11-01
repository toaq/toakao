# -*- coding: utf-8 -*-

# COPYRIGHT LICENSE: See LICENSE.md in the top level directory.
# SPDX-License-Identifier: ISC

# PURPOSE:
# This script synchronizes the content of the ⟦toakao.json⟧ file with the official Toaq dictionary and the Toadua community dictionary, fetching their data over the Internet; it also produces various JSON files storing dictionary entries which were discarded, such as non-lemma entries and disfavored competing wordings of definitions.

# USAGE: $ python update.py
# OUTPUT: toakao.json, nonlemmas.json, muakao.json, orphanes.json, deleted.json, discarded.json, ignored.json

# ==================================================================== #

import sys, os, time, io, subprocess, requests
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
	soakue_path = this_dir + "soakue-toakue.json"
	toakao_path = this_dir + "toakao.json"
	idmap_path = this_dir + "id-map.csv"
	nonlemmas_path = this_dir + "nonlemmas.json"
	muakao_path = this_dir + "muakao.json"
	deleted_path = this_dir + "deleted.json"
	discarded_path = this_dir + "discarded.json"
	ignored_path = this_dir + "ignored.json"
	print("Collecting remote vocabulary sources…")
	try:
		step_desc = "attempting to download the official dictionary"
		official_dict = dicts_from_json_url(OFFICIAL_DICTIONARY_URL)
		step_desc = "attempting to download the Toadua dictionary"
		result = subprocess.run(
			TOADUA_DOWNLOAD_COMMAND,
			shell = True, capture_output = True, text = True
		)
		assert result.stdout not in {None, ""}
		toadua = json.loads(result.stdout)
	except:
		print(
			f"Unexpected error upon {step_desc}: {str(sys.exc_info()[0])}")
		sys.exit()
	print("Download time: {:.3f} seconds.".format(time.time() - t1))
	print("Opening the previous Toakao file…")
	t2 = time.time()
	idmap = indexed_idmap_from(sorted(
		table_from_csv_path(idmap_path),
		key = lambda e: e[0]))
	save_as_json_file(idmap, this_dir + "id-map.json")
	old_toakao = object_from_json_path(toakao_path)
	print("Duration: {:.3f} seconds.".format(time.time() - t2))
	print("Now unifying the data from these different sources…")
	official_dict, muakao = reformat_official_dictionary(official_dict)
	toadua, muakao2 = reformated_toadua(toadua)
	muakao += muakao2
	new_toakao = official_dict + toadua
	clashlist = []
	new_toakao, nonlemmas = postprocessed(new_toakao, idmap)
	new_toakao, discarded = competitorless_of(new_toakao)
	#save_as_json_file(new_toakao, this_dir + "TMP.json")
	old_toakao = sorted_toakao(old_toakao)
	toakao, deleted, ignored = sync_with(old_toakao, new_toakao)
	print(f"toakao: {len(toakao)} entries.")
	print(f"muakao: {len(muakao)} entries.")
	print(f"nonlemmas: {len(nonlemmas)} entries.")
	print(f"deleted: {len(deleted)} entries.")
	print(f"discarded: {len(discarded)} entries.")
	print(f"ignored: {len(ignored)} entries.")
	# ⌵ Saving files.
	print("Saving files…")
	t3 = time.time()
	save_as_json_file(toakao, toakao_path)
	save_as_json_file(muakao, muakao_path)
	save_as_json_file(nonlemmas, nonlemmas_path)
	save_as_json_file(deleted, deleted_path)
	save_as_json_file(discarded, discarded_path)
	save_as_json_file(ignored, ignored_path)
	print("Duration: {:.3f} seconds.".format(time.time() - t3))
	print("Total execution time:     {:.3f} seconds.".format(
		time.time() - t1))
	return

def indexed_idmap_from(idmap):
	# This function sorts the idmap into submaps for each first letter of Toadua ID, for improving performances when searching a specific ID in it.
	prev_initial = ""
	initial = ""
	l = []
	indexed = dict()
	for e in idmap:
		initial = e[0][0]
		if prev_initial not in ("", initial):
			assert prev_initial not in indexed
			indexed[prev_initial] = l
			l = []
		l.append(e)
		prev_initial = initial
	if initial != "" and len(l) > 0:
		indexed[initial] = l
	return indexed

def sorted_toakao(toakao):
	return sorted(
		toakao,
		key = lambda e: e["lemma"] + "#" + e.get("discriminator", ""))

def sorted_toakao_2(toakao):
	return sorted(
		toakao,
		key = lambda e:
			(e["lemma"] + "#" + e.get("discriminator", "") + "-"
			+ all_langs_of(e)[0])
	)

def is_official_author(author):
	return author in {
		"official", "Hoemai", "solpahi", "official-examples"
	}

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
			"official", "oldofficial", "examples", "oldexamples", "oldcountries"
		} and not entry["scope"].endswith("-arch")
		and not entry["scope"].endswith("-archive")
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
		"toaq":             toaq_item,
		"discriminator":    "",
		"is_a_lemma":       is_a_lemma,
		"is_official":      is_official_author(author),
		"officialized":     False,
		"type":             pop_else("type", ""),
		"frame":            pop_else("frame", ""),
		"distribution":     pop_else("distribution", ""),
		"pronominal_class": pop_else("pronominal_class", ""),
		"subject":          pop_else("subject", ""),
		"examples":         pop_else("examples", []),
		"etymology":        [],
		"etymological_notes": "",
		"sememe":           "",
		"synonyms":         [],
		"definition_type":  definition_type,
		"translations":     [{
			"id":               id,
			"language":         language_code,
			"definition":       definition,
			"notes":            notes,
			"gloss":            pop_else("gloss", ""),
			"author":           author,
			"date":             date,
			"score":            pop_else("score", 0)
		}]
	}
	if author == "countries":
		r["discriminator"] = "1"
	return with_toadua_note_fields(r, comments)

def with_toadua_note_fields(entry, notes):
	# We will walk the notes from the most recent one to the most ancient one,
	# looking for field-value expressions such as ⟪type: illocution⟫,
	# and for each field we will at most pick a single assignment, namely
	# the most recent one.
	notes = reversed(notes)
	ks = [k for k in entry.keys() if k not in [
		"toaq", "is_official", "synonyms"]]
	for note in notes:
		for k in ks:
			t = note["content"]
			if t.startswith(k) or t.startswith(k.capitalize()):
				t = t[len(k):]
				if t.startswith(":") or t.startswith("s:"):
					entry[k] = t[t.index(":")+1:].strip()
					ks.remove(k)
					# TODO: Handle multiple notes each starting with ⟪example:⟫.
	if isinstance(entry["officialized"], str):
		entry["officialized"] = (
			entry["officialized"] in ("True", "true", "Yes", "yes"))
	if isinstance(entry["etymology"], str):
		entry["etymological_notes"] = entry["etymology"]
		entry["etymology"] = []
	return entry

# ==================================================================== #

def postprocessed(toakao, idmap):
	nonlemmas = []
	i = 0
	while i < len(toakao):
		if toakao[i]["officialized"] == True:
			toakao.pop(i)
			continue
		if not toakao[i]["is_a_lemma"]:
			nonlemmas.append(toakao.pop(i))
			continue
		for k in ["is_a_lemma", "officialized"]:
			if k in toakao[i]:
				toakao[i].pop(k)
		if not "langdata" in toakao[i]:
			toakao[i]["langdata"] = dict()
		for translation in toakao[i]["translations"]:
			lang = translation["language"]
			toakao[i][lang + "_definition"] = translation["definition"]
			toakao[i][lang + "_notes"] = translation["notes"]
			toakao[i][lang + "_gloss"] = translation["gloss"]
			toakao[i]["langdata"][lang] = {
				"id": translation["id"],
				"author": translation["author"],
				"date": translation["date"],
				"score": translation["score"]
			}
		toakao[i].pop("translations")
		toakao[i] = {
			key if key != 'toaq' else 'lemma': value
			for key, value in toakao[i].items()
		} # renaming the key ⟪toaq⟫ to ⟪lemma⟫
		if toakao[i]["discriminator"] == "":
			toakao[i]["discriminator"] = discriminator_from_tid_of(
				toakao[i], idmap)
		i += 1
	toakao = sorted_toakao_2(toakao)
	return (toakao, nonlemmas)

def discriminator_from_tid_of(entry, idmap):
	tids = all_tids_of(entry)
	for selected_id in tids:
		if selected_id[0] in idmap:
			for e in idmap[selected_id[0]]:
				if e[0] == selected_id:
					assert e[2] == entry["lemma"]
					return e[3]
	return ""

# ==================================================================== #

DATE_TEMPLATE = '%Y-%m-%dT%H:%M:%S.%fZ'

def timestamp_from_date_text(date_text):
	try:
		return datetime.strptime(date_text, DATE_TEMPLATE).timestamp()
	except:
		return 0

WINNER_SELECTION_FUNCTIONS = [
	lambda _: 1 if _.get("author", "") == "official" else 0,
#	lambda _: 1 if is_official_author(_.get("author", "")) else 0,
	lambda _: _["score"] if "score" in _ else 0,
	lambda _: -timestamp_from_date_text(_.get("date", None))
]

def wins_over(e, ε):
	for f in WINNER_SELECTION_FUNCTIONS:
		winner = the_most(e, ε, f)
		if winner == e:
			return True
		elif winner == ε:
			return False
		else:
			continue
	return False

def the_most(α, β, f):
	if f(α) > f(β):
		return α
	elif f(α) < f(β):
		return β
	else:
		return None

def competitorless_of(toakao):
	# We assume the data is already sorted according to the following hierarchy:
	#    lemma > discriminator > language
	discarded = []
	prev_item = ""
	i = 0
	while i < len(toakao):
		lang = all_langs_of(toakao[i])[0]
		item = toakao[i]["lemma"]
		item += "#" + toakao[i]["discriminator"]
		item += "-" + lang
		if i != 0 and item == prev_item:
			if wins_over(
				toakao[i]["langdata"][lang],
				toakao[i - 1]["langdata"][lang]
			):
				discarded.append(toakao[i - 1])
			else:
				discarded.append(toakao[i])
				toakao[i] = toakao[i - 1]
			toakao[i - 1] = None
		prev_item = item
		i += 1
	return [e for e in toakao if not e is None], discarded

# ==================================================================== #

DBG_LEMMAS = []

def sync_with(old, new):
	# We assume that both are already sorted alphabetically.
	added = []
	deleted = []
	ignored = []
	oi = 0
	ni = 0
	prev_oi = -1
	waitlist_lemma = ""
	waitlist = []
	oi_has_synced = False
	while oi < len(old) and ni < len(new):
		assert(len(new[ni]["langdata"]) == 1)
		if "toadua_ids" in old[oi]:
			assert not "langdata" in old[oi]
			old[oi]["langdata"] = {
				lang : {"id": tid, "author": "", "date": "", "score": ""}
				for lang, tid in old[oi]["toadua_ids"].items()
			}
			old[oi].pop("toadua_ids")
		old_lemma = old[oi]["lemma"]
		new_lemma = new[ni]["lemma"]
		od = old[oi]["discriminator"]
		nd = new[ni]["discriminator"]
		if new_lemma in DBG_LEMMAS or old_lemma in DBG_LEMMAS:
			s = "⊤" if oi_has_synced else "⊥"
			print(f"● @{oi} {old_lemma}#{od} {s} : @{ni} {new_lemma}#{nd}")
			print(f"   {all_tids_of(old[oi])} : {sole_tid_of(new[ni])}")
		if prev_oi != oi:
			oi_has_synced = False
			remaining = []
			for e in waitlist:
				tid = sole_tid_of(e)
				if tid in all_tids_of(old[oi]):
					lang = list(e["langdata"].keys())[0]
					print(f"𖣔 WL-SYNC {e['lemma']}#{od} @{lang} #{tid}")
					assert(lang in old[oi]["langdata"].keys())
					assert(lang in all_langs_of(old[oi]))
					old[oi] = sync_fields_with(old[oi], e)
					oi_has_synced = True
				else:
					remaining.append(e)
			waitlist = remaining
		prev_oi = oi
		if waitlist_lemma not in ("", old_lemma):
			# Purging the remnants of the waitlist.
			for e in waitlist:
				lang = list(e["langdata"].keys())[0]
				definition = e[lang + "_definition"]
				dis = e["discriminator"]
				print(f"⚠ IGNORING NEW COMPETITOR WITHOUT DISCRIMINATOR:")
				print(f"  {e['lemma']}#{dis} @{lang} #{list(e['langdata'].values())[0]}: ⟪{definition}⟫")
				ignored.append(e)
			waitlist = []
		waitlist_lemma = old_lemma
		if old_lemma > new_lemma:
			# ⟦new[ni]⟧ is a new lemma, absent from ⟦old⟧.
			new[ni]["discriminator"] = "1"
			is_found = False
			for i, e in enumerate(added):
				if e["lemma"] == new_lemma:
					if e["discriminator"] == "1":
						# TODO: ACCOUNT FOR SCORING!
						added[i] = sync_fields_with(e, new[ni])
						is_found = True
						break
			if not is_found:
				print(f'𖣔 N-ADD: {new[ni]["lemma"]} @{list(new[ni]["langdata"].keys())[0]}')
				added.append(new[ni])
			else:
				print(f'𖣔 N-ADD-SYNC: {new[ni]["lemma"]} @{list(new[ni]["langdata"].keys())[0]}')
			ni += 1
		elif old_lemma < new_lemma:
			if not oi_has_synced:
				# ⟦old[oi]⟧ has been deleted in ⟦new⟧, it must likewise be deleted in ⟦old⟧.
				print(f"𖣔 O-DEL {old_lemma}#{od}")
				deleted.append(old[oi])
				old[oi] = None
			oi += 1
		else: # old_lemma == new_lemma
			assert(equals(old[oi], new[ni], lambda e: e["lemma"]))
			assert(od != "")
			nid = sole_tid_of(new[ni])
			lemma = old_lemma
			lang = list(new[ni]["langdata"].keys())[0]
			definition = new[ni][lang + "_definition"].strip()
			m = re.search(r"([a-zA-Z ]+): ‘([^’;]+)’; (.+)", definition)
			if not m is None:
				#print(f"◈◆◈ DEF ⟪{m.group(3)}⟫ GLOSS ⟪{m.group(2)}⟫")
				new[ni]["type"] = m.group(1)
				new[ni][lang + "_definition"] = m.group(3)
				new[ni][lang + "_gloss"] = m.group(2)
				definition = m.group(3)
			if nd == "":
				otids = all_tids_of(old[oi])
				s = "⊤" if nid in otids else "⊥"
				#print(f"✸✸✸ {new_lemma} @{lang} #{nid} {s}: ⟪{definition}⟫")
				if nid in otids:
					if old_lemma in DBG_LEMMAS:
						print(f"𖣔 N-SYNC-∅ {old_lemma} @{lang}: ⟪{definition}⟫")
						print(f"  ➤ {new[ni]}")
					old[oi] = sync_fields_with(old[oi], new[ni])
					oi_has_synced = True
				else:
					if old_lemma in DBG_LEMMAS:
						print(f"𖣔 WL {old_lemma} @{lang} #{nid}: ⟪{definition}⟫")
						print(f"    ¬∈ {otids}")
						print(f"  ➤ {new[ni]}")
					waitlist.append(new[ni])
				ni += 1
				if ni < len(new) and new[ni]["lemma"] != old_lemma:
					oi += 1
			elif od > nd:
				print(f'⚠ NEW POLYSEME: {lemma}#{nd}')
				added.append(new[ni])
				ni += 1
			elif od < nd:
				if not oi_has_synced:
					print(f"𖣔 O-DEL₂ {old_lemma}#{od}")
					deleted.append(old[oi])
					old[oi] = None
				oi += 1
			elif od == nd:
				if old_lemma in DBG_LEMMAS:
					print(f"𖣔 N-SYNC-D {old_lemma}#{od} @{lang} #{nid}: ⟪{definition}⟫")
				if not lang in list(old[oi]["langdata"].keys()):
					# Translation in a new language.
					old[oi]["langdata"][lang] = new[ni]["langdata"][lang]
					assert(
						[lang + s in new[ni]
							for s in ("_definition", "_notes", "_gloss")])
					for s in ("_definition", "_notes", "_gloss"):
						old[oi][lang + s] = new[ni][lang + s]
				old[oi] = sync_fields_with(old[oi], new[ni])
				oi_has_synced = True
				ni += 1
				if ni < len(new) and new[ni]["lemma"] != old_lemma:
					oi += 1
	print(f"❖ ADDED ×{len(added)}: {[e['lemma'] for e in added]}")
	print(f"❖ REMOVED × {len(deleted)}: {[e['lemma'] for e in deleted]}")
	old = [e for e in old if e != None]
	old += added
	old = sorted_toakao(old)
	# CHECKING FOR DISCRIMINATOR DUPLICATION:
	prev_lemma = ""
	prev_discriminator = ""
	for e in old:
		for lang in all_langs_of(e):
			for k in [lang + suffix for suffix in ["_notes", "_gloss"]]:
				if not k in e:
					e[k] = ""
		if e["lemma"] == prev_lemma:
			if e["discriminator"] == prev_discriminator:
				print(f"🤂🤂🤂 DISCRIMINATOR-DUPLICATE: {prev_lemma}#{prev_discriminator}")
		prev_lemma = e["lemma"]
		prev_discriminator = e["discriminator"]
	return (old, deleted, ignored)

def sole_tid_of(e):
	l = all_tids_of(e)
	assert len(l) == 1
	return l[0]

def all_tids_of(e):
	return [e["langdata"][lang]["id"] for lang in e["langdata"]]

def all_langs_of(e):
	s = "_definition"
	return [k[: len(k) - len(s)] for k in e if k.endswith(s)]

IGNORED_FIELDS = (
	"langdata", "is_official", "type"
)
PROTECTED_FIELDS = (
	"lemma", "discriminator"
)

def sync_fields_with(old, new):
	for lang in new["langdata"]:
		if lang in old["langdata"]:
			old["langdata"][lang] = new["langdata"][lang]
	for k in new:
		if not k in IGNORED_FIELDS:
			if new[k] not in ("", [], dict()):
				if k in old and old[k] != new[k]:
					print(
						f"❖ {old['lemma']}#{old['discriminator']}.{k}: "
						+ f"new ⟪{new[k]}⟫ ≠ old ⟪{old[k]}⟫."
					)
				if not k in PROTECTED_FIELDS:
					old[k] = new[k]
	return old

# ==================================================================== #

### MISCELLANEOUS ROUTINES ###

def forall(property, iterable):
	return all([property(e) for e in iterable])

def equals(α, β, f):
	return f(α) == f(β)

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

