"""Check the site before it is published.

    python3 tools/check.py

For every page: each local link and asset resolves to a file in this
repository, each #anchor names an element on its page, no id is used twice,
nothing is loaded from another site, the security policy's hashes match
(tools/csp.py --check), the shared header and footer are in step
(tools/sync_partials.py --check), every page has its own title, description
and share picture, and every page but the not-found page and /get/ (a redirect) is in the sitemap.
No published store screenshot may be one that shows a room code, and every
video must pass tools/video_check.py (no keyframe may redraw a still picture;
needs ffmpeg). Outside links are listed for a person to check, since
this script makes no network request.
"""
import html.parser
import pathlib
import subprocess
import sys
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://trespusoy.com"
LOADS = {("link", "href"), ("script", "src"), ("img", "src"), ("source", "src"),
         ("video", "poster"), ("use", "href")}


class Page(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids, self.dupes, self.refs = set(), [], []
        self.meta, self.title, self._in_title = {}, "", False

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            self._in_title = True
        if tag == "meta" and (a.get("name") or a.get("property")):
            self.meta[a.get("name") or a.get("property")] = a.get("content", "")
        if "id" in a:
            (self.dupes.append(a["id"]) if a["id"] in self.ids else self.ids.add(a["id"]))
        for name in ("href", "src", "poster"):
            if name in a and a[name] is not None:
                self.refs.append((tag, name, a[name]))
        if tag == "meta" and a.get("property") in ("og:image", "og:url"):
            self.refs.append((tag, "content", a.get("content", "")))

    handle_startendtag = handle_starttag


def target(page: pathlib.Path, url: str) -> pathlib.Path:
    path = urllib.parse.urlparse(url).path
    base = ROOT if path.startswith("/") else page.parent
    t = (base / path.lstrip("/")) if path else page
    return t / "index.html" if (t.is_dir() or path.endswith("/")) else t


def main() -> int:
    problems, outside = [], set()
    pages = [p for p in sorted(ROOT.rglob("*.html")) if "tools" not in p.relative_to(ROOT).parts]
    parsed = {}
    for page in pages:
        parser = Page()
        parser.feed(page.read_text())
        parsed[page] = parser
    for page, parser in parsed.items():
        rel = page.relative_to(ROOT)
        for dupe in parser.dupes:
            problems.append(f"{rel}: id used twice: {dupe}")
        for tag, attr, url in parser.refs:
            if url.startswith(("mailto:", "tel:")):
                continue
            if url.startswith(SITE):
                url = url[len(SITE):] or "/"
            elif url.startswith(("http://", "https://", "//")):
                if (tag, attr) in LOADS:
                    problems.append(f"{rel}: loads from another site: {url}")
                else:
                    outside.add(url)
                continue
            frag = urllib.parse.urlparse(url).fragment
            dest = target(page, url)
            if not dest.exists():
                problems.append(f"{rel}: {tag} {attr} -> {url}: no such file")
            elif frag and dest in parsed and frag not in parsed[dest].ids:
                problems.append(f"{rel}: {url}: no element with id {frag!r}")
    for tool in ("csp.py", "sync_partials.py"):
        run = subprocess.run([sys.executable, str(ROOT / "tools" / tool), "--check"],
                             capture_output=True, text=True)
        if run.returncode:
            problems.append(run.stdout.strip())
    # Each page its own title and description; every page in the sitemap.
    seen_titles, seen_desc = {}, {}
    sitemap = (ROOT / "sitemap.xml").read_text()
    for page, parser in parsed.items():
        rel = page.relative_to(ROOT).as_posix()
        for label, value, seen in (("title", parser.title.strip(), seen_titles),
                                   ("description", parser.meta.get("description", ""), seen_desc)):
            if not value:
                problems.append(f"{rel}: no {label}")
            elif value in seen:
                problems.append(f"{rel}: same {label} as {seen[value]}")
            seen[value] = rel
        if not parser.meta.get("og:image"):
            problems.append(f"{rel}: no share picture")
        if rel not in ("404.html", "get/index.html"):  # not-found and the redirect stay out
            url = SITE + "/" + (rel[: -len("index.html")] if rel.endswith("index.html") else rel)
            if f"<loc>{url}</loc>" not in sitemap:
                problems.append(f"{rel}: not in sitemap.xml ({url})")
    # Nothing published may render text taken from its address.
    for page in pages + [ROOT / "tools" / "share-card.html"]:
        text = page.read_text()
        for needle in ("location.search", "URLSearchParams", "location.hash"):
            if needle in text and page.relative_to(ROOT).as_posix() != "get/index.html":
                problems.append(f"{page.relative_to(ROOT)}: reads its own address ({needle})")
    # Every video must pass the keyframe-pop test (tools/video_check.py),
    # so a clip whose still picture jumps at its keyframes cannot be published.
    for clip in sorted(ROOT.rglob("*.mp4")):
        if "tools" in clip.relative_to(ROOT).parts:
            continue
        run = subprocess.run([sys.executable, str(ROOT / "tools" / "video_check.py"), str(clip)],
                             capture_output=True, text=True)
        if run.returncode:
            detail = (run.stdout.strip().splitlines() or [run.stderr.strip()])[-1]
            problems.append(f"{clip.relative_to(ROOT)}: fails the keyframe-pop test: {detail}")
    for coded in ("02-same-room-gameplay", "04-join-by-room-code", "08-find-nearby-room"):
        for found in ROOT.rglob(f"{coded}*"):
            problems.append(f"{found.relative_to(ROOT)}: this store screenshot shows a room code")
    for p in problems:
        print("PROBLEM", p)
    for url in sorted(outside):
        print("outside link (check by hand):", url)
    print(f"{len(pages)} pages, {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
