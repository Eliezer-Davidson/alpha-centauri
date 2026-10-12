#!/usr/bin/env python3
"""Pre-publication check for this repository.

    python3 tools/publish_check.py            # from the repository root
    python3 tools/publish_check.py --verbose  # also list what was scanned

Exits 0 when everything passes, 1 otherwise.

WHY THE PATTERNS ARE ASSEMBLED FROM FRAGMENTS
---------------------------------------------
This file ships publicly. A checker that spells out the private names it is
looking for publishes them, which is the exact leak it exists to prevent. So
every needle below is built at runtime from pieces, and no failure message ever
prints the needle itself -- only the file, the line number, and a short label.

A SECOND TRAP THIS FILE AVOIDS
------------------------------
This codebase legitimately uses "monolith" ~25 times as a geometry term: the
spine rack and the waist rail build a monolithic reference part and assert the
split assembly is identical to it. A private-repo check that greps for that bare
word fires on correct engineering prose. Private workspaces are therefore matched
by PATH SHAPE (an absolute home path, a sibling-checkout reference) and by
assembled multi-word fragments -- never by a bare token that has an innocent
meaning here.
"""
from __future__ import annotations

import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SKIP_DIRS mirrors .gitignore. The two must be changed together: a directory
# named here is invisible to this checker, so it had better also be invisible to
# git. "output" and "assembly" are the generated-CAD directories.
SKIP_DIRS = {".git", "__pycache__", "node_modules", "output", "assembly",
             ".venv", ".cadenv", ".mypy_cache", ".pytest_cache"}
# .step/.stl/.3mf are in here because an OCCT STEP header carries a FILE_NAME
# record that can hold an author string or a path. is_text() rejects anything
# with a NUL byte in its first 8 KiB, so binary STL/3MF skip themselves and the
# ASCII ones get scanned.
TEXT_EXT = {".py", ".md", ".txt", ".json", ".yml", ".yaml", ".toml", ".cfg",
            ".sh", ".html", ".css", ".js", ".ini", ".xml",
            ".step", ".stp", ".stl", ".3mf", ".gcode", ""}

MAX_FILE_MB = 10.0


def _j(*parts: str) -> str:
    """Join fragments. Keeps the literal out of this file's own text."""
    return "".join(parts)


