# -*- coding: utf-8 -*-

# LATIN TOAQ MODULE

# ==================================================================== #

import re, unicodedata

# ==================================================================== #

vowel_str = "aeiıouáéíóúäëïöüâêîôûạẹịı̣ọụạ́ẹ́ị́ọ́ụ́ạ̈ẹ̈ị̈ọ̈ụ̈ậệị̂ộụ̂"
std_vowel_str = "aeıouáéíóúäëïöüâêîôûạẹı̣ọụạ́ẹ́ị́ọ́ụ́ạ̈ẹ̈ị̈ọ̈ụ̈ậệị̂ộụ̂"
vowels = vowel_str
std_vowels = std_vowel_str
consonant_str = "'bcdfghjȷklmnprstzqꝡ"
initial_str = "'bcdfghjȷklmnprstzꝡ"
word_initial_str = "bcdfghjȷklmnprstzꝡ"
std_consonant_str = "'bcdfghjklmnprstzqꝡ"
std_initial_str = "'bcdfghjklmnprstzꝡ"
std_word_initial_str = "bcdfghjklmnprstzꝡ"
charset = vowel_str + consonant_str
std_charset = std_vowel_str + std_consonant_str

initials = ("m", "b", "p", "f", "n", "d", "t", "z", "c", "s", "r", "l", "nh", "j", "ȷ", "ch", "sh", "ꝡ", "g", "k", "'", "h")
finals = ("m", "q")
consonants = initials + ("q",)
std_initials = ("m", "b", "p", "f", "n", "d", "t", "z", "c", "s", "r", "l", "nh", "j", "ch", "sh", "ꝡ", "g", "k", "'", "h")
std_consonants = std_initials + ("q",)

# ==================================================================== #

root_subordinators = {"ꝡa", "ma", "tıo"}
nominal_subordinators = {"ꝡä", "mä", "tïo", "lä", "ꝡé", "ná", "é"}
adnominal_subordinators = {"ꝡë", "ë", "jü"}
injective_subordinators = {"ꝡâ", "mâ", "tîo", "lâ", "ꝡê", "nâ", "ê"}
predicatizers = {"jeı", "mea", "po"}
determiners = {
  "ló", "ké", "sá", "sía", "tú", "túq", "báq", "já", "hí", "ní", "hú"
}
injective_determiners = {
  "lô", "kê", "sâ", "sîa", "tû", "tûq", "bâq", "jâ", "hî", "nî", "hû"
}
type_1_conjunctions = {"róı", "rú", "rá", "ró", "rí", "kéo"}
type_2_conjunctions = {"roı", "ru", "ra", "ro", "rı", "keo"}
type_3_conjunctions = {"rôı", "rû", "râ", "rô", "rî", "kêo"}
conjunctions = (
  type_1_conjunctions | type_2_conjunctions | type_3_conjunctions)
falling_tone_illocutions = {"ka", "da", "ba", "nha", "doa", "ꝡo"}
peaking_tone_illocutions = {"dâ", "môq"}
raising_tone_illocutions = {"móq"}
illocutions = (
  falling_tone_illocutions | raising_tone_illocutions
  | peaking_tone_illocutions)
focus_markers = {"kú", "béı", "tó", "máo", "júaq"}
injective_focus_markers = {"kû", "bêı", "tô", "mâo", "jûaq"}
clefts = {"bï", "nä", "gö"}
vocative = {"hóı"}
terminators = {"teo", "kı"}
exophoric_pronouns = {
  "jí", "súq", "nháo", "súna", "nhána", "úmo", "íme", "súho", "áma", "há"
}
endophoric_pronouns = {
  "hóa", "hó", "máq", "tá", "hóq", "róu", "zé", "bóu", "áq", "chéq"
}
pronouns = exophoric_pronouns | endophoric_pronouns
injective_pronouns = {
   "jî", "sûq", "nhâo", "sûna", "nhâna", "ûmo", "îme", "sûho", "âma", "hâ",
   "hôa", "hô", "mâq", "tâ", "hôq", "rôu", "zê", "bôu", "âq", "chêq"
}

injectives = (
  injective_pronouns | injective_subordinators | injective_determiners
  | injective_focus_markers
)

functors_with_grammatical_tone = predicatizers | {"mı", "shu", "mo"}

functors_with_lexical_tone = (
  root_subordinators | nominal_subordinators | adnominal_subordinators
  | pronouns | determiners | conjunctions | illocutions | focus_markers
  | clefts | vocative | terminators | {"kïo"} | injectives)

functor_lemmas = (
  functors_with_grammatical_tone | functors_with_lexical_tone)

