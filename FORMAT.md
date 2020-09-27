|Field|Type|Purpose|
|---|---|---|
|`id`|String|Unique identifier.|
|`date`|String|ISO date of creation of the dictionary entry.|
|`author`|String|Author of the dictionary entry.|
|`toaq`|String|Toaq item being described.|
|`is_a_lexeme`|Truth value|Indicates whether the Toaq item is a lexeme, as opposed to a transparent composition such as a phrase, a sentence or a whole text.|
|`example_id`|String|Example ID, such as "QUA.1" or "B0001".|
|`audio`|Set of links|URL links to any number of audio files.|
|`class`|String|Syntactic class (e.g. DA, RU, RAI…), possibly combined with arity and signatures (POQ, CHUQ, TAO…).|
|`namesake`|Truth value|If true, the word is the name used to refer to its frametype.|
|`frame`|String|Signature for behavior in serial predicates ; this is NOT a type signature, so there’s no more than one subordinating slot per signature, e.g. ``c 0`` and not ``0 0`` for the predicate «ca».|
|`distribution`|String|Distribution signature : list of letter codes. D = distributive, C = collective.|
|`generics`|String|Generics handling signature : list of letter codes. K = kind slot, S = stage level, I = individual level.|
|`noun_classes`|String|Noun class signature : list of letter codes. A = animate, I = inanimate, P = platonic/abstract/intensional, X = any.|
|`slot_tags`|Sequence of strings|Ordered list of tags or semantic fields for each argument slot.|
|`tags`|Set of strings|Semantic fields or tags for the current vocabulary item as a whole.|
|`examples`|Set of links|Any number of links to entries whose head is an example sentence illustrating the vocabulary item at hand.|
|`target_language`|String|Three letter ISO code for the language used for the definition, the glosses, the keywords and the notes.|
|`definition_type`|String|Type of the definition : `meta`, `informal`, or `formal`. Formal definitions are strictly substitutional and have full definitional force (strict semantic equivalence), e.g. « we = you and me and possibly the others » ; Informal definitions are also substitutional but not are not semantically strictly equivalent, and rather focus on being shorter and easier to understand than formal definitions. Meta definitions are not substitutional, but external descriptions of the meaning of the vocabulary item, e.g. «’we’ is a pronoun referring to the speaker and the addressee taken together, possibly with the addition of related third parties».|
|`definition`|String|Definition for the Toaq word in the target language.|
|`notes`|String|Notes on the word, its meaning or usage.|
|`gloss`|String|Short gloss word used for example in interlinear glosses.
|`keywords`|String|List of relevant words of the target langages which may be appropriate translations of the vocabulary item it at least some contexts or environments, or may help better finding the word when these keywords are searched for.|
|`segmentation`|String|Segmentation of the compound vocabulary item into their etymological components, e.g. ``muıdūa`` → ``muı-dua``.|
|`etymology`|Sequence of associative arrays|For each etymological component of the vocabulary item at hand, a data structure [`language`, `item`] is provided. Item is the original vocabulary item in the source language (provided in the native script).|
|`related`|Set of links|Related vocabulary items; "see also".|
|`derived`|Set of links|Vocabulary items derived from this one.|
|`synonyms`|Set of links|Vocabulary items with the exact same meaning as this one.|
|`antonyms`|Set of links|Vocabulary items with a meaning opposed to that of this one.|
|`hypernyms`|Set of links|Vocabulary items with a broader meaning encompassing the meaning of this item.|
|`hyponyms`|Set of links|Vocabulary items with a narrower meaning encompassed in the meaning of this item.|
|`comments`|Sequence of associative arrays|Components follow the structure [`date`, `user`, `content`]. This is a list of dated comments made by Toaq users.|
|`score`|Integer|Total upvotes minus total downvotes.|
|`votes`|Sequence of associative arrays|Components follow the structure [`user`, `vote`]. List of votes on the dictionary entry. Should be hidden from public view.|


