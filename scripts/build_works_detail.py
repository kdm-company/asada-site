"""事例紹介の詳細ページ（/works/<id>/）を作る。

一覧（public/works/index.html）の並び順と、旧サイトの事例ページの並び順が同じことを前提にしている。
文章はナレッジベース「浅田｜営業・マーケティング」のカテゴリ別事例一覧と、旧サイトの説明だけで書く。

使い方: /usr/bin/python3 -I scripts/build_works_detail.py <旧サイト事例のJSON> <旧サイト写真のフォルダ>
"""
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.parse

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "public")
old_json, old_img_dir = sys.argv[1], sys.argv[2]

# 人物が写っている写真（載せない）
PEOPLE = {
    "2018_03_写真-251.jpg",
    "2017_05_P1000108-320x240.jpg",
    "2017_05_P1000109-320x240.jpg",
    "2017_05_b0f4176f738caf97d97d62e90d6aa48e-800x600.jpg",
    "2018_04_027-1.jpg",
}

CATS = {
    "electric": ("electrical", "Electric", "電気",
                 "浅田鉄工では、ケーブルダクト・配電ボックス・架台など、電気設備向けの製品を数多く手がけています。"),
    "architecture": ("architecture", "Architecture", "建築",
                     "建築分野では、デザイン階段や手すり、ダクトなどを手がけています。"),
    "machine": ("machine", "Machine", "機械",
                "機械分野では、タンクやコンベア、機器のカバーなどを手がけています。"),
    "transport": ("traffic", "Transport", "交通",
                  "交通分野では、高速道路や鉄道の支柱・金具などを手がけています。"),
}

TEXT = {
    "e-01": "大阪市内の浄水場の屋上に設置したケーブルダクトです。",
    "e-02": "トランス（変圧器）の架台です。お客様の立会いのもと、仮組立と寸法検査を行いました。",
    "e-03": "電気設備向けの各種ダクト、特殊BOX、金物です。",
    "e-04": "浄水場施設向けの、アルミ製の配線ダクトです。",
    "e-05": "大手化粧品メーカーの工場向けの配線ダクトです。",
    "e-06": "電気設備の配管を支える配管サポートです。",
    "e-07": "発電所・変電所施設向けのトランスカバーです。",
    "e-08": "電気設備向けの配線カバーです。",
    "e-09": "ケーブルダクトは、浅田鉄工の主要製品のひとつです。パイプ曲げ・溶接・プレス・製缶を一貫して製造し、自社塗装で短納期に対応しています。",
    "e-10": "工具を掛けて収納するための工具掛けです。",
    "a-01": "工務店様からのご依頼で製造した、階段のささら骨と手すりです。",
    "a-02": "螺旋階段を、製造から塗装まで一貫して手がけました。",
    "a-03": "オリジナルのデザインを、レーザーで加工した製品です。",
    "a-04": "大阪市内のマンションで、コインランドリー機と排気ダクトをつなぎました。",
    "a-05": "マンションの手すりの取付と、段板の設置を行いました。",
    "a-06": "ステンレス（SUS）製の納骨用の扉です。",
    "a-07": "換気扇のカバーです。",
    "m-01": "膜厚検査機械に関わるカバーフレームです。",
    "m-02": "ゴムを切断する機械（スリッダー）です。",
    "m-03": "機械分野で製造したコンベアです。",
    "m-04": "ペレットのタンクを特注で生産しました。",
    "m-05": "ペレット貯蔵タンクの蓋です。",
    "m-06": "PCB溶液の処理に使うタンクです。",
    "m-07": "下水処理場向けの配管バンドです。",
    "m-08": "下水処理場向けの配管サポートです。",
    "m-09": "セルロースファイバーの吹付けを行う機械（ブロワー）です。お客様のご要望のヒアリングから設計・製造管理・試作までを担当し、パワーと取り回しを最適化しました。",
    "m-10": "ペレット貯蔵タンクです。",
    "m-11": "配管を固定するためのサドルです。",
    "m-12": "機器を覆うカバーです。",
    "t-01": "高速道路の道路標識を支える支柱です。",
    "t-02": "高速道路の道路標識の取り付け箇所です。",
    "t-03": "新幹線・在来線の電車線に関わる製品です。",
    "t-04": "電車線の架線金具です。JR西日本・東海・四国の架線金物を手がけています。",
    "t-05": "高速道路の監視カメラを支える支柱です。",
    "t-06": "電車線に使う金具です。",
    "t-07": "大手プラントの点検用の歩廊の一部です。プラントなどの大型施設や、大規模な工場内の点検歩廊で、数多くの実績があります。",
}

ARROW = ('<span class="btn-link__icon"><img src="/assets/images/icons/arrow-right.svg" alt="" '
         'class="btn-link__icon-img btn-link__icon-img--out"><img src="/assets/images/icons/arrow-right.svg" '
         'alt="" class="btn-link__icon-img btn-link__icon-img--in"></span>')

list_path = os.path.join(ROOT, "works", "index.html")
listing = open(list_path, encoding="utf-8").read()
items = re.findall(
    r'<li class="works-cat__item" data-cat="(\w+)">(?:<a [^>]*>)?<img src="/assets/images/case-(\w-\d+)\.jpg" alt="([^"]*)">'
    r'<p class="works-cat__name">([^<]*)</p>(?:</a>)?</li>', listing)