toneless_particles = (
  root_subordinators | falling_tone_illocutions | terminators)

interjections = {
  'm̄', 'ḿ', 'm̈', 'm̉', 'm̂', 'm̀', 'm̃'
}

# ==================================================================== #

def is_a_word(s):
  raise NotImplementedError()

def _with_replaced_characters(str, src_chars, rep_chars):
  i = 0
  while i < len(str):
    if str[i] in src_chars:
      str = str[:i] + rep_chars[src_chars.index(str[i])] + str[i+1:]
    i += 1
  return str

def inflected_from_lemma(lemma, tone):
  assert is_a_lemma(lemma)
  assert not lemma in functors_with_lexical_tone | interjections
  i = _first(lemma, lambda c: c in "aeıou")
  lemma = _with_replaced_interval(
    lemma, i, i + 1, inflected_vowel(lemma[i], tone))
  return lemma

def inflected_vowel(vowel, tone):
  # TODO: Under-dotted vowels
  if vowel not in "aeıouAEIOU":
    raise ValueError(f"⟦inflected_vowel⟧: Invalid vowel: ⟪{vowel}⟫")
  if tone == "":
    return vowel
  elif tone in {"´", "́"}:
    targets = "áéíóúÁÉÍÓÚ"
  elif tone in {"^", "̂"}:
    targets = "âêîôûÂÊÎÔÛ"
  elif tone in {"¨", "̈"}:
    targets = "äëïöüÄËÏÔÛ"
  else:
    raise Exception(f"⟦inflected_vowel⟧: Invalid tone: ⟪{tone}⟫")
  return _with_replaced_characters(vowel, "aeıouAEIOU", targets)

def _first(iterable, has_property):
    i = next(
      (i for i, e in enumerate(iterable) if has_property(e)),
      None)
    if i is None:
      raise ValueError
    else:
      return i

def _with_replaced_interval(s1, i, j, s2):
  assert isinstance(s1, str)
  assert isinstance(s2, str)
  assert isinstance(i, int)
  assert isinstance(j, int)
  assert i < j
  return s2.join([s1[:i], s1[j:]])


def is_an_inflected_contentive(s):
  return None != re.match(
    ( f"([{std_consonant_str}]h?)?"
    + f"[{std_vowel_str}]"
    + f"[aeıou]*[mq]?(([{std_consonant_str}]h?)[aeıouạẹı̣ọụ]+[mq]?)*$" ),
    s)

def is_a_prefix_lemma(s):
  return None != re.match(
    f"(([{std_word_initial_str}]h?)?)?[aeıou]+[mq]?-$",
    s)

def is_a_contentive_lemma(s):
  return None != re.match(
    ( f"([{std_word_initial_str}]h?)?[aeıouạẹı̣ọụ]+[mq]?"
    + f"(([{std_consonant_str}]h?)[aeıouạẹı̣ọụ]+[mq]?)*$" ),
    s)

def is_a_lemma(s):
  return (
    is_a_contentive_lemma(s) or is_a_prefix_lemma(s) or s in (
      toneless_particles | functors_with_lexical_tone | interjections))

def __is_an_interjection(s):
  return None != re.match(
      u"[áéíóúäëïöüâêîôû][aeiıou]*$", s)

# ==================================================================== #

def diacriticless_normalized(s):
  s = s.lower()
  s = re.sub("[x’]", "'", s)
  s = re.sub("(?<=^)'", "", s)
  s = unicodedata.normalize("NFD", s)
  #s = re.sub("[^0-9A-Za-zı\u0300-\u030f'_ ()«»,;.…!?]+", " ", s)
  s = re.sub("[^0-9A-Za-zı'_ ()«»,;.…!?]+", "", s)
  s = unicodedata.normalize("NFC", s)
  s = re.sub("i", "ı", s)
  s = re.sub("ȷ", "j", s)
  return s.strip()
  
def lemma_of(s):
  return diacriticless_normalized(s)

CUD = "̣" # Combining Underdot
PU1 = "\u0091"
PU2 = "\u0092"

