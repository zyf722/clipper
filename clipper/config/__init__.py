import re
from dataclasses import dataclass
from re import Pattern
from typing import List

from clipper.api.base import BaseTranslationAPI


class Regex:
    """
    A class to store regular expressions replacements.
    """

    pattern: Pattern
    """
    The regular expression pattern to match.
    """

    repl: str
    """
    The replacement string.
    """

    def __init__(self, pattern: str, repl: str):
        self.pattern = re.compile(pattern)
        self.repl = repl


@dataclass
class LanguageConfig:
    """
    Type for `language` related configuration.
    """

    original: str
    """
    The language code to translate from.
    """

    target: str
    """
    The language code to translate to.
    """


@dataclass
class ProcessorConfig:
    """
    Type for `processor` related configuration.
    """

    input_re: List[Regex]
    """
    A list of regex patterns to match and replace in the input text.
    
    The regex patterns are applied in the order they are defined in the list.
    """

    output_re: List[Regex]
    """
    A list of regular expressions to apply to the output.

    The regex patterns are applied in the order they are defined in the list.
    """


@dataclass
class Config:
    api: BaseTranslationAPI
    """
    The translation API to use.
    """

    lang: LanguageConfig
    """
    The language configuration.
    """

    processor: ProcessorConfig
    """
    The processor configuration.
    """
