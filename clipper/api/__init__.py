from typing import Literal

from clipper.api.baidu import BaiduTranslationAPI, BaseTranslationAPI


def create_api(type: Literal["baidu"], appid: str, appkey: str) -> BaseTranslationAPI:
    if type == "baidu":
        return BaiduTranslationAPI(appid, appkey)
    else:
        raise ValueError(f"Unknown API type: {type}")
