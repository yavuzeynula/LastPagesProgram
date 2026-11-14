"""Tek komutla guncelleme: python yayinla.py <surum>  (Windows'ta; Mac'ten: python3 ~/tools/yayin/vm.py yayinla.py <surum>)

1. local reading/kod/zincir.py'de bos hucre duzeltmesi yoksa ekler
2. app.py surumunu SURUM yapar, commit + push
3. derle.bat ile exe'yi derler
4. GitHub release acar, exe'yi yukler (git'in kayitli girisiyle; tarayici gerekmez)
"""
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

SURUM = sys.argv[1].lstrip("v") if len(sys.argv) > 1 else "0.3.2"  # python yayinla.py 0.3.3
REPO = "yavuzeynula/LastPagesProgram"
HERE = Path(__file__).resolve().parent
EXE = HERE / "dist" / "LastPagesApp.exe"
ZINCIR = HERE.parent / "local reading" / "kod" / "zincir.py"


def oku(p):
    with open(p, encoding="utf-8", newline="") as f:  # satir sonlari (CRLF) korunur
        return f.read()


def yaz(p, s):
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(s)


def git(*a):
    subprocess.run(["git", *a], cwd=HERE, check=True)


def duzelt_zincir():
    s = oku(ZINCIR)
    if "g.size == 0" in s:
        print("zincir.py: duzeltme zaten var")
        return
    nl = "\r\n" if "\r\n" in s else "\n"
    eski = "    g, (ct, cb) = cell" + nl
    if eski not in s:
        sys.exit("HATA: zincir.py beklenen yerde degil, durdum")
    yeni = eski + ("    if g.size == 0:  # hucre sayfa disina tasti: OpenCV bos goruntude hata verir" + nl
                   + "        return g, 0" + nl)
    yaz(ZINCIR, s.replace(eski, yeni, 1))
    print("zincir.py: duzeltme eklendi")


def surum_ve_push():
    app = HERE / "app.py"
    s = oku(app)
    s2 = re.sub(r'^__version__ = ".+"', f'__version__ = "{SURUM}"', s, count=1, flags=re.M)
    if s2 != s:
        yaz(app, s2)
        git("commit", "-m", f"v{SURUM}: Yerel AI bos hucrede OpenCV hatasiyla cokmez", "app.py")
    git("push")


def derle():
    # derle.bat sonda 'pause' bekler; Enter gonderiyoruz
    r = subprocess.run(["cmd", "/c", "derle.bat"], cwd=HERE, input="\n\n", text=True)
    if r.returncode != 0 or not EXE.exists():
        sys.exit("HATA: derleme basarisiz")


def token():
    out = subprocess.run(["git", "credential", "fill"], input="protocol=https\nhost=github.com\n\n",
                         capture_output=True, text=True, encoding="utf-8", check=True).stdout
    for line in out.splitlines():
        if line.startswith("password="):
            return line.split("=", 1)[1]
    sys.exit("HATA: kayitli GitHub girisi bulunamadi")


def istek(url, tok, data=None, ctype="application/json"):
    req = urllib.request.Request(url, data=data, method="POST" if data is not None else "GET", headers={
        "Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json",
        "Content-Type": ctype, "User-Agent": "yayinla"})
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def yayinla():
    tok = token()
    api = f"https://api.github.com/repos/{REPO}/releases"
    try:
        rel = istek(api, tok, json.dumps({"tag_name": f"v{SURUM}", "name": f"v{SURUM}",
                                          "target_commitish": "main"}).encode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code != 422:  # 422 = bu release zaten var
            raise
        rel = istek(f"{api}/tags/v{SURUM}", tok)
    if any(a["name"] == EXE.name for a in rel.get("assets", [])):
        print("exe zaten yuklu")
    else:
        istek(f"https://uploads.github.com/repos/{REPO}/releases/{rel['id']}/assets?name={EXE.name}",
              tok, EXE.read_bytes(), "application/octet-stream")
    print(f"\nBITTI: v{SURUM} yayinda\n{rel['html_url']}")


if __name__ == "__main__":
    duzelt_zincir()
    surum_ve_push()
    derle()
    yayinla()
