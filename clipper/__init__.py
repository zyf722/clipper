import hashlib
import json
import random
import re
import time

import pyperclip  # type: ignore
import requests
from rich.text import Text
from rich.traceback import Traceback
from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Header, Rule, Static

DELIMITERS = ("•", "⚫", "➢")


class ClipperApp(App):
    CSS = """
    Button {
        width: 1fr;
        margin: 0 1;
    }

    .buttons {
        width: 100%;
        height: auto;
        margin: 1;
    }

    .rule {
        width: 100%;
        height: auto;
        margin: 1;
    }

    .text {
        margin: 1;
    }

    .view {
        width: 100%;
        height: auto;
        margin: 0 1;
    }

    #footer {
        background: dodgerblue;
        dock: bottom;
    }
    """

    def compose(self) -> ComposeResult:
        yield Vertical(
            Header(),
            Horizontal(
                Button("Load", id="load", variant="primary"),
                Button("Copy", id="copy", variant="primary"),
                Button("Translate", id="translate", variant="primary"),
                Button("Copy Translation", id="copy-translation", variant="primary"),
                classes="buttons",
            ),
            Horizontal(
                Button("Load & Copy", id="load-copy", variant="success"),
                Button(
                    "Load, Copy & Translate",
                    id="load-copy-translate",
                    variant="success",
                ),
                Button(
                    "Load, Translate & Copy Translation",
                    id="load-translate-copy-translation",
                    variant="success",
                ),
                classes="buttons",
            ),
            Vertical(
                VerticalScroll(Static(id="text", classes="view")),
                Rule.horizontal("double", classes="rule"),
                VerticalScroll(Static(id="translation", classes="view")),
                classes="text",
            ),
            Static(id="footer", classes="view"),
        )

    def on_mount(self) -> None:
        self.title = "Clipper"
        self.config = json.load(open("config.json"))
        self.newline_re = re.compile("(\r)*\n(?![" + "".join(DELIMITERS) + "])")
        self.translation_text = ""
        self.cliptext = ""

    @on(Button.Pressed, "#load")
    def load_clipboard(self, event: Button.Pressed) -> None:
        text: Static = self.query_one("#text")  # type: ignore
        footer: Static = self.query_one("#footer")  # type: ignore

        footer.styles.background = "dodgerblue"
        footer.update(" Processing clipboard data...")
        try:
            # Remove newlines, except for those before sepecial characters
            self.cliptext = self.newline_re.sub(" ", pyperclip.paste().strip())

            text.update(Text(self.cliptext))
            footer.update(" Clipboard data loaded")
        except Exception:
            text.update(Traceback(theme="github-dark", width=None))
            footer.styles.background = "red"
            footer.update(" Error loading clipboard data")

    @on(Button.Pressed, "#copy")
    def copy_clipboard(self, event: Button.Pressed) -> None:
        footer: Static = self.query_one("#footer")  # type: ignore

        footer.styles.background = "dodgerblue"
        footer.update(" Copying to clipboard...")
        try:
            pyperclip.copy(self.cliptext)
            footer.update(" Copied to clipboard")
        except Exception:
            footer.styles.background = "red"
            footer.update(" Error copying to clipboard")

    @on(Button.Pressed, "#copy-translation")
    def copy_translation_to_clipboard(self, event: Button.Pressed) -> None:
        footer: Static = self.query_one("#footer")  # type: ignore

        footer.styles.background = "dodgerblue"
        footer.update(" Copying to clipboard...")
        try:
            pyperclip.copy(self.translation_text)
            footer.update(" Copied to clipboard")
        except Exception:
            footer.styles.background = "red"
            footer.update(" Error copying to clipboard")

    @on(Button.Pressed, "#translate")
    def translate_text(self, event: Button.Pressed) -> None:
        translation: Static = self.query_one("#translation")  # type: ignore
        footer: Static = self.query_one("#footer")  # type: ignore

        footer.styles.background = "dodgerblue"
        footer.update(" Translating...")
        if self.cliptext == "":
            footer.styles.background = "red"
            footer.update(" No text loaded yet")
            return
        else:
            appid = self.config["appid"]
            appkey = self.config["appkey"]

            url = "https://fanyi-api.baidu.com/api/trans/vip/translate"
            session = requests.Session()
            session.trust_env = False

            # Split text into chunks of 6000 characters or until the end of a sentence
            chunks = []
            chunk = ""
            for sentence in self.cliptext.split("."):
                if len(chunk) + len(sentence) >= 6000:
                    chunks.append(chunk)
                    chunk = ""
                if chunk:
                    chunk += "."
                chunk += sentence
            if chunk:
                chunks.append(chunk)

            # Translate each chunk and append to the final result
            result = ""
            for i, chunk in enumerate(chunks):
                salt = str(random.randint(32768, 65536))
                sign_str = f"{appid}{chunk}{salt}{appkey}"
                sign = hashlib.md5(sign_str.encode()).hexdigest()

                params = {
                    "q": chunk,
                    "from": "auto",
                    "to": "zh",
                    "appid": appid,
                    "salt": salt,
                    "sign": sign,
                }
                response = session.get(url, params=params)
                try:
                    if response.status_code == 200:
                        chunk_result = response.json()
                        if "trans_result" in chunk_result:
                            chunk_translation = ""
                            for res in chunk_result["trans_result"]:
                                chunk_translation += f"{res['dst']}\n"
                            result += chunk_translation
                            if i < len(chunks) - 1 and i % 10 == 9:
                                time.sleep(0.2)
                        else:
                            footer.styles.background = "red"
                            footer.update(
                                f" Unknown error when translating: {chunk_result}"
                            )
                            return
                    else:
                        footer.styles.background = "red"
                        footer.update(
                            f" HTTP status code error: {response.status_code}"
                        )
                        return
                except Exception as e:
                    footer.styles.background = "red"
                    footer.update(f" Error translating: {e}")
                    return

            self.translation_text = result
            translation.update(Text(result))
            footer.update(" Translation complete")

    @on(Button.Pressed, "#load-copy")
    def load_copy_clipboard(self, event: Button.Pressed) -> None:
        self.load_clipboard(event)
        self.copy_clipboard(event)

    @on(Button.Pressed, "#load-copy-translate")
    def load_copy_translate_clipboard(self, event: Button.Pressed) -> None:
        self.load_clipboard(event)
        self.copy_clipboard(event)
        self.translate_text(event)

    @on(Button.Pressed, "#load-translate-copy-translation")
    def load_translate_copy_translation_clipboard(self, event: Button.Pressed) -> None:
        self.load_clipboard(event)
        self.translate_text(event)
        self.copy_translation_to_clipboard(event)
