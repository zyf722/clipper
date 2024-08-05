from clipper.api.baidu import BaiduTranslationAPI
from clipper.config import Config, LanguageConfig, ProcessorConfig, Regex

LIST_INDICATORS = "[•⚫➢]"
REGEX_ADD_SPACE_AFTER_HYPHEN = Regex(pattern="(^|\n)-(?! )", repl="\\1- ")

config = Config(
    api=BaiduTranslationAPI(appid="<your appid here>", appkey="<your appkey here>"),
    lang=LanguageConfig(
        original="auto",
        target="zh",
    ),
    processor=ProcessorConfig(
        input_re=[
            Regex(pattern=f"(\r)*\n(?!{LIST_INDICATORS})", repl=" "),
            Regex(pattern=f"(^|\n){LIST_INDICATORS}(?![A-Za-z])", repl="\\1-"),
            REGEX_ADD_SPACE_AFTER_HYPHEN,
        ],
        output_re=[
            REGEX_ADD_SPACE_AFTER_HYPHEN,
        ],
    ),
)
