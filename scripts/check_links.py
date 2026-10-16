"""public/ 内の全ページについて、サイト内リンク・画像・CSS・JS の参照先が存在するかを調べる。

使い方: python3 -I scripts/check_links.py [publicディレクトリ]
外部リンク（http で始まるもの）は数えるだけで、つながるかは見ない。
"""
import os
import re
import sys
from urllib.parse import unquote, urlsplit

root = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "public")
root = os.path.abspath(root)

ATTR = re.compile(r'(?:href|src)="([^"]*)"|url\(["\']?([^"\')]+)["\']?\)')
ID = re.compile(r'\sid="([^"]+)"')

pages = {}
for dirpath, _, files in os.walk(root):
    for name in files:
        if name.endswith((".html", ".css")):
            path = os.path.join(dirpath, name)
            pages[path] = open(path, encoding="utf-8").read()


def resolve(base_file, ref):
    """参照を public/ 内のファイルパスにする。存在しなければ None。"""
    parts = urlsplit(ref)
    path = unquote(parts.path)
    if path.startswith("/"):
        target = os.path.join(root, path.lstrip("/"))
    else:
        target = os.path.normpath(os.path.join(os.path.dirname(base_file), path))
    if os.path.isdir(target) or path.endswith("/"):
        target = os.path.join(target, "index.html")
    return target if os.path.isfile(target) else None


errors, external = [], set()
for page, text in sorted(pages.items()):
    rel = os.path.relpath(page, root)
    for m in ATTR.finditer(text):
        ref = m.group(1) if m.group(1) is not None else m.group(2)
        if not ref or ref.startswith(("data:", "tel:", "mailto:", "javascript:")):
            continue
        if ref.startswith(("http://", "https://", "//")):
            external.add(ref)
            continue
        if ref.startswith("#"):
            if ref != "#" and ref[1:] not in ID.findall(text):
                errors.append(f"{rel}: ページ内リンク先がない {ref}")
            continue
        target = resolve(page, ref)
        if not target:
            errors.append(f"{rel}: 参照先がない {ref}")
            continue
        frag = urlsplit(ref).fragment
        if frag and target.endswith(".html") and frag not in ID.findall(open(target, encoding="utf-8").read()):
            errors.append(f"{rel}: リンク先にidがない {ref}")

print(f"{len(pages)} ファイルを確認")
print("外部リンク:")
for e in sorted(external):
    print("  ", e)
if errors:
    print(f"\n問題 {len(errors)} 件:")
    for e in errors:
        print("  ", e)
    sys.exit(1)
print("\n問題なし")
