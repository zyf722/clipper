# clipper
Clipper is a simple [TUI-based](https://github.com/Textualize/textual) Python app to extract text from clipboard and translate it, originally made for paper-reading purpose.

[Baidu Translate API](https://fanyi-api.baidu.com/) is used in the project.

![Screenshot](https://s2.loli.net/2023/11/19/oP6zq54gbtv7J9Q.png)

## Installation & Usage
This project is managed by [Poetry](https://python-poetry.org/).

To install, run the following commands after cloning the repository:

```bash
poetry lock
poetry install
cp config.example.json config.json
```

After installing dependencies, set your own APPID and APPKEY in `config.json`. 

Then, you can run the app by:

```bash
poetry run clipper
```

There are three buttons with different purposes:
- `Load`: load text from clipboard, removing all line breaks
- `Copy`: copy the processed text by `Load` to the clipboard
- `Translate`: translate the loaded text using the selected translation service

The rest two are just the (partial) combination of them.

## License
[AGPLv3](./LICENSE)