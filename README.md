# clipper
Originally made for essay-reading purpose (now you can also utilize it to get texts in slides translated), clipper is a simple [TUI-based](https://github.com/Textualize/textual) Python app to extract text from clipboard and translate it using extensible translation services, with custom RegEx pre- and post-processing support.

[Baidu Translate API](https://fanyi-api.baidu.com/) is provided as a built-in translation service.

![Screenshot](./assets/image.png)

## Installation & Usage
This project is managed by [Poetry](https://python-poetry.org/).

To install, run the following commands after cloning the repository:

```bash
poetry lock
poetry install
cp config.example.json config.json
```

After installing dependencies, open `config.json` and fill in the necessary information.

The config file is validated by [json-schema](https://json-schema.org/). See [`config.schema.json`](./config.schema.json) for the schema.

Hot-reloading of the config file is supported. You can modify the config file while the app is running, and it will be automatically reloaded.

Then, you can run the app by:

```bash
poetry run clipper
```

There are four buttons with different purposes:
- `Load`: load text from clipboard, removing all line breaks
- `Copy`: copy the processed text by `Load` to the clipboard
- `Translate`: translate the loaded text using the selected translation service
- `Copy Translated`: copy the translated text to the clipboard

The rest three are just the (partial) combination of them.

### Add Custom Translation API
To add a custom translation API, you need to extend the `BaseTranslationAPI` class in [`clipper/api/base.py`](./clipper/api/base.py) and implement the `translate` method.

Then, you can add the new API to `create_api` method in [`clipper/api/__init__.py`](./clipper/api/__init__.py).

Finally, set `api` in your config file to the name of your newly-added API - make sure the name is the same as parameter `type` in `create_api`.

### RegEx Pre- and Post-Processing
Clipper supports custom RegEx pre- and post-processing. You can add your own RegEx and replacement in `processor.input` and `processor.output` in the config file.

For example, to keep list structure in PDF slides and convert it to Markdown style, you can add the following to `config.json`:

```json
"processor.input": [
    {
        "regex": "(\r)*\n(?![•⚫➢])",
        "replace": " "
    }
],
"processor.output": [
    {
        "regex": "(^|\n)[•⚫➢] ",
        "replace": "\\2- "
    }
]
```

This will replace all line breaks not followed by `•`, `⚫`, or `➢` with a space, and replace all `•`, `⚫`, or `➢` followed by a space with `- `.

## License
[AGPLv3](./LICENSE)