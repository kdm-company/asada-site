"""設備紹介のカード（9台）と、設備ごとの詳細ページ（/facility/<slug>/）を作る。

設備はナレッジベース「浅田｜技術力・設備」にあり、写真が旧サイトかテスト版にあるものだけ。
旧式の設備（旧レーザー加工機・ストッカー・ユニットワーカー）は載せない。

使い方: /usr/bin/python3 -I scripts/build_facility_detail.py <旧サイト写真のフォルダ>
"""
import os
import re
import shutil
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "public")
old_img_dir = sys.argv[1]
img_dir = os.path.join(ROOT, "assets", "images", "facility")
os.makedirs(img_dir, exist_ok=True)

ARROW = ('<span class="btn-link__icon"><img src="/assets/images/icons/arrow-right.svg" alt="" '
         'class="btn-link__icon-img btn-link__icon-img--out"><img src="/assets/images/icons/arrow-right.svg" '
         'alt="" class="btn-link__icon-img btn-link__icon-img--in"></span>')

# slug, 名前, 分野(英・日), カードの写真, カードの仕様, カードの説明,
# 詳細の写真（/assets/images/ からのパスと説明）, 詳細の仕様, 詳細の本文, 補足写真（旧サイトのファイル名, 説明）
EQUIP = [
    dict(slug="fiber-laser", name="ファイバーレーザマシン", cat=("Cutting", "切断設備"),
         card_img="photo-set-laser-product.jpg", card_alt="レーザー加工品の例",
         card_specs=[("メーカー", "AMADA"), ("最大板厚", "鋼板（SS400）25mm／SUS 12mm")],
         card_desc="パレットチェンジャーで定尺板2枚の同時加工が可能です。（写真はレーザー加工品の例）",
         main=("photo-laser-02.jpg", "レーザー加工品の例（オリジナルデザイン）"),
         specs=[("メーカー", "AMADA"), ("台数", "1台"), ("最大板厚", "鋼板（SS400）最大25mm／SUS（ステンレス）最大12mm"),
                ("導入", "2023年末（既存のレーザー加工機から更新）")],
         body=["レーザーの光で金属の板を切る機械です。図面どおりの形を、高い精度で切り抜くことができます。",
               "鋼板（SS400）は最大板厚25mm、SUSは12mmまで切断できます。パレットチェンジャーで定尺板2枚を同時に加工できるため、数の多いご注文ではコストの低減につながります。",
               "CADMACによる3D設計と組み合わせ、パイプのカットやY管・K管など複雑な形状の加工にも対応しています。",
               "※写真は、レーザーで加工した製品の例です。"],
         gallery=[("2018_04_328.jpg", "レーザー加工品の例"), ("2018_04_331.jpg", "レーザー加工品の例")]),
    dict(slug="corner-shear", name="コーナーシャー", cat=("Cutting", "切断設備"),
         card_img="photo-set-corner.jpg", card_alt="コーナーシャー",
         card_specs=[("メーカー", "アマダ"), ("台数", "1台")],
         card_desc="板材のコーナー切断に用いる専用機です。",
         main=("photo-set-corner.jpg", "コーナーシャー"),
         specs=[("メーカー", "アマダ"), ("台数", "1台")],
         body=["板材の角（コーナー）を切り欠くための専用機です。",
               "板を折り曲げて箱の形に組み立てる製品では、曲げる前に角を切り欠いておく必要があります。その下ごしらえに使います。"],
         gallery=[]),
    dict(slug="cadmac", name="CADMAC（3D設計）", cat=("Design", "設計"),
         card_img="photo-set-cadmac.jpg", card_alt="CADMACの設計画面", card_small=True,
         card_specs=[("用途", "3D（三次元）設計")],
         card_desc="複雑なデザインやパイプの立体裁断にも対応します。",
         main=("photo-set-cadmac.jpg", "CADMACの設計画面"), main_small=True,
         specs=[("用途", "3D（三次元）設計")],
         body=["製品を3D（三次元）で設計するために使っています。",
               "3Dで展開することで、複雑なデザインも正確に、スピーディに形にできます。パイプなどの立体裁断にも対応しています。",
               "図面がないご依頼でも、詳細をうかがったうえで設計から対応します。"],
         gallery=[]),
    dict(slug="bender-10", name="10尺ベンダー", cat=("Bending", "曲げ設備"),
         card_img="photo-set-bender10.jpg", card_alt="10尺ベンダー",
         card_specs=[("メーカー", "コマツ"), ("台数", "1台")],
         card_desc="大型の板材の曲げ加工に対応します。",
         main=("photo-set-bender10.jpg", "10尺ベンダー"),
         specs=[("メーカー", "コマツ"), ("台数", "1台")],
         body=["金属の板を型で押さえ、まっすぐに折り曲げる機械（プレスブレーキ）です。",
               "「10尺」は曲げられる板の長さの目安で、約3mにあたります。保有するベンダーの中でいちばん大きく、長い製品の曲げ加工に使います。"],
         gallery=[]),
    dict(slug="bender-8", name="8尺ベンダー", cat=("Bending", "曲げ設備"),
         card_img="photo-set-bender8.jpg", card_alt="8尺ベンダー",
         card_specs=[("メーカー", "アマダ"), ("台数", "1台")],
         card_desc="プレスブレーキによる曲げ加工に対応します。",
         main=("photo-set-bender8.jpg", "8尺ベンダー"),
         specs=[("メーカー", "アマダ"), ("台数", "1台")],
         body=["金属の板を型で押さえ、まっすぐに折り曲げる機械（プレスブレーキ）です。",
               "「8尺」は曲げられる板の長さの目安で、約2.4mにあたります。このほか6尺・4尺のベンダー（いずれもアマダ）もあわせて保有しています。"],
         gallery=[]),
    dict(slug="set-press", name="セットプレス", cat=("Bending", "曲げ設備"),
         card_img="photo-set-press.jpg", card_alt="セットプレス",
         card_specs=[("メーカー", "アマダ"), ("台数", "1台")],
         card_desc="パンチング・成形などのプレス加工に用います。",
         main=("photo-set-press.jpg", "セットプレス"),
         specs=[("メーカー", "アマダ"), ("台数", "1台")],
         body=["金型を使い、板に穴をあけたり（パンチング）、形をつけたり（成形）するプレス機です。",
               "このほか、250t・100t・80t（2台）・60tのプレスも保有しています。"],
         gallery=[]),
    dict(slug="radial-drill", name="ラジアルボール盤", cat=("Drilling", "穴あけ設備"),
         card_img="photo-set-radial.jpg", card_alt="ラジアルボール盤",
         card_specs=[("台数", "1台")],
         card_desc="大型のワークへの穴あけ加工にも対応できるボール盤です。",
         main=("photo-set-radial.jpg", "ラジアルボール盤"),
         specs=[("台数", "1台")],
         body=["金属に穴をあけるための機械（ボール盤）です。",
               "腕（アーム）を回したり動かしたりして穴をあける位置を合わせるため、大きなワークでも材料を動かさずに穴あけができます。"],
         gallery=[]),
    dict(slug="shot-blast", name="ターンテーブルショットブラスト機", cat=("Surface", "表面処理"),
         card_img="photo-set-blast.jpg", card_alt="ターンテーブルショットブラスト機",
         card_specs=[("方式", "テーブルタイプ"), ("台数", "1台")],
         card_desc="スケール除去やバリ取りなどの表面処理に対応します。",
         main=("photo-blast.jpg", "ターンテーブルショットブラスト機"),
         specs=[("方式", "テーブルタイプ"), ("台数", "1台")],
         body=["細かな粒（研削材）を勢いよく吹き付けて、金属の表面を整える機械です。",
               "スケール除去・付着物除去・表面粗し・バリ取り・ピーニングなど、様々な加工のご要望に対応しています。"],
         gallery=[]),
    dict(slug="baking-furnace", name="焼付乾燥炉", cat=("Painting", "塗装設備"),
         card_img="photo-set-furnace.jpg", card_alt="焼付乾燥炉（塗装工場）",
         card_specs=[("全長", "10m"), ("焼付温度", "最高240℃")],
         card_desc="2017年に新設した塗装工場に設置しています。",
         main=("photo-set-furnace.jpg", "焼付乾燥炉（塗装工場）"),
         specs=[("全長", "10m"), ("焼付温度", "最高240℃"), ("最大加工寸法", "10000×3400×3400mm"),
                ("設置", "2017年新設の塗装工場"), ("塗装ブース設備", "アマダ・2台")],
         body=["塗装したあとの製品を、熱で焼き付けて乾かすための炉です。",
               "2017年に新設した塗装工場に、大阪府下最大級となる全長10mの焼付乾燥炉を備えています。間仕切りで5m×2に分けて使うこともでき、5m未満の製品は左右の炉で並行して作業できます。",
               "粉体塗装・吹付のどちらにも対応しています。"],
         gallery=[("2017_04_fac2.jpg", "塗装工場の内部"), ("2017_04_fac3.jpg", "塗装工場の内部"),
                  ("2017_04_fac4.jpg", "塗装工場の内部"), ("2017_04_fac5.jpg", "塗装工場の内部")]),
]

