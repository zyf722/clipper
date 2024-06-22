import json
import os
import re
import sys
from typing import Literal

import pyperclip  # type: ignore
from rich.text import Text
from rich.traceback import Traceback
from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Header, Rule, Static
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

from clipper.api import create_api

VERSION = "v0.3.0"


class ConfigHandler(PatternMatchingEventHandler):
    """
    A class to reload the config file when it changes.
    """

    def __init__(self, app: "ClipperApp") -> None:
        self.app = app
        super().__init__(patterns=["config.json"])

    def on_modified(self, event) -> None:
        self.app._update_footer("busy", "Reloading config file...")
        try:
            self.app._load_config()
        except Exception as e:
            self.app._update_footer("error", str(e))
            return
        self.app._update_footer("info", "Config file reloaded")


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

    FOOTER_COLORS = {
        "info": "dodgerblue",
        "error": "red",
        "busy": "gold",
    }

    def _load_config(self) -> None:
        self.config = json.load(open("config.json", "r", encoding="utf-8"))
        self.api = create_api(
            self.config["api"],
            **self.config["api.secrets"],
        )
        self.input_re = [
            (re.compile(f"({processor['regex']})"), processor["replace"])
            for processor in self.config["processor.input"]
        ]
        self.output_re = [
            (re.compile(f"({processor['regex']})"), processor["replace"])
            for processor in self.config["processor.output"]
        ]

    def compose(self) -> ComposeResult:
        yield Vertical(
            Header(),
            Horizontal(
                Button("Load", id="load", variant="primary"),
                Button("Copy", id="copy", variant="primary"),
                Button("Translate", id="translate", variant="primary"),
                Button("Copy Translation", id="copy-translation", variant="primary"),
                Button("Show Config", id="show-config"),
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
        self.title = f"Clipper {VERSION}"
        self._load_config()
        self.translation_text = ""
        self.cliptext = ""

        # Watch for changes to the config file
        self.config_observer = Observer()
        self.config_observer.schedule(ConfigHandler(self), path=".", recursive=False)
        self.config_observer.start()

        # Footer
        self.footer: Static = self.query_one("#footer")  # type: ignore
        self.text: Static = self.query_one("#text")  # type: ignore
        self.translation: Static = self.query_one("#translation")  # type: ignore

    def _update_footer(
        self, level: Literal["info", "error", "busy"], message: str
    ) -> None:
        self.footer.styles.background = self.FOOTER_COLORS[level]
        self.footer.update(f" {message}")

    @on(Button.Pressed, "#load")
    def load_clipboard(self, _: Button.Pressed) -> None:
        self._update_footer("busy", "Processing clipboard data...")
        try:
            # Remove newlines, except for those before sepecial characters
            self.cliptext = pyperclip.paste().strip()
            for regex, repl in self.input_re:
                self.cliptext = regex.sub(repl, self.cliptext)

            self.text.update(Text(self.cliptext))
            self._update_footer("info", "Clipboard data loaded")
        except Exception:
            self.text.update(Traceback(theme="github-dark", width=None))
            self._update_footer("error", "Error loading clipboard data")

    def __copy_to_clipboard(self, text: str) -> None:
        self._update_footer("busy", "Copying to clipboard...")
        try:
            pyperclip.copy(text)
            self._update_footer("info", "Copied to clipboard")
        except Exception:
            self._update_footer("error", "Error copying to clipboard")

    @on(Button.Pressed, "#copy")
    def copy_text(self, _: Button.Pressed) -> None:
        self.__copy_to_clipboard(self.cliptext)

    @on(Button.Pressed, "#copy-translation")
    def copy_translation(self, _: Button.Pressed) -> None:
        self.__copy_to_clipboard(self.translation_text)

    @on(Button.Pressed, "#translate")
    def translate_text(self, _: Button.Pressed) -> None:
        self._update_footer("busy", "Translating...")

        if self.cliptext == "":
            self._update_footer("error", "No text loaded yet")
            return
        else:
            try:
                result = self.api.translate(
                    self.cliptext,
                    self.config["api.originalLang"],
                    self.config["api.targetLang"],
                )
            except Exception as e:
                self.translation.update(Traceback(theme="github-dark", width=None))
                self._update_footer("error", str(e))
                return

            for regex, repl in self.output_re:
                result = regex.sub(repl, result)

            self.translation_text = result
            self.translation.update(Text(result))
            self._update_footer("info", "Translation complete")

    @on(Button.Pressed, "#load-copy")
    def load_copy_clipboard(self, event: Button.Pressed) -> None:
        self.load_clipboard(event)
        self.copy_text(event)

    @on(Button.Pressed, "#load-copy-translate")
    def load_copy_translate_clipboard(self, event: Button.Pressed) -> None:
        self.load_clipboard(event)
        self.copy_text(event)
        self.translate_text(event)

    @on(Button.Pressed, "#load-translate-copy-translation")
    def load_translate_copy_translation_clipboard(self, event: Button.Pressed) -> None:
        self.load_clipboard(event)
        self.translate_text(event)
        self.copy_translation(event)

    @on(Button.Pressed, "#show-config")
    def show_config(self, _: Button.Pressed) -> None:
        if sys.platform == "win32":
            os.startfile("config.json")
        else:
            import subprocess

            subprocess.call(
                (f"{'' if sys.platform == 'darwin' else 'xdg-'}open", "config.json")
            )