assert len(items) == 36, len(items)

old = json.load(open(old_json, encoding="utf-8"))
by_cat = {}
for v in old.values():
    by_cat.setdefault(v["cat"], []).append(v)

template = listing
img_dir = os.path.join(ROOT, "assets", "images", "works")
os.makedirs(img_dir, exist_ok=True)


def gallery_class(n):
    """写真の枚数から、最後の段に穴が空かない並べ方を選ぶ"""
    if n == 1:
        return "works-detail__gallery--single"
    if n % 3 == 0:
        return "works-detail__gallery--col3"
    if n % 2 == 0:
        return "works-detail__gallery--col2"
    # 奇数（5・7枚）は1枚目を大きく、残りを2列か3列に
    return "works-detail__gallery--lead3" if (n - 1) % 3 == 0 else "works-detail__gallery--lead2"


report = []
seen = {}
for cat, cid, alt, name in items:
    old_cat, cat_en, cat_ja, cat_text = CATS[cat]
    i = seen.get(cat, 0)
    seen[cat] = i + 1
    src = by_cat[old_cat][i]

    photos = []
    for u in src["imgs"]:
        fname = urllib.parse.unquote(u.split("/uploads/")[-1]).replace("/", "_")
        if fname in PEOPLE:
            continue
        n = len(photos) + 1
        out = f"{cid}-{n}.jpg"
        shutil.copyfile(os.path.join(old_img_dir, fname), os.path.join(img_dir, out))
        # 大きすぎる写真は長辺1200pxに（小さい写真は拡大しない）
        subprocess.run(["sips", "-Z", "1200", "-s", "format", "jpeg", os.path.join(img_dir, out)],
                       capture_output=True, check=True)
        w = int(re.search(r"pixelWidth: (\d+)", subprocess.run(
            ["sips", "-g", "pixelWidth", os.path.join(img_dir, out)], capture_output=True, text=True).stdout).group(1))
        if w > 1200:
            subprocess.run(["sips", "--resampleWidth", "1200", os.path.join(img_dir, out)], capture_output=True, check=True)
        photos.append((out, fname))
    report.append((cid, name, [f for _, f in photos]))

    lazy = ' loading="lazy"'
    gallery = "\n".join(
        f'            <li><img src="/assets/images/works/{out}" alt="{name}"{"" if k == 0 else lazy}></li>'
        for k, (out, _) in enumerate(photos))
    main = f'''
        <section class="page-section" data-reveal>
          <h2 class="section-head">
            <span class="section-head__en">{cat_en}</span>
            <span class="section-head__ja">{cat_ja}</span>
          </h2>
          <div class="works-detail__text">
            <p>{TEXT[cid]}</p>
            <p>{cat_text}</p>
          </div>
          <ul class="works-detail__gallery {gallery_class(len(photos))}">
{gallery}
          </ul>
          <a class="btn-link works-detail__back" href="/works/"><span class="btn-link__text">事例一覧にもどる</span>{ARROW}</a>
        </section>
'''
    page = template
    page = re.sub(r"<title>[^<]*</title>", f"<title>{name} – 事例紹介 – 株式会社浅田鉄工</title>", page, count=1)
    page = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + f"{name} – 事例紹介 – 株式会社浅田鉄工", page, count=1)
    page = page.replace('<h1 class="page-head__ja">事例紹介</h1>', f'<h1 class="page-head__ja">{name}</h1>')
    page = page.replace("                <li>Works</li>",
                        f'                <li><a href="/works/">Works</a></li>\n                <li>{name}</li>')
    page = page.replace("/assets/css/works.css' media='all' />",
                        "/assets/css/works.css' media='all' />\n<link rel='stylesheet' id='asada-works-detail-css' href='/assets/css/works-detail.css' media='all' />")
    a = page.index('<div class="page-main">') + len('<div class="page-main">')
    b = page.index("</div>", page.rindex("</section>", 0, page.index('<section class="cta"')))
    page = page[:a] + "\n" + main + "\n      " + page[b:]
    out_dir = os.path.join(ROOT, "works", cid)
    os.makedirs(out_dir, exist_ok=True)
    open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8").write(page)

# 一覧の各写真から詳細ページへ
def link(m):
    cat, cid, alt, name = m.groups()
    return (f'<li class="works-cat__item" data-cat="{cat}"><a class="works-cat__link" href="/works/{cid}/">'
            f'<img src="/assets/images/case-{cid}.jpg" alt="{alt}"><p class="works-cat__name">{name}</p></a></li>')

listing = re.sub(
    r'<li class="works-cat__item" data-cat="(\w+)">(?:<a [^>]*>)?<img src="/assets/images/case-(\w-\d+)\.jpg" alt="([^"]*)">'
    r'<p class="works-cat__name">([^<]*)</p>(?:</a>)?</li>', link, listing)
open(list_path, "w", encoding="utf-8").write(listing)

json.dump(report, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "works_detail_photos.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
for cid, name, fs in report:
    print(f"/works/{cid}/ {name}: {len(fs)}枚")
