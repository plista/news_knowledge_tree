import functools
import sys
from typing import Set

import nltk
from flair.data import Sentence
from flair.models import SequenceTagger
from langdetect import detect


@functools.lru_cache(maxsize=1)
def get_tagger(language: str) -> SequenceTagger:
    """Return the tagger needed """
    if language == "de":
        return SequenceTagger.load("de-ner")
    if language == "en":
        return SequenceTagger.load("ner-fast")
    raise Exception("Invalid language")


def filter_text(text: str) -> str:
    """remove unwanted character from the text which can disturb NER"""
    filtered = text
    for s in "\\\xa0\"'[]()’“”\xad":
        filtered = filtered.replace(s, "")
    return filtered


def format_entities(entities: Set[str]) -> Set[str]:
    """
    Remove
    :param entity:
    :return:
    """
    result = []
    for entity in entities:
        if entity[-1] in [".", ",", "?", "!", ":"]:
            entity = entity[0:-1]
        entity = entity.replace("\n", " ")
        if entity[-1] == "s" and entity[:-1] in entities:
            continue
        if not entity:
            continue
        result.append(entity)
    return set(result)


@functools.lru_cache(maxsize=512)
def find_entity(text: str, language: str) -> Set[str]:
    """extract entity using flair"""
    global tagger
    filtered = filter_text(text)
    if not filtered:
        return set()
    detected_language = detect(filtered)
    if language != detected_language:
        return set()
    sent_tokens = nltk.sent_tokenize(filtered)
    sentences = [Sentence(i) for i in sent_tokens]
    tagger = get_tagger(language)
    tagger.predict(sentences)
    flair_entities = []
    for sentence in sentences:
        flair_entities.extend(
            [entity.text for entity in sentence.get_spans("ner")]
        )
    result = format_entities(set(flair_entities))
    return result


if __name__ == "__main__":
    text = sys.argv[1]
    print(find_entity(text))
