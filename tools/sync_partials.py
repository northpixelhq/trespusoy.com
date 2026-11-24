"""Write the shared parts of the site into every page.

The header, footer, phone get-bar and the symbol sprite are written once, in
tools/partials/, and copied into each page between markers such as

    <!-- partial:header --> ... <!-- /partial:header -->

The link to the page being shown is marked aria-current="page". Run after
editing a partial; --check only reports pages that are out of step.

    python3 tools/sync_partials.py
    python3 tools/sync_partials.py --check
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PARTIALS = ROOT / "tools" / "partials"
MARK = re.compile(r"(<!-- partial:(\w+) -->\n)(.*?)(<!-- /partial:\2 -->)", re.S)


def url_of(page: pathlib.Path) -> str:
    rel = page.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return "/" + rel[: -len("index.html")]
    return ""  # e.g. 404.html: no nav link is "current"


def render(name: str, here: str) -> str:
    text = (PARTIALS / f"{name}.html").read_text()
    if here:
        text = re.sub(r'<a href="%s"' % re.escape(here), f'<a href="{here}" aria-current="page"', text)
    return text


def main() -> int:
    check = "--check" in sys.argv
    stale = []
    pages = [p for p in sorted(ROOT.rglob("*.html")) if "tools" not in p.relative_to(ROOT).parts]
    for page in pages:
        html = page.read_text()
        here = url_of(page)
        new = MARK.sub(lambda m: m.group(1) + render(m.group(2), here) + m.group(4), html)
        if new != html:
            if check:
                stale.append(str(page.relative_to(ROOT)))
            else:
                page.write_text(new)
                print("updated", page.relative_to(ROOT))
    for p in stale:
        print(f"{p}: shared parts out of step (run tools/sync_partials.py)")
    return 1 if stale else 0


if __name__ == "__main__":
    sys.exit(main())
