from typing import Dict, Literal, Tuple

from clipper.api.baidu import BaiduTranslationAPI
from clipper.api.base import (
    BaseTranslationAPI,
    TranslationAPIWithAppID,
    TranslationAPIWithToken,
)
from clipper.api.lingocloud import LingoCloudTranslationAPI

__TRANS_API: Dict[str, BaseTranslationAPI] = {
    "baidu": BaiduTranslationAPI,
    "lingocloud": LingoCloudTranslationAPI,
}


def create_api(type: Literal["baidu", "lingocloud"], **kwargs) -> BaseTranslationAPI:
    if type not in __TRANS_API:
        raise ValueError(f"Unknown API type: {type}")

    def check_secrets(required_keys: Tuple[str, ...]):
        for key in required_keys:
            if key not in kwargs:
                raise ValueError(f"Missing required secret in `api.secrets`: {key}")

    api = __TRANS_API[type]
    if issubclass(api, TranslationAPIWithAppID):
        check_secrets(("appid", "appkey"))
    elif issubclass(api, TranslationAPIWithToken):
        check_secrets(("token",))

    return api(**kwargs)
