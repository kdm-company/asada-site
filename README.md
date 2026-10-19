# 株式会社浅田鉄工 公式サイト

本番ドメイン：asada-iws.com（ネームサーバー切り替え前は Workers の URL で公開）

- デザインの元：WordPress のテスト版 https://test-asada.mccoy04.com/ をトレースした静的サイト
- 事実の正本：Notion「浅田鉄工 ナレッジベース」の本編。「要社内確認バッファ」の項目は載せない。KB にないことは書かない
- `浅田鉄工/` 直下にある index.html などは、KDM が作った別デザインの静的版。このリポジトリとは混ぜない

## 構成

| 場所 | 中身 |
|---|---|
| `public/` | 公開されるファイル一式。**ここだけが配信される** |
| `public/_redirects` | 旧サイト（WordPress）の URL → 新ページの転送表 |
| `public/_headers` | 公開確認中の noindex ヘッダー（切り替え後に消す） |
| `public/404.html` | 存在しない URL のときに返すページ |
| `wrangler.jsonc` | Cloudflare Workers の設定。トップ（/）だけ Worker を通し、ほかは静的配信 |
| `src/index.js` | トップの「新着情報」とNEWS帯に note の最新記事を差し込む Worker |
| `scripts/check_links.py` | サイト内リンク・画像の参照先がそろっているかの確認 |
| `scripts/build_works_detail.py` | 事例の詳細ページ36件を作る（一度きりの生成用。以後は HTML を直接直してよい） |
| `scripts/build_facility_detail.py` | 設備カード9枚と設備の詳細ページ9件を作る（同上） |
| `docs/` | ネームサーバー切り替えの依頼文・切り替え後の作業一覧・DNS の控え |

ページ：トップ / 事業内容 `service/` / 事例紹介 `works/`（詳細36件 `works/e-01/` など）/ 設備紹介 `facility/`（詳細9件 `facility/fiber-laser/` など）/ 新着情報 `news/`（記事 `news/renewal/`、カテゴリ `news/category/info/`、月別 `news/2026/`）/ 会社案内 `company/` / お問い合わせ `contact/` / プライバシーポリシー `privacy/`

採用情報ページは置かない（2026-10-16 の打ち合わせで削除）。

お問い合わせフォームは置かない（2026-10-16 決定）。電話と、旧サイトと同じ表記のメールアドレス（全角の＠＋「アットマークを小文字へ変更ください」）で受ける。

## 公開（デプロイ）

`main` に push すると GitHub Actions がリンク確認のあと `wrangler deploy` する。
リポジトリの Settings → Secrets and variables → Actions に `CLOUDFLARE_API_TOKEN` と `CLOUDFLARE_ACCOUNT_ID` が無いうちは、リンク確認だけ行ってデプロイは飛ばす。

手元から直接出す場合（Cloudflare にログイン済みの端末で）：

```bash
npx wrangler@4 deploy
```

## 確認

```bash
python3 -I scripts/check_links.py public
```

プレビューは `/Users/yu-ki/Desktop/サイト制作/.claude/launch.json` の `asada-trace`（port 8096）。Desktop 配下は直接配信できないので、`rsync -a --delete public/ /tmp/asada-trace-preview/` で写してから開く。転送表と 404 はこのプレビューでは動かないので、Workers の URL で確かめる。

## note の最新記事（トップの新着情報・NEWS帯）

平原こうや公式サイトと同じ組み方。`src/index.js` がトップを返すときに note の RSS（https://note.com/asada_tekko/rss）を取り込み、
`#note-feed`（新着情報）と `#note-ticker`（NEWS帯）を書き換える。

- note の最新3件と、`index.html` に書いた自社のお知らせを日付順に混ぜ、新着情報は4件・NEWS帯は3件まで出す
- note の記事は別タブで開く。ラベルは「note」
- 取り込み結果は1時間キャッシュ（失敗時は5分）。**workers.dev の確認用URLではキャッシュが効かず、表示のたびに RSS を取りに行く**（本番ドメインに切り替えると効く）
- RSS が取れないときは `index.html` の一覧のまま表示する
- 動作確認は応答ヘッダー `X-Note-Feed`：`rss`＝差し込み成功／`static`＝RSS 取得失敗で静的一覧（GET で見る。HEAD は Worker を通らない）
- 手元で動かすときは `npx wrangler@4 dev`。プレビューは launch.json の `asada-worker`（port 8797、`/tmp/asada-worker-dev` に写してから起動）

## 新着記事を足すとき

note の記事は自動で出るので、ここで書くのは自社のお知らせ（サイト内の記事）だけ。

静的サイトなので、次の箇所を手で更新する。

1. `public/news/renewal/` を複製して記事ページを作る（日付・カテゴリ・本文・title）
2. 一覧：`public/news/index.html`、`public/news/category/info/index.html`、`public/news/2026/index.html`（年が変わったら月別アーカイブのページを足す）
3. 各記事ページと一覧ページのサイドバー（カテゴリの件数・月別アーカイブ・最新記事）
4. トップ `public/index.html` のヒーロー下の NEWS ティッカーと「新着情報」一覧
5. `python3 -I scripts/check_links.py public` でリンク切れがないか確かめる

## 写真の決まり

- 写真は現行サイト（asada-iws.com）かテスト版にあるものだけを使う。生成画像やネットの画像は使わない
- 人物が写っている写真は載せない（退職者の写り込み・ハローワークからの問い合わせ対策）。例外：ショットブラスト機の写真（作業者の後ろ姿、2026-10-16 ユーザー判断）
- 旧式の設備（旧レーザー加工機・ストッカー・ユニットワーカー）の写真は載せない。最新のファイバーレーザーの写真はまだないので、加工品の写真で代用している
- 出どころと、外した写真・判断に迷った写真の一覧は `docs/写真の出どころ.md`

## 赤のアクセント

`--color-accent: #e90000`（現行サイトの赤）。使うのは次の3か所だけ。
1. トップのキャッチコピーの「欲しい」
2. トップ「製品事例のご紹介」の番号（01〜06）
3. 会社案内の沿革の年表の点

## 元のテスト版からの主な変更

- ヘッダーのロゴを拡大（スマホ 160→200px、PC 1024px 以上 220→280px）
- WordPress の記事・アーカイブを `/news/` の下にまとめた（`/renewal/` → `/news/renewal/` など）
- フッターのメニュー順をヘッダーと同じにした
- 文言・数字・設備をナレッジベースに合わせた（創業65年超、社員数29名、設備のメーカー・台数、沿革など）
- 主要取引先（20社）と主要取引銀行（4行）は、2026-10-16 にユーザーから受けた一覧どおり（ナレッジベースの一覧とは異なる）
- 2026-10-16 の打ち合わせ反映：ご挨拶をテスト版の文に戻し明朝体に、事例紹介のピックアップと採用情報を削除、事例・設備の詳細ページを追加、人物写真の差し替え、赤のアクセント
- KB に裏付けのない事例カテゴリ（商業施設・各種イベント）と、写真と機械が一致しない設備カードを外した
