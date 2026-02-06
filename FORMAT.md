
The ⟦toakao.json⟧ JSON file's structure is constituted of a list of maps (i.e. associative arrays), whose fields are described in the table below:

|Field|Type|Purpose|
|---|---|---|
|`lemma`|string|The Toaq word or affix described by the current entry.|
|`discriminator`|string|A label (typically a number, such as ⟪1⟫, ⟪2⟫…) which identifies a specific sense or homonym of the lemma form given in the `lemma` field.|
|`is_official`|boolean|Whether the lemma and its definition are official or not.|
|`type`|string|The general type of the lemma, e.g. ⟪predicate⟫, ⟪pronoun⟫, ⟪prefix⟫…|
|`frame`|string|Subtype: the serialization type of the lemma if it can take part in verb serialization; the values for this field are sequences of letters separated by whitespace, each group of letter representing one of the argument slots of the lemma, and each letter group representing a slot type, e.g. ⟪c⟫ for nonsubordinating slots, ⟪0⟫ for propositional subordination, ⟪1⟫ for property subordination… Examples of full `frame` values include `c`, `c c`, `c 0`, `c 1`, `c c 2` and so on.|
|`distribution`|string|Subtype: distributivity signature for the lemma. Its formatting is similar as that of `frame` above, but with different letter codes: `d` = distributive argument slot, `n` = non-distributive, collective slot.|
|`pronominal_class`|string|Subtype: pronoun assignment class for the lemma. This trait indicates which pronoun is bound by e.g. a quantifier phrase whose complement is the lemma of this entry. Possible values are: ⟪hoq⟫, ⟪maq⟫, ⟪ho⟫, ⟪ta⟫.|
|`subject`|string|Subtype: this trait governs the behavior of the subject verbs in certain syntactic environments, most particularly when the verb bears the adverbial peaking tone. Possible values are: ⟪free⟫, ⟪individual⟫, ⟪proposition⟫, ⟪event⟫, ⟪agent⟫, ⟪shape⟫.|
|`sememe`|string|The Predilex ID representing the meaning of the lemma.|
|`examples`|list|A list of example sentences with translations.|
|`synonyms`|list|A list of synonyms.|
|`etymology`|string|Etymological information. In the case of a simple root lemma, the etymology data has the format ⟪SOURCE_LANGUAGE_CODE, SOURCE_LEMMA⟫, where ⟪SOURCE_LANGUAGE_CODE⟫ is a 3-letter ISO code such as ⟪eng⟫ for English, and ⟪SOURCE_LEMMA⟫ is the source word in the specified source language. If the source language is Toaq, the language code may simply be omited. If the lemma is a compound or a word of a more complex internal structure, specifically a sequence of roots or affixes, then the etymologies of each element are listed, separated by a semicolon ⟪; ⟫, and each element's format is ⟪LEMMA_COMPONENT, SOURCE_LANGUAGE_CODE, SOURCE_LEMMA⟫. |
|`etymological_notes`|string|Etymological notes in English.|
|`langdata`|map|This field contains data used in the algorithm for synchronization with the Toadua collaborative dictionary. It is composed of language code keys mapped to sub-maps ⟨id, author, date, score⟩, these being 4 fields from the Toadua database.|
|`definition_type`|string|Type of the definition : `meta`, `informal`, or `formal`. Formal definitions are strictly substitutional and have full definitional force (strict semantic equivalence), e.g. ⟪we = you and me and possibly the others⟫ ; Informal definitions are also substitutional but not are not semantically strictly equivalent, and rather focus on being shorter and easier to understand than formal definitions. Meta definitions are not substitutional, but external descriptions of the meaning of the vocabulary item, e.g. ⟪’we’ is a pronoun referring to the speaker and the addressee taken together, possibly with the addition of related third parties⟫.|
|`eng_definition`|string|Definition in English.|
|`eng_notes`|string|Notes in English.|
|`eng_lem`|string|List of corresponding English lemmas, separated by semicolons.|
|`tags`|Set of strings|Semantic fields or tags for the current vocabulary item as a whole.|

Definitions, notes and lemmas in languages other than English may be present, in which case, their field names are made from the language's 3-letters ISO code followed by ⟪_definition⟫, ⟪_notes⟫, ⟪_lem⟫ etc, like for the English language fields described above.


