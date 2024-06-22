from typing import Dict, Literal

from clipper.api.baidu import BaiduTranslationAPI
from clipper.api.base import BaseTranslationAPI
from clipper.api.lingocloud import LingoCloudTranslationAPI

__TRANS_API: Dict[str, BaseTranslationAPI] = {
    "baidu": BaiduTranslationAPI,
    "lingocloud": LingoCloudTranslationAPI,
}


def create_api(type: Literal["baidu"], *args, **kwargs) -> BaseTranslationAPI:
    if type not in __TRANS_API:
        raise ValueError(f"Unknown API type: {type}")
    return __TRANS_API[type](*args, **kwargs)
