#!/usr/bin/env python3
"""Dönem/ders klasörlerini tarayıp README.md içindeki ders listesini üretir.

Kullanım (repo kökünden):
    python readme_olustur/readme_olustur.py

Beklenen yapı:  <dönem: 1-1, 1-2, ... 4-2> / <Ders Adı> / <alt klasörler> / dosyalar
Alt klasör adları serbesttir; bulunan her alt klasör tabloya sütun olarak yansır.
README.md içindeki DERSLER_BASLA / DERSLER_BITIS işaretleri arası yeniden yazılır,
geri kalan kısma dokunulmaz.
"""
import re
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
BASLA = "<!-- DERSLER_BASLA -->"
BITIS = "<!-- DERSLER_BITIS -->"
DONEM_RE = re.compile(r"^[1-4]-[12]$")
YOK_SAY = {".git", ".github", "__pycache__"}


def link(path: Path) -> str:
    return quote(path.relative_to(ROOT).as_posix())


def dosya_sayisi(klasor: Path) -> int:
    return sum(1 for p in klasor.rglob("*") if p.is_file() and p.name != ".gitkeep")


def donem_basligi(ad: str) -> str:
    sinif, yariyil = ad.split("-")
    return f"{sinif}. Sınıf {'Güz' if yariyil == '1' else 'Bahar'} ({ad})"


def donem_bolumu(donem: Path) -> list[str]:
    dersler = sorted(
        (d for d in donem.iterdir() if d.is_dir() and d.name not in YOK_SAY),
        key=lambda p: p.name.casefold(),
    )
    satirlar = [f"### {donem_basligi(donem.name)}", ""]
    if not dersler:
        return satirlar + ["_Henüz ders eklenmedi._", ""]

    sutunlar = sorted(
        {a.name for d in dersler for a in d.iterdir() if a.is_dir()},
        key=str.casefold,
    )
    satirlar.append("| " + " | ".join(["Ders"] + sutunlar) + " |")
    satirlar.append("| " + " | ".join(["---"] * (len(sutunlar) + 1)) + " |")
    for ders in dersler:
        hucreler = [f"[{ders.name}]({link(ders)})"]
        for s in sutunlar:
            alt = ders / s
            n = dosya_sayisi(alt) if alt.is_dir() else 0
            hucreler.append(f"[{n} dosya]({link(alt)})" if n else "-")
        satirlar.append("| " + " | ".join(hucreler) + " |")
    satirlar.append("")
    return satirlar


def main() -> int:
    if not README.exists():
        print("README.md bulunamadı.", file=sys.stderr)
        return 1
    metin = README.read_text(encoding="utf-8")
    if BASLA not in metin or BITIS not in metin:
        print(f"README.md içinde {BASLA} ve {BITIS} işaretleri olmalı.", file=sys.stderr)
        return 1

    donemler = sorted(p for p in ROOT.iterdir() if p.is_dir() and DONEM_RE.match(p.name))
    govde: list[str] = []
    for d in donemler:
        govde += donem_bolumu(d)

    onceki, kalan = metin.split(BASLA, 1)
    _, sonraki = kalan.split(BITIS, 1)
    yeni = f"{onceki}{BASLA}\n\n" + "\n".join(govde).rstrip() + f"\n\n{BITIS}{sonraki}"
    README.write_text(yeni, encoding="utf-8")
    print(f"{len(donemler)} dönem işlendi, README.md güncellendi.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
