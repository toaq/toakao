# toakao

This is a project of modular Toaq dictionary, aiming to be a complement for [the official dictionary](https://github.com/toaq/dictionary/blob/master/dictionary.json) and other existing word lists (country names…) and example lists.


* `toadai.json` contains exclusively community definitions.
* `translations-of-official-definitions.csv` are community translations of official definitions.
* `toatuq.json` contains all community and official definitions, it is automatically generated with `unify.py` and should not be edited manually.

`unify.py` creates a new universal Toaq dictionary `toatuq.json` by combining the contents of `toadai.json`, [the official dictionary](https://github.com/toaq/dictionary/blob/master/dictionary.json), the [example sentence spreadsheets](https://docs.google.com/spreadsheets/d/1bCQoaX02ZyaElHiiMcKHFemO4eV1MEYmYloYZgOAhac/edit#gid=1395088029) and the [country words spreadsheet](https://docs.google.com/spreadsheets/d/1P9p1D38p364JSiNqLMGwY3zDRPQ_f6Yob_OL-uku28Q/edit#gid=637793855).

`archives/toadai-0.json` is the original basis for `toadai.json`and contains reformated Toadua data excluding all definitions which were automatically imported from external dictionaries (i.e. official definitions, example sentences, country words…) and with downvoted entries removed. It has been automatically generated from `archives/200708-last-toadua-dump.json` using `archives/toadua_json_to_toadai-0.py`. The Toadua data also contained comments and votes information on the aforementioned imported entries; these were removed from `archives/toadai-0.json` and were stored instead in a dedicated database `archives/feedback_on_imported_entries.json`.


# Current state of affairs

`archives/toadai-mono-0.json` is a work-in-progress database made by filtering out duplicates from `archives/toadai-0.json` data, as well as merging synonyms and definition translations into single entries.
Eventually its content will replace that of `toadai.json` and will be the basis for community editions, additions and improvements.
It is generated from `archives/toadai-0.json` with `archives/make-toadai-mono-0.py`. All the duplicate entries which were filtered out are stored in archive database, such as `archives/toadai-0-deleted-entries.json` and `archives/toadai-0-orphane-entries.json`. Toadua definitions which were competing for those of official words are stored in a dedicated database `archives/official-definition-competitors.csv`.

∎