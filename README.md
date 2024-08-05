# clipper
Originally made for essay-reading purpose (now you can also utilize it to get texts in slides translated), clipper is a simple [TUI-based](https://github.com/Textualize/textual) Python app to extract text from clipboard and translate it using extensible translation services, with custom RegEx pre- and post-processing support.

![Screenshot](./assets/image.png)

## Installation & Usage
This project is managed by [Poetry](https://python-poetry.org/).

To install, run the following commands after cloning the repository:

```bash
poetry lock
poetry install
cp userconfig.example.py userconfig.py
```

After installing dependencies, open `userconfig.py` and create your own `config` object based on the example in the file. Check [`clipper.config`](./clipper/config/__init__.py) for full configuration options.

> [!CAUTION]
> Clipper won't check whether the config file is valid or contains malicious code.
>
> Please be cautious when running the app with a custom config file.

Hot-reloading of the config file is supported. You can modify the config file while the app is running, and it will be automatically reloaded.

Then, you can run the app by:

```bash
poetry run clipper
```

There are four blue buttons representing main functions of the app:
- `Load`: load text from clipboard, removing all line breaks
- `Copy`: copy the processed text by `Load` to the clipboard
- `Translate`: translate the loaded text using the selected translation service
- `Copy Translation`: copy the translated text to the clipboard

There are also three green buttons, which are just shortcuts to some combinations of the blue buttons:
- `Load & Copy`
- `Load, Copy & Translate`
- `Load, Translate & Copy Translation`

Apart from above, there is a gray button to focus `userconfig.py` in your file explorer in case you want to open it with a text editor and modify it.

### Translation API
#### Built-in APIs
| Class | Provider | Type | Docs | Note |
| :-: | :------: | :--: | :--: | :---: |
| [`BaiduTranslationAPI`](./clipper/api/baidu.py) | Baidu General Translate API | `TranslationAPIWithAppID` | [Link](https://fanyi-api.baidu.com/doc/21) (Simplified Chinese) | - |
| [`LingoCloudTranslationAPI`](./clipper/api/lingocloud.py) | LingoCloud Translate API | `TranslationAPIWithToken` | [Link](https://docs.caiyunapp.com/lingocloud-api/) (Simplified Chinese) | - |

Set `api` in your config object using the class of the translation API you want to use, along with corresponding secrets based on its type to initialize it.

Continue reading to gain more information on API types and how to add custom APIs.

#### Add Custom API
To add a custom translation API, you need to extend the [`BaseTranslationAPI`](./clipper/api/base.py#L9) class (or [`TranslationAPIWithAppID`](./clipper/api/base.py#L40) / [`TranslationAPIWithToken`](./clipper/api/base.py#L53) if secrets are required) and implement the `translate` method.

Then, import your API class and set `api` property in the config object using your API class and secrets (if required). Everything should work after hot-reloading.

### RegEx Pre- and Post-Processing
Clipper supports custom RegEx pre- and post-processing. You can add your own RegEx and replacement in `processor.input_re` and `processor.output_re` in the config object.

For example, to keep list structure in PDF slides and convert it to Markdown style, you can add the following to `userconfig.py`:

```py
from clipper.config import Config, ProcessorConfig, Regex

config = Config(
    # Other properties are omitted ...
    processor=ProcessorConfig(
        input_re=[
            Regex(pattern="(\r)*\n(?![•⚫➢])", repl=" "),
        ],
        output_re=[
            Regex(pattern="(^|\n)[•⚫➢] ", repl="\\1- "),
        ],
    ),
    # ...
)
```

This will replace all line breaks not followed by `•`, `⚫`, or `➢` with a space in the input, and replace all `•`, `⚫`, or `➢` followed by a space with `- ` in the output.

## License
[AGPLv3](./LICENSE)
