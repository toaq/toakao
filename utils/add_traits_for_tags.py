
# ============================================================ #

import sys, os, time
from collections import OrderedDict
from common import edit_json_from_path, object_from_json_path

SELF_PATH = os.path.dirname(os.path.realpath(__file__))

# ============================================================ #

def entrypoint():
	start_time = time.time()
	path = SELF_PATH + "/../toakao.json"
	edit_json_from_path(
		path, proceed, output_path = path)
	print("Execution time: {:.3f}s.".format(
		time.time() - start_time))

def proceed(toakao):
	toakao_extended = object_from_json_path(
		SELF_PATH + "/../toakao_extended.json")
	return proceed_2(toakao, toakao_extended)

TAG_TO_TRAITS = {
	"artifact": {
		"frame": "c",
		"distribution": "d",
		"pronominal_class": "maq",
		"subject": "individual"
	},
	"body_part": {
		"frame": "c",
		"distribution": "d",
		"pronominal_class": "maq",
		"subject": "individual"
	},
	"kinship": {
		"frame": "c c",
		"distribution": "d d",
		"pronominal_class": "ho",
		"subject": "individual"
	},
	"has_illness": {
		"frame": "c",
		"distribution": "d",
		"pronominal_class": "ho",
		"subject": "individual"
	},
	"food": {
		"frame": "c",
		"distribution": "d",
		"pronominal_class": "maq",
		"subject": "individual"
	},
	"geographic_feature": {
		"frame": "c",
		"distribution": "d",
		"pronominal_class": "maq",
		"subject": "individual"
	},
	"astronomy": {
		"frame": "c",
		"distribution": "d",
		"pronominal_class": "maq",
		"subject": "individual"
	},
	"profession": {
		"frame": "c",
		"distribution": "d",
		"pronominal_class": "ho",
		"subject": "individual"
	},
	"has_shape": {
		"frame": "c",
		"distribution": "d",
		"pronominal_class": "maq",
		"subject": "individual"
	},
	"ideal_shape": {
		"frame": "c",
		"distribution": "d",
		"pronominal_class": "hoq",
		"subject": "individual"
	},
	"animal": {
		"frame": "c",
		"distribution": "d",
		"pronominal_class": "ho",
		"subject": "individual"
	},
	"plant": {
		"frame": "c",
		"distribution": "d",
		"pronominal_class": "maq",
		"subject": "individual"
	},
	"celestial_body": {
		"frame": "c",
		"distribution": "d",
		"pronominal_class": "maq",
		"subject": "individual"
	},
	"country": {
		"frame": "c",
		"distribution": "d",
		"pronominal_class": "maq",
		"subject": "individual"
	},
	"geographic_entity": {
		"frame": "c",
		"distribution": "d",
		"pronominal_class": "maq",
		"subject": "individual"
	}
}

def proceed_2(toakao, toakao_extended):
	for i, e in enumerate(toakao):
		assert(i < len(toakao_extended))
		ext_e = toakao_extended[i]
		for field in ("lemma", "discriminator"):
			assert(equals(e, ext_e, lambda x: x[field]))
		if "tags" in ext_e:
			tags = ext_e["tags"].replace(",", "").split(" ")
			for tag in TAG_TO_TRAITS:
				if tag in tags:
					toakao[i] = with_traits(e, TAG_TO_TRAITS[tag])
	return toakao

def with_traits(entry, value_from_trait):
	for trait in value_from_trait.keys():
		val = value_from_trait[trait]
		if not trait in entry or entry[trait] == "":
			entry[trait] = val
		elif entry[trait] != val:
			print(
				f"⚠ ⟦{entry['lemma']}⟧.{trait}: {entry[trait]} ≠ {val}")
	return entry

def equals(α, β, P):
	return P(α) and P(β)

# ==================================================================== #

# === ENTRY POINT === #

entrypoint()

