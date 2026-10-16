# asada-iws.com の DNS レコード控え

2026-10-16 に WADAX のネームサーバー（sv122.wadax-sv.jp）へ直接問い合わせて確認した、切り替え前のレコード。
ワイルドカード（`*.asada-iws.com`）はなし。AAAA・CAA もなし。

| 名前 | 種類 | 値 | 用途 |
|---|---|---|---|
| asada-iws.com | A | 153.123.7.87 | 旧サイト（WADAX） |
| www.asada-iws.com | CNAME | asada-iws.com | 旧サイト（WADAX） |
| mail.asada-iws.com | A | 153.123.7.87 | **メール** |
| asada-iws.com | MX | 10 sva106.wadax-sv.jp | **メール** |
| asada-iws.com | TXT | `v=spf1 +ip4:153.123.7.87 +include:_spf-sd.wadax-sv.jp ~all` | **メール（SPF）** |
| _dmarc.asada-iws.com | TXT | `v=DMARC1; p=none; adkim=s; aspf=s` | **メール（DMARC）** |
| default._domainkey.asada-iws.com | TXT | `v=DKIM1; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDiWK+8ODJHtGt9MQhNz3rW0aJF1eb/m532TRyDOqLlafwQENkGOYv7PuA+otLTMUcon/vOBwqAC6UoaXv0u11EgqYycDs7z172LbTHFHnjiofotFjEgbutH2vaimaTjFRlnCVomK3Mo/lpgjEShD6ecH3pfrbONt+kHcViI6VRrQIDAQAB;` | **メール（DKIM）** |

- 旧ネームサーバー：sv122.wadax-sv.jp / nssv101.wadax-sv.jp
- SOA：sv122.wadax-sv.jp. postmaster.asada-iws.com. 2023111402
- ドメインの登録先：お名前.com（GMO）、期限 2026-12-27

## Cloudflare 側の設定（切り替え前に入れておくもの）

上の7件をすべて同じ値で入れる。**プロキシはすべてオフ（DNS only・灰色の雲）**にする。

- `mail` の A をプロキシすると、メールソフトが WADAX のメールサーバーにつながらなくなる
- ルートの A と `www` も、切り替え直後は旧サイト（WADAX）を見せ続けるためにプロキシなしで残す。
  新サイトへの切り替えは「切り替え後の作業」で Workers のカスタムドメインを付けて行う

メールの5件（mail の A、MX、SPF、DMARC、DKIM）が抜けていると、切り替えた瞬間からメールの送受信が止まる。
