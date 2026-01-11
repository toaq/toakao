
var g_lexicon = [];
//var g_selection = "All";

function is_string(v) {
    return Object.prototype.toString.call(v) === '[object String]';
}

function is_array(v) {
    return Object.prototype.toString.call(v) === '[object Array]';
}

function hget(map, field) {
	if (map === null || field === null) return "";
	if (field in map) {
		return map[field];
	} else return "";
}

function parsed_filter(filter) {
	var split_filter = filter
		.replace("\\@", "\u0091")
		.split("@")
		.map((f) => f.replace("\u0091", "@"));
	var col_filters = split_filter.slice(1);
	var map = {};
	map["lemma|eng_definition"] = split_filter[0].trim();
	col_filters.forEach((f) => {
		f = f + " ";
		var i = f.indexOf(" ");
		map[f.slice(0, i).trim()] = new RegExp(f.slice(i).trim());
	});
	return map;
}

function validated_by_filter(entry, filter) {
	var pf = parsed_filter(filter);
	var found = false;
	for (k in pf) {
		if (k === "") return;
		if (k === "any") {
			if (pf[k] === "") found = true;
			else {
				Object.keys(entry).forEach((gk) => {
					var v = hget(entry, gk);
					if (is_string(v)) {
						if (v.search(pf[k]) >= 0) {
							found = true;
						}
					} else if (is_array(v)) {
						for (e in v) {
							if (is_string(e) && e.search(pf[k]) >= 0) {
								found = true;
							}
						}
					}
				});
			}
		} else {
			searched_for = pf[k];
			k.split("|").forEach((key) => {
				if (searched_for === "") {
					if (hget(entry, key) === "")
						found = true;
				} else {
					if (hget(entry, key).search(searched_for) >= 0)
						found = true;
				}
			});
		}
		if (!found)
			return false;
		found = false;
	}
	return true;
}

function with_reformated_slots_2(definition) {		
	var s = definition.split("▯");
	if (s.length > 1) {
		s[0] += "[S]";
		if (s.length > 2) {
			if (s.length > 3) {
				s[1] += "[IO]";
				s[2] += "[DO]";
			} else {
				s[1] += "[DO]";
			}
		}
	}
	return s.join("");
}

function with_reformated_slots(definition) {
	if (!is_string(definition)) return definition;
	return definition
		.split(";")
		.map(e => {
			return with_reformated_slots_2(e);
		})
		.join(";");
}

function html_entry_for(entry, field_selection) {
	ehtml = "<summary class='entry-head'><b style='color: #002255;'>" + entry["lemma"]
		+ "<sub style='font-size: 60%; color: #225095;'>" + entry["discriminator"] + "</sub></b>";
	ehtml += " <i style='font-size: 75%;'>" + entry["type"] + "</i> — ";
	ehtml += with_reformated_slots(entry["eng_definition"]) + "</summary>";
	details = [];
	for (field in entry) {
		if (field_selection === "AllNonempty" && ["", []].includes(entry[field]))
			continue;
		if (!["lemma", "discriminator", "type", "eng_definition", "langdata"].includes(field)) {
			value = entry[field];
			if (["synonyms"].includes(field))
				value = value.join(", ");
			if (field == "sememe") {
				value = "<a href='https://ntsekees.github.io/Predilex/viewer/index.html?id=" + value + "'>" + value + "</a>";
			}
			details.push("<b>" + field + ":</b> " + value + "<br />");
		}
	}
	var n = Math.ceil(details.length / 2);
	var d1 = details.slice(0, n);
	var d2 = details.slice(n);
	ehtml += "<table class='entry-details-table'><tr>";
	ehtml += "<td class='entry-details'>" + d1.join("") + "</td>";
	ehtml += "<td class='entry-details'>" + d2.join("") + "</td>";
	ehtml += "</tr></table>";
	return "<details class='entry'>\n" + ehtml + "\n</details>\n";
}

function run() {
	var field_selection = document.getElementById("fields-selector").value;
	var filter = document.getElementById("filter-text").value;
	var html = "";
	var count = 0;
	if (filter !== "") {
		for (const entry of g_lexicon) {
			if (filter != "" && !validated_by_filter(entry, filter)) continue;
			count += 1;
			html += html_entry_for(entry, field_selection);
		}
	}
	html += "<div class='entry'></div>\n";
	document.getElementById("result-count").innerHTML = "(" + count + " results)";
	document.getElementById("results").innerHTML = html;
}

function get_url_parameters() {
	return window.location.search.substr(1).split('&').reduce(
		function (map, item) {
			var parts = item.split('=');
			map[parts[0]] = parts[1];
			return map;
		},
		{}
	);
}

function setup_2(lexicon) {
	g_lexicon = lexicon;
	var s = "";
	Object.keys(lexicon).forEach((k) => {
		if (k !== "langdata")
			s += `<option value='${k}'>${k}</option>`;
	});
	//document.getElementById("fields-selector").innerHTML += s;
	//document.addEventListener('keydown', handle_keydown, true);
	const filter_text_input = document.getElementById('filter-text');
	filter_text_input.addEventListener('keydown', (event) => {
		if (event.key === 'Enter')
			run();
	});
	params = get_url_parameters();
	filter = "";
	for (key in params) {
		if (key != "")
			filter += "@" + key + " " + params[key];
	}
	filter_text_input.value = filter;
	run();
}

function setup() {
	fetch('../toakao_extended.json')
    .then((response) => response.text())
    .then((json) => {setup_2(JSON.parse(json))});
}

setup();
 
