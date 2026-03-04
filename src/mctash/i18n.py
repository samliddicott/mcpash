from __future__ import annotations

import gettext
import os
from functools import lru_cache
from pathlib import Path
from typing import Callable


@lru_cache(maxsize=8)
def get_translator(domain: str = "mctash", localedir: str | None = None) -> Callable[[str], str]:
    if localedir is None:
        candidate = Path(__file__).resolve().parent / "locale"
        localedir = str(candidate) if candidate.exists() else None
    language = os.environ.get("LC_ALL") or os.environ.get("LC_MESSAGES") or os.environ.get("LANG")
    languages = [language] if language else None
    try:
        tr = gettext.translation(domain, localedir=localedir, languages=languages, fallback=True)
    except Exception:
        tr = gettext.NullTranslations()
    return tr.gettext

