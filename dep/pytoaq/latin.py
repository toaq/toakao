# -*- coding: utf-8 -*-

# LATIN TOAQ MODULE

# ==================================================================== #

import re, unicodedata

# ==================================================================== #

vowel_str = "aeiıouyāēīōūȳáéíóúýäëïöüÿǎěǐǒǔảẻỉỏủỷâêîôûŷàèìòùỳãẽĩõũỹ"
std_vowel_str = "aeıouyāēīōūȳáéíóúýäëïöüÿảẻỉỏủỷâêîôûŷàèìòùỳãẽĩõũỹ"
vowels = vowel_str
std_vowels = std_vowel_str
consonant_str = "'bcdfghjȷklmnprstzq"
initial_str = "'bcdfghjȷklmnprstz"
std_consonant_str = "'bcdfghjklmnprstzq"
std_initial_str = "'bcdfghjklmnprstz"
charset = vowel_str + consonant_str
std_charset = std_vowel_str + std_consonant_str

initials = ("'", "b", "c", "ch", "d", "f", "g", "h", "j", "ȷ", "k", "l", "m", "n", "p", "r", "s", "sh", "t", "z")
consonants = initials + ("q",)
std_initials = ("'", "b", "c", "ch", "d", "f", "g", "h", "j", "k", "l", "m", "n", "p", "r", "s", "sh", "t", "z")
std_consonants = std_initials + ("q",)

# ('', 'a', 'e', 'ı', 'o', 'u', 'y')
# ('', 'ā', 'ē', 'ī', 'ō', 'ū', 'ȳ')


# ==================================================================== #

quantifiers = {"sa", "sıa", "tu", "ja", "ke", "hı", "co", "baq", "hoı"}
conjunctions = {"ru", "ra", "ro", "rı", "roı"}
illocutions = {"da", "ba", "ka", "moq"}
linkers = {"fı", "go", "cu", "ta"}
sentence_prefixes = {"je", "keo", "tıu"}
prefixes = {"ku", "tou", "beı"}
terminators = {"na", "ga", "ceı"}
prenex_markers = {"bı", "pa"}
freemod_prefixes = {"ju", "la"}

toneless_particles = (
  quantifiers | {"to"} | conjunctions | illocutions | linkers
  | sentence_prefixes | prefixes | terminators | prenex_markers
  | freemod_prefixes)
# "sa", "sıa", "tu", "ja", "ke", "hı", "co", "baq", "hoı", "to", "ru", "ra", "ro", "rı", "roı", "da", "ba", "ka", "moq", "fı", "go", "cu", "ta", "je", "keo", "tıu", "ku", "tou", "beı", "bı", "pa", "ju", "la", "kıo", "kı", "teo", "hu", "na", "ga", "ceı"


particles_with_grammatical_tone = {
  "po", "jeı", "mea", "mı", "shu", "mo"
}

particles_with_lexical_tone = {
  "mả", "mâ", "tỉo", "tîo", "lủ", "lú", "lü", "lũ", "lî"
}

particle_lemmas = (
  toneless_particles | particles_with_grammatical_tone
  | particles_with_lexical_tone)

interjections = {
  'm̄', 'ḿ', 'm̈', 'm̉', 'm̂', 'm̀', 'm̃'
}

# ==================================================================== #

def is_a_word(s):
  raise NotImplementedError()

def with_carons_replaced_with_diareses(s):
  return _with_replaced_characters(s, "ǎěǐǒǔ", "äëïöü")

def _with_replaced_characters(str, src_chars, rep_chars):
  i = 0
  while i < len(str):
    if str[i] in src_chars:
      str = str[:i] + rep_chars[src_chars.index(str[i])] + str[i+1:]
    i += 1
  return str

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
  s = diacriticless_normalized(s)
  return with_macrons(s)

def normalized(s):
  # Normalizing nonstandard characters:
  s = s.strip()
  s = re.sub("[x’]", "'", s)
  s = re.sub("i", "ı", s)
  s = re.sub("ȷ", "j", s)
  s = re.sub("(?<=^)'", "", s)
  s = unicodedata.normalize("NFC", s)
  s = with_carons_replaced_with_diareses(s)
  if None == re.search(
    "[\sáéíóúýäëïöüÿảẻỉỏủỷâêîôûŷàèìòùỳãẽĩõũỹ]", s, re.IGNORECASE
  ):
    # The input is a lemma.
    s = s.lower()
    s = _with_replaced_characters(s, "āēīōūȳ", "aeıouy")
    p = ("([aeiıouyāēīōūȳ][aeiıouy]*q?['bcdfghjklmnprstz]h?[aeiouy])"
         + "(?![\u0300-\u030f])")
    s = re.sub(p, "\\1\u0304", s)
    s = unicodedata.normalize("NFC", s)
  else:
    # The input is a normal Toaq text or fragment (not a lemma form).
    s = re.sub("[\t ]+", " ", s)
    # Currently incorrect capitalization is not corrected.
    p = ( "\\b" )
    l = re.split(p, s)
    def f(w):
      p = "^(?:[" + std_initial_str + "]h?)?([" + std_vowel_str + "])"
      r = re.findall(p, w, re.IGNORECASE)
      if r != []:
        main_vowel_pos = w.index(r[0])
        bare = _with_replaced_characters(
          w,
          "āēīōūȳáéíóúýäëïöüÿảẻỉỏủỷâêîôûŷàèìòùỳãẽĩõũỹ",
          "aeıouyaeıouyaeıouyaeıouyaeıouyaeıouyaeıouy")
        if bare in toneless_particles:
          return bare
        elif bare in particles_with_grammatical_tone:
          pass
        v = w[main_vowel_pos]
        if v in "aeıouy":
          # Sparse writing: the default falling tone mark is restored.
          v = _with_replaced_characters(v, "aeıouy", "ảẻỉỏủỷ")
        w = bare[:main_vowel_pos] + v + bare[main_vowel_pos + 1:]
      return w
    i = 1
    while i < len(l):
      l[i] = f(l[i])
      i += 2
    s = "".join(l)
    # ⌵ Restoring missing macrons:
    s = with_macrons(s)
  return s

def with_macrons(s):
  p = ("([" + std_vowel_str
         + "][aeiıouy]*q?['bcdfghjklmnprstz]h?[aeiouy])"
         + "(?![\u0300-\u030f])")
  s = re.sub(p , "\\1\u0304", s)
  s = unicodedata.normalize("NFC", s)
  return s

def is_an_inflected_contentive(s):
  return None != re.match(
    ( "([bcdfghjklmnprstz]h?)?"
    + "[aeiıouyāēīōūȳáéíóúýäëïöüÿǎěǐǒǔảẻỉỏủỷâêîôûŷàèìòùỳãẽĩõũỹ]"
    + "[aeıouy]*q?((['bcdfghjklmnprstz]h?)[āēīōūȳ][aeıouy]*q?)*$" ),
    s)

def is_a_contentive_lemma(s):
  return None != re.match(
    ( "([bcdfghjklmnprstz]h?)?[aeıouy]+q?"
    + "((['bcdfghjklmnprstz]h?)[āēīōūȳ][aeıouy]*q?)*$" ),
    s)

def is_a_lemma(s):
  return (
    is_a_contentive_lemma(s) or s in (
      toneless_particles | particles_with_lexical_tone | interjections))

def __is_an_interjection(s):
  return None != re.match(
      u"[áéíóúýäëïöüÿǎěǐǒǔảẻỉỏủỷâêîôûŷàèìòùỳãẽĩõũỹ][aeiıouy]*$", s)

# ==================================================================== #

