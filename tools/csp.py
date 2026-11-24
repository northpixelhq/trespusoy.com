"""Keep each page's Content-Security-Policy in step with its inline code.

Every page carries its policy in a <meta> tag (GitHub Pages cannot send
headers). A page's inline <script> and <style> blocks are allowed by their
SHA-256 hashes, so a change to one must change the policy too. This rewrites
the hashes in place, or with --check fails if any page is out of step.

    python3 tools/csp.py            # update
    python3 tools/csp.py --check    # verify only
"""
import base64
import hashlib
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CSP = re.compile(r'(<meta http-equiv="Content-Security-Policy" content=")([^"]*)(")')
INLINE_SCRIPT = re.compile(r"<script>(.*?)</script>", re.S)
INLINE_STYLE = re.compile(r"<style>(.*?)</style>", re.S)


def digest(code: str) -> str:
    return "'sha256-" + base64.b64encode(hashlib.sha256(code.encode()).digest()).decode() + "'"


def policy_for(html: str, old: str) -> str:
    scripts = " ".join(digest(c) for c in INLINE_SCRIPT.findall(html))
    styles = " ".join(digest(c) for c in INLINE_STYLE.findall(html))
    parts = []
    for part in [p.strip() for p in old.split(";") if p.strip()]:
        name = part.split()[0]
        if name == "script-src":
            part = "script-src 'self'" + (" " + scripts if scripts else "")
        elif name == "style-src":
            part = "style-src 'self'" + (" " + styles if styles else "")
        parts.append(part)
    return "; ".join(parts)


def main() -> int:
    check = "--check" in sys.argv
    stale = []
    for page in sorted(ROOT.rglob("*.html")):
        if "tools" in page.relative_to(ROOT).parts:
            continue
        html = page.read_text()
        match = CSP.search(html)
        if not match:
            stale.append(f"{page.relative_to(ROOT)}: no policy")
            continue
        new = policy_for(html, match.group(2))
        if new != match.group(2):
            if check:
                stale.append(f"{page.relative_to(ROOT)}: policy out of step")
            else:
                page.write_text(html[:match.start(2)] + new + html[match.end(2):])
                print(f"updated {page.relative_to(ROOT)}")
    for line in stale:
        print(line)
    return 1 if stale else 0


if __name__ == "__main__":
    sys.exit(main())