listing_path = os.path.join(ROOT, "facility", "index.html")
listing = open(listing_path, encoding="utf-8").read()
template = listing


def specs_html(rows, indent):
    pad = " " * indent
    return "".join(f'''
{pad}<div class="facility-equip__spec">
{pad}  <dt class="facility-equip__spec-label">{k}</dt>
{pad}  <dd>{v}</dd>
{pad}</div>''' for k, v in rows)


# --- 一覧のカード（9台）---
cards = []
for e in EQUIP:
    small = ' facility-equip__photo--small' if e.get("card_small") else ""
    cards.append(f'''
            <li class="facility-equip__card">
              <div class="facility-equip__photo{small}">
                <img src="/assets/images/{e["card_img"]}" alt="{e["card_alt"]}">
              </div>
              <div class="facility-equip__body">
                <h3 class="facility-equip__name"><a class="facility-equip__link" href="/facility/{e["slug"]}/">{e["name"]}</a></h3>
                <dl class="facility-equip__specs">{specs_html(e["card_specs"], 18)}
                </dl>
                <p class="facility-equip__desc">{e["card_desc"]}</p>
                <span class="btn-link facility-equip__more" aria-hidden="true"><span class="btn-link__text">詳しくみる</span>{ARROW}</span>
              </div>
            </li>
''')
a = listing.index('<ul class="facility-equip__grid">') + len('<ul class="facility-equip__grid">')
b = listing.index("</ul>", a)
listing = listing[:a] + "\n" + "".join(cards) + "\n          " + listing[b:]
open(listing_path, "w", encoding="utf-8").write(listing)