# ---------------------------------------------------------------- patterns
# (label, compiled regex). The label is what a failure prints; the needle is
# never printed.
def build_patterns() -> list[tuple[str, re.Pattern[str]]]:
    home = _j("/ho", "me/")
    pats: list[tuple[str, re.Pattern[str]]] = [
        # Absolute developer home paths, whoever the user is.
        # `pi/` is excluded on purpose: it is the HiWonder vendor Pi image's own
        # filesystem layout (a public, documented vendor path), not a developer
        # home. Same reasoning as the vendor-default AP address 192.168.149.1,
        # which is likewise not flagged.
        ("absolute home path",
         re.compile(re.escape(home) + r"(?!pi/)[A-Za-z0-9_.\-]+/")),
        # Site hostnames (letters + two digits, the shape the site used).
        ("site hostname", re.compile(r"\b" + _j("ar", "c") + r"0[0-9]\b")),
        ("site hostname", re.compile(r"\b" + _j("tit", "an") + r"-?5090\b", re.I)),
        ("site hostname", re.compile(r"\b" + _j("inspi", "ron") + r"-?76\d\d\b", re.I)),
        # Private sibling repositories, matched as assembled multi-part names.
        ("private workspace", re.compile(_j("gem", "ini_hi", "wonder") + r"\w*")),
        ("private workspace", re.compile(r"\b" + _j("physic", "alagent") + r"\b", re.I)),
        ("private workspace", re.compile(r"\b" + _j("mj", "lab") + r"\b")),
        ("private workspace", re.compile(r"\b" + _j("Video", "2Real") + r"\b", re.I)),
        ("private workspace", re.compile(r"\b" + _j("Robo", "JuDo") + r"\b", re.I)),
        ("private workspace", re.compile(
            r"\b" + _j("PRI", "SM") + r"[ _\-](?:" + _j("MAS", "TER") + r"|pipeline)\b", re.I)),
        ("private workspace", re.compile(r"\b" + _j("Proje", "ct-PRI", "SM") + r"\b", re.I)),
        # Note the bare word MONO+LITH is NOT matched: this codebase uses
        # "monolith(ic)" as a geometry term for a reference part.
        ("private workspace", re.compile(
            r"\b" + _j("MONO", "LITH") + r"(?:[ _\-]" + _j("ACTI", "VATE") + r"|CLE)\b")),
        # Old account handle.
        ("old account handle", re.compile(r"\b" + _j("Loop", "daed") + r"5\b", re.I)),
        # ------------------------------------------------------------------
        # Other implementations, papers and repositories. This repository
        # describes what its own code does and does not say where any idea
        # came from, in either direction; these needles catch the names and
        # phrases that would. The bare PRI+SM token is matched case-insensitively
        # because the geometry sense (a solid swept from a polygon) is written
        # "extrusion" in this codebase.
        ("other implementation", re.compile(r"\b" + _j("rest", " ?3", "d") + r"\b", re.I)),
        ("other implementation", re.compile(r"\b" + _j("PRI", "SM") + r"\b", re.I)),
        ("other implementation", re.compile(r"\b" + _j("PRI", "SM-LE", "NS") + r"\b", re.I)),
        ("paper reference", re.compile(_j("ma", " et", " al"), re.I)),
        ("paper reference", re.compile(_j("2605", r"\.", "30338"))),
        ("paper reference", re.compile(r"\b" + _j("ar", "xiv") + r"\b", re.I)),
        ("paper reference", re.compile(
            r"\bpublished (?:" + _j("met", "hod") + r"|" + _j("pap", "er") + r")\b", re.I)),
        ("other-implementation phrase", re.compile(
            r"\breference (?:" + _j("implem", "entation") + r"|run|" + _j("check", "out") + r")\b", re.I)),
        ("other-implementation phrase", re.compile(r"\bexternal " + _j("refer", "ence") + r"\b", re.I)),
        ("other-implementation phrase", re.compile(
            r"\bbehavi" + r"ou?ral " + _j("base", "line") + r"\b", re.I)),
        # The licence token in its space, hyphen and bold-split spellings.
        ("other-implementation licence", re.compile(
            _j("CC", r"[ -]BY") + r"(?:[ -]SA)?[ -]\**" + _j("N", "C") + r"\b", re.I)),
        # ------------------------------------------------------------------
        # Affiliation identifiers: a workplace, a programme, a supervisor, a
        # site. Vendor and technology names are fine; a person, an
        # organisation or a workplace is not.
        ("affiliation", re.compile(r"\b" + _j("Info", "sys") + r"\b", re.I)),
        ("affiliation", re.compile(r"\b" + _j("In", "Step") + r"\b")),
        ("affiliation", re.compile(r"\b" + _j("ARC") + r"\s+" + _j("Huma", "noid") + r"\b", re.I)),
        ("affiliation", re.compile(r"\b" + _j("Raja", "vardhan") + r"\w*", re.I)),
        ("affiliation", re.compile(r"\b" + _j("EliTh", "eIn", "tern") + r"\b", re.I)),
        ("affiliation word", re.compile(r"\b" + _j("inter", "nship") + r"s?\b", re.I)),
        ("affiliation word", re.compile(r"\b" + _j("int", "ern") + r"s?\b", re.I)),
        ("affiliation word", re.compile(r"\b" + _j("emplo", "yer") + r"s?\b", re.I)),
        ("affiliation word", re.compile(r"\b" + _j("men", "tor") + r"s?\b", re.I)),
        ("affiliation word", re.compile(r"\b" + _j("colle", "ague") + r"s?\b", re.I)),
        ("affiliation word", re.compile(r"\b" + _j("instit", "ution") + r"s?\b", re.I)),
        ("affiliation word", re.compile(r"\b" + _j("superv", "ised") + r" lab\b", re.I)),
        ("affiliation word", re.compile(
            r"\blab (?:session|workstation|network|hostname|notebook)s?\b", re.I)),
        # "the lab" as a workplace; "Isaac Lab" (the software) is allowed.
        ("affiliation word", re.compile(r"(?<!isaac )\bthe lab\b", re.I)),
        ("affiliation word", re.compile(r"\benterprise wi-?fi\b", re.I)),
        # Premises and organisations named as such; the neutral forms are
        # "the workstation", "the site network", "an open-plan room".
        ("affiliation word", re.compile(r"\bthe " + _j("off", "ice") + r"\b", re.I)),
        ("affiliation word", re.compile(r"\bthe " + _j("comp", "any") + r"\b", re.I)),
        ("affiliation word", re.compile(r"\b" + _j("progr", "amme") + r"s?\b", re.I)),
        ("affiliation word", re.compile(r"\b" + _j("bad", "ge") + r"s?\b", re.I)),
        # ------------------------------------------------------------------
        # Ownership assertions and the author's name. The licence is a plain
        # no-grant notice with no named rights-holder, and nothing in the tree
        # says whose time, equipment or hire the work was.
        ("named author", re.compile(r"\b" + _j("Eli", "ezer") + r"\b", re.I)),
        ("named author", re.compile(r"\b" + _j("David", "son") + r"\b", re.I)),
        ("named author", re.compile(r"\b" + _j("El", "i") + r"\b")),
        ("ownership assertion", re.compile(
            r"\bcopyright \(c\) \d{4}\b", re.I)),
        ("ownership assertion", re.compile(r"\bown (?:time|equipment|resources)\b", re.I)),
        ("ownership assertion", re.compile(r"\bwork (?:made )?for hire\b", re.I)),
        ("ownership assertion", re.compile(r"\bno " + _j("emplo", "yer") + r"\b", re.I)),
        ("ownership assertion", re.compile(r"\bcreated by " + _j("Eli", "ezer") + r"\b", re.I)),
        # Possessive ownership of the work itself. "the author's call" is a
        # person reference and is fine; "the author's own X" is not.
        ("ownership assertion", re.compile(r"\bauthor'?s own\b", re.I)),
        # Site networks. 192.168.149.1 is HiWonder's vendor-default AP and is fine.
        ("site network address", re.compile(r"\b100\.82\.\d{1,3}\.\d{1,3}\b")),
        ("site network address", re.compile(r"\b172\.20\.\d{1,3}\.\d{1,3}\b")),
        ("site network address", re.compile(r"\b10\.212\.\d{1,3}\.\d{1,3}\b")),
        # MAC / BLE addresses.
        ("hardware address", re.compile(r"\b(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}\b")),
        # A specific device serial, assembled rather than written: a checker
        # that spells out the serial it hunts for has published the serial.
        ("hardware serial",
         re.compile(r"\b" + _j("31B", "8BP", "5C") + r"\d{7}\b")),
        # Agent scratchpad paths: they encode a home dir and a workspace name.
        ("build-time scratchpad path",
         re.compile(r"/tmp/cla" + r"ude-\d+/[^\s\"']*")),
        # Secrets.
        ("possible secret", re.compile(
            r"(?i)\b(api[_-]?key|secret[_-]?key|access[_-]?token|bearer\s+[A-Za-z0-9._\-]{20,})\b"
            r"\s*[:=]\s*[\"']?[A-Za-z0-9._\-]{16,}")),
        ("possible secret", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
        ("possible secret", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
        ("possible secret", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ]
    return pats


FORBIDDEN_NAMES = {
    "CLAUDE.md", ".mcp.json", "HANDOFF.md", "PROMPT.md", "NEXT-SESSION.md",
    ".env",
}
FORBIDDEN_DIRS = {".claude", ".cursor", "skill-observations", ".superpowers"}
FORBIDDEN_GLOBS = [
    re.compile(r"^NEXT-SESSION.*\.md$", re.I),
    re.compile(r".*HANDOFF.*\.md$", re.I),
    re.compile(r".*-PROMPT.*\.md$", re.I),
    re.compile(r"^MORNING_REPORT.*$", re.I),
    re.compile(r"^\.env($|\..*)"),
]

# This file is allowed to describe the patterns it enforces.
SELF = os.path.join("tools", "publish_check.py")


def iter_files():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            yield os.path.join(dirpath, fn)


def rel(p: str) -> str:
    return os.path.relpath(p, ROOT)


def is_text(path: str) -> bool:
    ext = os.path.splitext(path)[1].lower()
    if ext not in TEXT_EXT:
        return False
    try:
        with open(path, "rb") as fh:
            return b"\0" not in fh.read(8192)
    except OSError:
        return False


def check_patterns(failures, verbose):
    pats = build_patterns()
    scanned = 0
    for path in iter_files():
        r = rel(path)
        if r == SELF or not is_text(path):
            continue
        scanned += 1
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                for n, line in enumerate(fh, 1):
                    for label, pat in pats:
                        if pat.search(line):
                            failures.append(f"{r}:{n}: {label}")
        except OSError as exc:
            failures.append(f"{r}: unreadable ({exc.strerror})")
    if verbose:
        print(f"  scanned {scanned} text files against {len(pats)} patterns")


def check_forbidden_files(failures):
    for path in iter_files():
        r = rel(path)
        base = os.path.basename(path)
        if base in FORBIDDEN_NAMES:
            failures.append(f"{r}: forbidden file")
            continue
        for g in FORBIDDEN_GLOBS:
            if g.match(base):
                failures.append(f"{r}: forbidden file")
                break
    for dirpath, dirnames, _ in os.walk(ROOT):
        if ".git" in dirpath.split(os.sep):
            continue
        for d in dirnames:
            if d in FORBIDDEN_DIRS:
                failures.append(f"{rel(os.path.join(dirpath, d))}/: forbidden directory")


def check_no_compiled_python(failures):
    """A .pyc embeds the absolute path of the source it was compiled from.

    .gitignore keeps them out of a push, but not out of a zip, an rsync or a
    drag-upload of this directory -- and SKIP_DIRS hides __pycache__ from every
    other stage here. So this one stage walks without the SKIP_DIRS filter.
    """
    for dirpath, dirnames, filenames in os.walk(ROOT):
        if ".git" in dirpath.split(os.sep):
            continue
        for fn in filenames:
            if fn.endswith((".pyc", ".pyo")):
                failures.append(
                    f"{rel(os.path.join(dirpath, fn))}: compiled python "
                    f"(embeds an absolute source path)")


def check_no_virtualenv(failures):
    """A previous publication attempt shipped a virtualenv. Never again."""
    for dirpath, dirnames, filenames in os.walk(ROOT):
        if ".git" in dirpath.split(os.sep):
            continue
        if "pyvenv.cfg" in filenames:
            failures.append(f"{rel(dirpath)}/pyvenv.cfg: virtualenv in the export")
        for d in dirnames:
            if d in ("site-packages", "dist-packages"):
                failures.append(f"{rel(os.path.join(dirpath, d))}/: vendored packages")


def check_sizes(failures):
    limit = MAX_FILE_MB * 1024 * 1024
    for path in iter_files():
        if ".git" in path.split(os.sep):
            continue
        try:
            size = os.path.getsize(path)
        except OSError:
            continue
        if size > limit:
            failures.append(
                f"{rel(path)}: {size / 1024 / 1024:.1f} MB > {MAX_FILE_MB} MB")


def check_required(failures):
    for f in ("LICENSE", "THIRD_PARTY_NOTICES.md", "README.md", "BUILD.md",
              "docs/EVIDENCE.md", "PROVENANCE", ".gitignore"):
        if not os.path.exists(os.path.join(ROOT, f)):
            failures.append(f"{f}: missing (required)")


LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
HTML_SRC_RE = re.compile(r"<img[^>]*\ssrc=\"([^\"]+)\"")


def check_links(failures, verbose):
    md_files = [p for p in iter_files() if p.endswith(".md")]
    checked = 0
    for path in md_files:
        base = os.path.dirname(path)
        try:
            text = open(path, encoding="utf-8").read()
        except OSError:
            continue
        targets = LINK_RE.findall(text) + HTML_SRC_RE.findall(text)
        for t in targets:
            if t.startswith(("http://", "https://", "mailto:", "#")):
                continue
            t = t.split("#")[0]
            if not t:
                continue
            checked += 1
            if not os.path.exists(os.path.normpath(os.path.join(base, t))):
                failures.append(f"{rel(path)}: broken link -> {t}")
    if verbose:
        print(f"  checked {checked} relative links in {len(md_files)} markdown files")


def check_scale_numbers(failures):
    """The README and the evidence index quote the Python line count beside the
    command that produces it. This file is counted too, so any edit here moves
    the number; re-derive it and refuse to pass a stale quote."""
    total = 0
    for path in iter_files():
        if path.endswith(".py"):
            try:
                with open(path, "rb") as fh:
                    total += sum(1 for _ in fh)
            except OSError:
                continue
    quoted = f"{total // 1000} {total % 1000:03d}" if total >= 1000 else str(total)
    for f in ("README.md", "docs/EVIDENCE.md"):
        try:
            text = open(os.path.join(ROOT, f), encoding="utf-8").read()
        except OSError:
            continue
        if quoted not in text:
            failures.append(
                f"{f}: does not quote the current Python line count "
                f"({quoted}; run the Scale command in docs/EVIDENCE.md)")


def check_readme_images(failures):
    """Every image the README inlines must resolve AND be non-trivial."""
    readme = os.path.join(ROOT, "README.md")
    text = open(readme, encoding="utf-8").read()
    imgs = [m for m in LINK_RE.findall(text) if
            m.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".svg"))]
    imgs += HTML_SRC_RE.findall(text)
    if not imgs:
        failures.append("README.md: no images")
    for t in imgs:
        p = os.path.normpath(os.path.join(ROOT, t))
        if not os.path.exists(p):
            failures.append(f"README.md: missing image {t}")
        elif os.path.getsize(p) < 2048:
            failures.append(f"README.md: suspiciously small image {t}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args()

    failures: list[str] = []
    stages = (
        ("required files", lambda: check_required(failures)),
        ("forbidden files", lambda: check_forbidden_files(failures)),
        ("no virtualenv", lambda: check_no_virtualenv(failures)),
        ("no compiled python", lambda: check_no_compiled_python(failures)),
        ("file sizes", lambda: check_sizes(failures)),
        ("privacy patterns", lambda: check_patterns(failures, args.verbose)),
        ("markdown links", lambda: check_links(failures, args.verbose)),
        ("README images", lambda: check_readme_images(failures)),
        ("scale numbers", lambda: check_scale_numbers(failures)),
    )
    for name, fn in stages:
        before = len(failures)
        fn()
        mark = "ok  " if len(failures) == before else "FAIL"
        print(f"[{mark}] {name}")

    if failures:
        print(f"\n{len(failures)} problem(s):")
        for f in failures:
            print(f"  {f}")
        return 1
    print("\nPUBLISH CHECK PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
