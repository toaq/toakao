# ============================================================ #

import sys, os, time

from common import object_from_json_path, save_as_json_file
from common import table_from_csv_url

SELF_PATH = os.path.dirname(os.path.realpath(__file__))

PREDILEX_URL = "https://raw.githubusercontent.com/Ntsekees/Predilex/refs/heads/master/predilex_with_lemmas.csv"

# ============================================================ #

def entrypoint():
	start_time = time.time()
	def normalized(path):
		return path.replace("/", os.path.sep)
	toakao = object_from_json_path(
		SELF_PATH + normalized("/../toakao.json"))
	predilex = table_from_csv_url(PREDILEX_URL)
	toakao = extended_from(toakao, predilex)
	save_as_json_file(
		toakao, SELF_PATH + normalized("/../toakao_extended.json"))
	print("Execution time: {:.3f}s.".format(
		time.time() - start_time))

def extended_from(toakao, predilex):
	header = predilex[0]
	content = predilex[2:]
	keys = ("tags", "eng_lem")
	pid_i = header.index("id")
	for te in toakao:
		if te["sememe"] != "":
			for pe in content:
				if pe[pid_i] == te["sememe"]:
					for k in keys:
						pi = header.index(k)
						te[k] = pe[pi]
	return toakao

# ============================================================ #

# === ENTRY POINT === #

entrypoint()
 