# --- 詳細ページ ---
for e in EQUIP:
    gallery_imgs = []
    for k, (fname, alt) in enumerate(e["gallery"], 1):
        out = f'{e["slug"]}-{k}.jpg'
        shutil.copyfile(os.path.join(old_img_dir, fname), os.path.join(img_dir, out))
        os.system(f'sips -Z 1200 "{os.path.join(img_dir, out)}" >/dev/null 2>&1')
        gallery_imgs.append((out, alt, fname))
    main_img, main_alt = e["main"]
    small = " facility-detail__photo--small" if e.get("main_small") else ""
    body = "\n".join(f"            <p>{p}</p>" for p in e["body"])
    gallery = ""
    if gallery_imgs:
        n = len(gallery_imgs)
        cols = "facility-detail__gallery--col2" if n % 2 == 0 else "facility-detail__gallery--col3"
        items = "\n".join(f'            <li><img src="/assets/images/facility/{o}" alt="{a}" loading="lazy"></li>' for o, a, _ in gallery_imgs)
        gallery = f'''
          <ul class="facility-detail__gallery {cols}">
{items}
          </ul>'''
    main = f'''
        <section class="page-section" data-reveal>
          <h2 class="section-head">
            <span class="section-head__en">{e["cat"][0]}</span>
            <span class="section-head__ja">{e["cat"][1]}</span>
          </h2>
          <div class="facility-detail">
            <figure class="facility-detail__photo{small}">
              <img src="/assets/images/{main_img}" alt="{main_alt}">
            </figure>
            <div class="facility-detail__body">
              <dl class="facility-equip__specs facility-detail__specs">{specs_html(e["specs"], 16)}
              </dl>
              <div class="facility-detail__text">
{body}
              </div>
            </div>
          </div>{gallery}
          <a class="btn-link facility-detail__back" href="/facility/"><span class="btn-link__text">設備一覧にもどる</span>{ARROW}</a>
        </section>
'''
    page = template
    page = re.sub(r"<title>[^<]*</title>", f'<title>{e["name"]} – 設備紹介 – 株式会社浅田鉄工</title>', page, count=1)
    page = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + f'{e["name"]} – 設備紹介 – 株式会社浅田鉄工', page, count=1)
    page = page.replace('<h1 class="page-head__ja">設備紹介</h1>', f'<h1 class="page-head__ja">{e["name"]}</h1>')
    page = page.replace("                <li>Facility</li>",
                        f'                <li><a href="/facility/">Facility</a></li>\n                <li>{e["name"]}</li>')
    page = page.replace("/assets/css/facility.css' media='all' />",
                        "/assets/css/facility.css' media='all' />\n<link rel='stylesheet' id='asada-facility-detail-css' href='/assets/css/facility-detail.css' media='all' />")
    a = page.index('<div class="page-main">') + len('<div class="page-main">')
    b = page.index("</div>", page.rindex("</section>", 0, page.index('<section class="cta"')))
    page = page[:a] + "\n" + main + "\n      " + page[b:]
    d = os.path.join(ROOT, "facility", e["slug"])
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(page)
    print(f'/facility/{e["slug"]}/ {e["name"]}: 写真 {main_img}＋補足{len(gallery_imgs)}枚 {[g[2] for g in gallery_imgs]}')
