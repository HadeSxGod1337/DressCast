"""i18n: t(key, locale) from JSON dicts."""

import json
from pathlib import Path

_I18N_DIR = Path(__file__).resolve().parent
_cache: dict[str, dict] = {}


def _load(locale: str) -> dict:
    if locale not in _cache:
        p = _I18N_DIR / f"{locale}.json"
        _cache[locale] = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    return _cache[locale]


def t(key: str, locale: str = "en") -> str:
    d = _load(locale) or _load("en")
    keys = key.split(".")
    for k in keys:
        val = d.get(k)
        if val is not None and not isinstance(val, dict):
            return str(val)
        d = val if isinstance(val, dict) else {}
    return key