def normalized(s, without_stripping = False):
  # TODO: Test again on example sentences. Check if the ⟦re⟧ module works instead of ⟦regex⟧.
  # TODO: Handle function words bearing prefixes.
  assert isinstance(s, str)
  if s == "":
    return s
  # Normalizing nonstandard characters:
  if not without_stripping:
    s = s.strip()
  s = _with_replaced_characters(s, "iȷwvxʼ", "ıjꝡꝡ''")
  s = _with_replaced_characters(s, "İWV", "'IꝠꝠ")
  s = re.sub("(?<=^)'", "", s)
  T = "́̈̂" # Tone marks (◌́, ◌̂, ◌̂)
  s = unicodedata.normalize("NFD", s)
  s = re.sub(f"([{CUD}])([{T}])", r"\2\1", s)
  s = s.replace(CUD, PU2)
  s = unicodedata.normalize("NFC", s)
  s = s.replace(PU2, CUD)
  if None == re.search(
    r"[\s'áéíóúäëïöüâêîôû]", s, re.IGNORECASE
  ) or s in functors_with_grammatical_tone:
    # The input is a lemma.
    s = s[0] + s[1:].lower()
    s = unicodedata.normalize("NFC", s)
  else:
    # The input is a normal Toaq text or fragment (not a lemma form).
    s = re.sub("[\t ]+", " ", s)
    # Currently incorrect capitalization is not corrected.
    chs = charset + charset.upper()
    p = ( f"([^{chs}]*)([{chs}]*)" )
    s = re.sub(p, f"\\1{PU1}\\2{PU1}", s)
    l = re.split(PU1, s)
    def f(w):
      p = "^(?:[" + std_initial_str + "]h?)?([" + std_vowel_str + "])"
      r = re.findall(p, w, re.IGNORECASE)
      if r != []:
        lower_w = w.lower().replace("i", "ı")
        bare = _with_replaced_characters(
          lower_w,
          "áéíóúäëïöüâêîôû",
          "aeıouaeıouaeıou")
        main_vowel_pos = w.index(r[0])
        main_vowel = lower_w[main_vowel_pos]
        def bare_with_vowel(vowel):
          return bare[:main_vowel_pos] + vowel + bare[main_vowel_pos + 1:]
        if (
          lower_w not in (functors_with_lexical_tone | injectives) and
          bare.lower() in toneless_particles
        ):
          return bare
        elif (
          lower_w not in functors_with_lexical_tone and (
          set() != functors_with_lexical_tone.intersection(
            {bare_with_vowel(inflected_vowel(bare[main_vowel_pos], tone))
             for tone in {"", "´", "^"}}
          )
        )):
          raise ValueError(f"Function word ⟪{w}⟫ bears a disallowed tone!")
        else:
          lower_w = bare_with_vowel(main_vowel)
          if w[0].isupper():
            w = lower_w[0].upper() + lower_w[1:]
          else:
            w = lower_w
      return w
    i = 1
    while i < len(l):
      l[i] = f(l[i])
      i += 2
    s = "".join(l)
  s = re.sub(
    f"([aeıouAEIOU][{CUD}])",
    lambda m: unicodedata.normalize("NFC", m.group(1)),
    s)
  return s

def index_of_matching_bracket(s, i, openers, closers):
  if i < 0 or i >= len(s):
    raise(ValueError(f"Index {i} not in range ⟨0, {len(s)}⟩ in ⟪{str(s)}⟫"))
  if s[i] in openers:
    step = 1
  elif s[i] in closers:
    step = -1
  else:
    return None
  c = 0
  l = len(s)
  while i in range(0, l):
    if s[i] in openers:
      c += 1
    elif s[i] in closers:
      c -= 1
    if c == 0:
      return i
    i += step
  return None

SSA = "\u0086"  # control character: Start Selected Area
ESA = "\u0087"  # control character: End Selected Area

def with_quotes_selected(text):
  text = re.sub(f"((?:M| m)[oóô])(?![{charset}])", r"\1" + SSA, text)
  return re.sub(f" (teo)(?![{charset}])", " " + ESA + r"\1", text)

def nonquote_quote_alternation(text):
  seq = re.split(f"((?:M| m)[oóô])|( teo)(?![{charset}])", text)
  i = 0
  l = len(seq)
  while i < l:
    seq[i] = "" if seq[i] is None else seq[i]
    i += 3
  return [x for x in seq if x is not None]

def toplevel_nonquote_quote_alternation(s):
  s = with_quotes_selected(s)
  l = []
  i = 0
  j = 0
  while i < len(s):
    if s[i] == SSA:
      k = index_of_matching_bracket(s, i, SSA, ESA)
      if k is None:
        k = len(s)
      l += [s[j : i], s[i + 1 : k]]
      s = s[k + 1 :]
      i = -1
    i += 1
  l += [s]
  return [x.replace(SSA, "").replace(ESA, "") for x in l]

def normalized_with_quotes_excluded(s):
  l = toplevel_nonquote_quote_alternation(s)
  for i, e in enumerate(l):
    if i % 2 == 0:
      l[i] = normalized(l[i], without_stripping = True)
  return "".join(l)

# ==================================================================== #

