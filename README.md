# toakao

This is a project of modular Toaq dictionary, aiming to be a complement for [the official dictionary](https://github.com/toaq/dictionary/blob/master/dictionary.json) and other existing word lists (country names…) and example lists.


* `toadai.json` contains exclusively community definitions.
* `translations-of-official-definitions.csv` are community translations of official definitions.
* `toatuq.json` contains all community and official definitions, it is automatically generated with `unify.py` and should not be edited manually.

`unify.py` creates a new universal Toaq dictionary `toatuq.json` by combining the contents of `toadai.json`, [the official dictionary](https://github.com/toaq/dictionary/blob/master/dictionary.json), the [example sentence spreadsheets](https://docs.google.com/spreadsheets/d/1bCQoaX02ZyaElHiiMcKHFemO4eV1MEYmYloYZgOAhac/edit#gid=1395088029) and the [country words spreadsheet](https://docs.google.com/spreadsheets/d/1P9p1D38p364JSiNqLMGwY3zDRPQ_f6Yob_OL-uku28Q/edit#gid=637793855).

∎