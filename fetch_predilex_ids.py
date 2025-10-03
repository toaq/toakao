
import sys
from routines import *
from predilex_handling import parsed_predilex_lemmas

PREDILEX_URL = "https://raw.githubusercontent.com/Ntsekees/Predilex/refs/heads/master/predilex.csv"



# ==================================================================== #

def entrypoint(this_path):
	this_dir = os.path.dirname(os.path.abspath(this_path)) + os.path.sep
	toakao_path = this_dir + "toakao.yaml"
	print("✽ Loading Predilex…")
	predilex = table_from_csv_url(PREDILEX_URL)
	print("✽ Loading Toakao…")
	toakao = object_from_yaml_path(toakao_path)
	print("✽ Fetching ID's…")
	toakao = fetch_predilex_ids(toakao, predilex)
	print("✽ Saving Toakao…")
	save_as_yaml_file(toakao, toakao_path)

def fetch_predilex_ids(toakao, full_predilex):
	header, predilex = full_predilex[0], full_predilex[2:]
	success_count = 0
	error_count = 0
	missing_count = 0
	bad_count = 0
	nonempty_entry_count = 0
	missing_list = []
	success_list = []
	for i, pe in enumerate(predilex):
		if i % 500 == 0:
			print(f"◇◆◇ {i}")
		if pe[header.index("id")] == "":
			print(f"FINISHING READING PREDILEX AT ENTRY #{i}")
			break
		s = pe[header.index("toa_lem")]
		if s != "":
			nonempty_entry_count += 1
			try:
				r = parsed_predilex_lemmas(s)
			except:
				print(f"⚠ Unable to parse ⟪{s}⟫.")
				error_count += 1
				continue
			if len(r) == 0:
				print(f"⚠ len(r) = 0 for ⟪{s}⟫")
			for lemdata in r:
				if (
					lemdata["is_certain"] and
						not lemdata["is_approximative"] and
							lemdata["arity_mismatch"] is None
				):
					is_found = False
					for te in toakao:
						if te["lemma"] == lemdata["lemma"]:
							te["sememe"] = pe[header.index("id")]
							if lemdata["slot_reordering"] != "":
								try:
									frame = frame_from(
										lemdata["slot_reordering"],
										pe[header.index("arity")])
									te["sememe"] += frame
								except:
									print(
										f"⚠ Invalid slot identifier in ⟪{lemdata['slot_reordering']}⟫")
									error_count += 1
									break
							if lemdata["syntactic_class"] != "":
								if te["type"] != "":
									te["type"] = lemdata["syntactic_class"]
							success_count += 1
							is_found = True
							break
					if not is_found:
						missing_count += 1
						missing_list.append(lemdata["lemma"])
				else:
					bad_count += 1
	print(f"✽ Error count: {error_count}")
	print(f"✽ Successfully retrieved ID's: {success_count}")
	print(f"✽ Missing count: {missing_count}")
	print(f"✽ Bad count: {bad_count}")
	print(f"✽ Nonempty entry count: {nonempty_entry_count}")
	print(f"✽ Missing list: {', '.join(missing_list)}.")
	return toakao

def frame_from(notation, valency):
	def f(c):
		if c in "123456789":
			c = int(c)
		return c
	if notation != "":
		slots = [f(c) for c in list(notation)]
	else:
		slots = []
		v = valency
		n = 1
		while v > 0:
			slots.append(n)
			n += 1
			v -= 1
	mapping = { 1 : "S", 2 : "DO", 3 : "IO", 4 : "TO", "X" : "COMPL" }
	return "[" + ",".join([mapping[e] for e in slots]) + "]"


# ==================================================================== #

# === ENTRY POINT === #

entrypoint(*sys.argv)

