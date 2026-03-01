import re
from pathlib import Path

broken = []
root = Path(".")
md_files = list(root.rglob("*.md"))
md_files = [
    f for f in md_files if ".git" not in str(f) and ".pytest_cache" not in str(f)
]

link_re = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")

for md_file in sorted(md_files):
    content = md_file.read_text(errors="replace")
    for match in link_re.finditer(content):
        link_text = match.group(1)
        link_target = match.group(2)

        if link_target.startswith(("http://", "https://", "mailto:", "#")):
            continue

        target_path = link_target.split("#")[0]
        if not target_path:
            continue

        resolved = (md_file.parent / target_path).resolve()

        if not resolved.exists():
            broken.append((str(md_file), link_text, link_target))

if broken:
    print(f"BROKEN LINKS ({len(broken)}):")
    for f, text, target in broken:
        print(f"  {f}: [{text}]({target})")
else:
    print(f"All relative links resolve OK (checked {len(md_files)} files)")
