from __future__ import annotations

import configparser
import os
import pathlib
import sys
import ctypes
import threading
import time

import webview


def app_dir() -> pathlib.Path:
    if getattr(sys, "frozen", False):
        return pathlib.Path(sys.executable).resolve().parent
    return pathlib.Path(__file__).resolve().parent


def read_url() -> str:
    base = app_dir()
    ini = base / "AvaliacaoFiscal.server.ini"
    url = "http://localhost:8744"
    if ini.exists():
        parser = configparser.ConfigParser()
        text = ini.read_text(encoding="utf-8-sig")
        parser.read_string("[server]\n" + text)
        candidate = (parser.get("server", "URL", fallback="") or "").strip()
        if candidate:
            url = candidate
    return url


def message(text: str) -> None:
    try:
        ctypes.windll.user32.MessageBoxW(None, text, "Avaliação Fiscal", 0x10)
    except Exception:
        pass


class DesktopApi:
    def __init__(self):
        self.window = None

    def bind(self, window):
        self.window = window

    def close_for_update(self):
        def _close():
            time.sleep(0.15)
            try:
                if self.window is not None:
                    self.window.destroy()
            except Exception:
                pass
        threading.Thread(target=_close, daemon=True).start()
        return {"ok": True}


def main() -> int:
    try:
        url = read_url()
        api = DesktopApi()
        window = webview.create_window(
            "Avaliação Fiscal",
            url,
            width=1360,
            height=820,
            min_size=(900, 620),
            resizable=True,
            maximized=True,
            confirm_close=True,
            js_api=api,
            localization={
                "global.quitConfirmation": "Deseja realmente fechar a Avaliação Fiscal?",
                "global.quit": "Fechar",
                "global.cancel": "Não fechar",
                "global.ok": "Sim",
            },
        )
        api.bind(window)
        webview.start(debug=False)
        return 0
    except Exception as exc:
        message("Não foi possível abrir o Avaliação Fiscal.\n\n" + str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
