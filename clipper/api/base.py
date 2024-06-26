from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import ClassVar

from requests import Session


@dataclass
class BaseTranslationAPI(ABC):
    """
    Base class for translation APIs.

    To create a new translation API, subclass this class,
    overwrite the class variable `endpoint` and implement the `translate` method.
    """

    session: Session = field(default_factory=Session, init=False)
    endpoint: ClassVar[str] = ""

    def __post_init__(self):
        self.session.trust_env = False

    @abstractmethod
    def translate(self, text: str, orig: str, to: str) -> str:
        """
        Translate the given text.

        Args:
            text (str): The text to translate.
            orig (str): The original language.
            to (str): The target language.

        Returns:
            str: The translated text.
        """
        raise NotImplementedError


@dataclass
class TranslationAPIWithAppID(BaseTranslationAPI, ABC):
    """
    Base class for translation APIs that require an app ID and app key.

    To create a new translation API in this category, subclass this class,
    overwrite the class variable `endpoint` and implement the `translate` method.
    """

    appid: str
    appkey: str


@dataclass
class TranslationAPIWithToken(BaseTranslationAPI, ABC):
    """
    Base class for translation APIs that require a token.

    To create a new translation API in this category, subclass this class,
    overwrite the class variable `endpoint` and implement the `translate` method.
    """

    token: str


class TranslationError(Exception):
    """
    Class for translation errors.
    """

    pass
