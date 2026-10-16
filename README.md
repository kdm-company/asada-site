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
| `wrangler.jsonc` | Cloudflare Workers（静的配信）の設定 |
| `scripts/check_links.py` | サイト内リンク・画像の参照先がそろっているかの確認 |
| `docs/` | ネームサーバー切り替えの依頼文・切り替え後の作業一覧・DNS の控え |

ページ：トップ / 事業内容 `service/` / 事例紹介 `works/` / 設備紹介 `facility/` / 新着情報 `news/`（記事 `news/renewal/`、カテゴリ `news/category/info/`、月別 `news/2026/`）/ 会社案内 `company/` / 採用情報 `recruit/` / お問い合わせ `contact/` / プライバシーポリシー `privacy/`

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

## 新着記事を足すとき

静的サイトなので、次の箇所を手で更新する。

1. `public/news/renewal/` を複製して記事ページを作る（日付・カテゴリ・本文・title）
2. 一覧：`public/news/index.html`、`public/news/category/info/index.html`、`public/news/2026/index.html`（年が変わったら月別アーカイブのページを足す）
3. 各記事ページと一覧ページのサイドバー（カテゴリの件数・月別アーカイブ・最新記事）
4. トップ `public/index.html` のヒーロー下の NEWS ティッカーと「新着情報」一覧
5. `python3 -I scripts/check_links.py public` でリンク切れがないか確かめる

## 元のテスト版からの主な変更

- ヘッダーのロゴを拡大（スマホ 160→200px、PC 1024px 以上 220→280px）
- WordPress の記事・アーカイブを `/news/` の下にまとめた（`/renewal/` → `/news/renewal/` など）
- フッターのメニュー順をヘッダーと同じにし、採用情報を追加
- 文言・数字・設備をナレッジベースに合わせた（創業65年超、社員数29名、設備のメーカー・台数、沿革、主要取引先など）
- KB に裏付けのない事例カテゴリ（商業施設・各種イベント）と、写真と機械が一致しない設備カードを外した
