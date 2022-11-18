== Main Table ==
|Field|Type|Purpose|
|---|---|---|
|`predilex_id`|List of strings|Unique identifier for sememes.|
|`translations`|Set of maps|Set of definitions in different languages. The content of each definition map is described in the table `Translation table` below (see further down on this page).
|`toaq_forms`|Set of maps|Set of maps describing Toaq forms for this entry. The content of the maps is described in the table `Toaq form table` below (see further down on this page).
|`distribution`|String|Distribution signature: list of letter codes. D = distributive, C = collective.|
|`slot_tags`|Sequence of strings|Ordered list of tags or semantic fields for each argument slot.|
|`tags`|Set of strings|Semantic fields or tags for the current vocabulary item as a whole.|
|`related`|Set of IDs|Related vocabulary items; “see also”.|
|`derived`|Set of IDs|Vocabulary items derived from this one.|
|`similar`|Set of IDs|Vocabulary items with a meaning similar to this one's.|
|`antonyms`|Set of IDs|Vocabulary items with a meaning opposed to that of this one.|
|`hypernyms`|Set of IDs|Vocabulary items with a broader meaning encompassing the meaning of this item.|
|`hyponyms`|Set of IDs|Vocabulary items with a narrower meaning encompassed in the meaning of this item.|


== Translation table ==
|Field|Type|Purpose|
|---|---|---|
|`language`|String|Three letter ISO code for the language used for the definition, the glosses, the keywords and the notes.|
|`definition_type`|String|Type of the definition : `meta`, `informal`, or `formal`. Formal definitions are strictly substitutional and have full definitional force (strict semantic equivalence), e.g. ⟪we = you and me and possibly the others⟫ ; Informal definitions are also substitutional but not are not semantically strictly equivalent, and rather focus on being shorter and easier to understand than formal definitions. Meta definitions are not substitutional, but external descriptions of the meaning of the vocabulary item, e.g. ⟪’we’ is a pronoun referring to the speaker and the addressee taken together, possibly with the addition of related third parties⟫.|
|`definition`|String|Definition for the Toaq word in the target language.|
|`notes`|String|Notes on the word, its meaning or usage.|
|`keywords`|List of string|List of relevant words of the target langages which may be appropriate translations of the vocabulary item it at least some contexts or environments, or may help better finding the word when these keywords are searched for.|
|`gloss`|String|Short gloss word used for example in interlinear glosses.|
|`author`|String|(Optional) Author of the dictionary entry.|
|`date`|String|(Optional) ISO date of creation of the dictionary entry.|


== Toaq form table ==
|Field|Type|Purpose|
|---|---|---|
|`id`|String|Unique identifier.|
|`is_official`|Truth value|Whether the entry is official or not.|
|`author`|String|(Optional) Author of the dictionary entry.|
|`date`|String|(Optional) ISO date of creation of the dictionary entry.|
|`toaq`|String|Toaq item (word, collocation or sentence) being described.|
|`is_a_lemma`|Truth value|Indicates whether the Toaq item is a lemma, as opposed to a transparent composition such as a phrase, a sentence or a whole text.|
|`example_id`|String|(Optional) Example ID, such as `QUA.1` or `B0001`.|
|`audio`|Set of links|URL links to any number of audio files.|
|`class`|String|Syntactic class (e.g. DA, RU, RAI…), possibly combined with arity and signatures (POQ, CHUQ, TAO…).|
|`is_namesake`|Truth value|If true, the word is the name used to refer to its frametype.|
|`frame`|String|Signature for behavior in serial predicates ; this is NOT a type signature, so there’s no more than one subordinating slot per signature, e.g. `c 0` and not `0 0` for the predicate ⟪ca⟫.|
|`generics`|String|Generics handling signature : list of letter codes. K = kind slot, S = stage level, I = individual level.|
|`noun_classes`|String|Noun class signature : list of letter codes. A = animate, I = inanimate, P = platonic/abstract/intensional, X = any.|
|`examples`|Set of links|Any number of links to entries whose head is an example sentence illustrating the vocabulary item at hand.|
|`segmentations`|Sequence of strings|Each element of the sequence corresponds to one element in the `toaq` entry, at the same sequence index. For each element in `toaq`, a string of morphological element (affix, root…) separated by a hyphen `-` is provided. For example if `toaq` contains `[chıejīo]`, then `segmentations` will contain `["chıe-jıo"]`.
|`etymology`|Sequence of maps|Etymological information; each member of the sequence is a data structure [`language`, `item`]. Item is the original vocabulary item in the source language (provided in the native script).|
|`comments`|(Optional) Sequence of maps|Components follow the structure [`date`, `user`, `content`]. This is a list of dated comments made by Toaq users. Dates are in ISO format, UTC time.|
|`score`|Integer|(Optional) Total Toadua upvotes minus total downvotes.|



