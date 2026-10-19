// トップページ（/）の「新着情報」とヒーロー下の NEWS 帯に、note の最新記事を差し込む（Cloudflare Workers）。
// 組み方は平原こうや公式サイト（functions/index.js）と同じ。
//
// note 公式ヘルプの案内どおり、RSS はサーバー側（Cloudflare）で取り込む。
// 取り込んだ結果は1時間キャッシュするので、note への問い合わせはおおむね1時間に1回。
// note を更新すると、遅くとも1時間ほどでHPに反映される。
// ※ workers.dev の確認用URLではキャッシュが効かないため、表示のたびに RSS を取りに行く（本番ドメインでは効く）。
// RSS が取れないときは、index.html に書かれている一覧をそのまま表示する。
// トップ以外のページは Worker を通らず、public/ の静的ファイルがそのまま返る（wrangler.jsonc の run_worker_first）。

const FEED = 'https://note.com/asada_tekko/rss';
const NOTE_LIMIT = 3;      // note から取り込む件数
const LIST_LIMIT = 4;      // 「新着情報」に並べる件数（note と自社のお知らせを日付順に混ぜる）
const TICKER_LIMIT = 3;    // ヒーロー下の NEWS 帯で順に流す件数
const TTL = 3600;          // 取得成功時のキャッシュ（秒）
const RETRY_TTL = 300;     // 取得失敗時は5分あけて再挑戦
const CACHE_KEY = 'https://asada-iws.com/__cache/note-feed-v1';
const LINK_RE = /^https:\/\/note\.com\/asada_tekko\/n\/[A-Za-z0-9]+$/;

const ARROW = '<span class="news__arrow btn-link__icon"><img src="/assets/images/icons/arrow-right.svg" alt="" class="btn-link__icon-img btn-link__icon-img--out"><img src="/assets/images/icons/arrow-right.svg" alt="" class="btn-link__icon-img btn-link__icon-img--in"></span>';

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    if (request.method !== 'GET' || url.pathname !== '/') return env.ASSETS.fetch(request);

    // 一覧の中身が変わっても静的ファイルの ETag は変わらないため、条件付きリクエストは使わない
    const req = new Request(request);
    req.headers.delete('If-None-Match');
    req.headers.delete('If-Modified-Since');
    const res = await env.ASSETS.fetch(req);
    if (res.status !== 200 || !(res.headers.get('content-type') || '').includes('text/html')) return res;

    let notes = null;
    try {
      notes = await loadItems(ctx);
    } catch (e) {
      notes = null;
    }
    if (!notes || !notes.length) return mark(res, 'static');   // RSS が取れないときは index.html の一覧のまま

    const page = await res.text();
    const items = notes.map((n) => ({ ...n, cat: 'note', external: true }))
      .concat(siteNews(page))
      .sort((a, b) => b.time - a.time);
    const listHtml = items.slice(0, LIST_LIMIT).map(renderNews).join('');
    const tickerHtml = items.slice(0, TICKER_LIMIT).map(renderTicker).join('');

    const headers = new Headers(res.headers);
    headers.delete('ETag');
    headers.delete('Last-Modified');
    headers.delete('Content-Length');
    headers.set('X-Note-Feed', 'rss');   // 動作確認用：RSS から差し込んだ印
    return new HTMLRewriter()
      .on('#note-feed', { element(el) { el.setInnerContent(listHtml, { html: true }); } })
      .on('#note-ticker', { element(el) { el.setInnerContent(tickerHtml, { html: true }); } })
      .transform(new Response(page, { status: 200, headers }));
  },
};

function mark(res, value) {
  const headers = new Headers(res.headers);
  headers.set('X-Note-Feed', value);
  return new Response(res.body, { status: res.status, headers });
}

async function loadItems(ctx) {
  const cache = caches.default;
  const key = new Request(CACHE_KEY);
  const hit = await cache.match(key);
  if (hit) return hit.json();

  let items = [];
  try {
    const r = await fetch(FEED, { headers: { 'User-Agent': 'Mozilla/5.0 (compatible; asada-iws.com note-feed)' } });
    if (r.ok) items = parse(await r.text());
  } catch (e) {
    items = [];
  }
  const ttl = items.length ? TTL : RETRY_TTL;
  ctx.waitUntil(cache.put(key, new Response(JSON.stringify(items), {
    headers: { 'Content-Type': 'application/json', 'Cache-Control': 'max-age=' + ttl },
  })));
  return items;
}

export function parse(xml) {
  const items = [];
  const re = /<item>([\s\S]*?)<\/item>/g;
  let m;
  while ((m = re.exec(xml))) {
    const body = m[1];
    const title = text(body, 'title');
    const link = text(body, 'link').split(/[?#]/)[0];
    const pub = Date.parse(text(body, 'pubDate'));
    if (!title || !LINK_RE.test(link) || Number.isNaN(pub)) continue;
    items.push({ title, link, time: pub });
  }
  items.sort((a, b) => b.time - a.time);
  return items.slice(0, NOTE_LIMIT);
}

// index.html に書かれている自社のお知らせ（新着情報の一覧）を読み取る
export function siteNews(page) {
  const list = page.match(/<ul class="news__list" id="note-feed">([\s\S]*?)<\/ul>/);
  if (!list) return [];
  const items = [];
  const re = /<a href="([^"]+)">\s*<time class="news__date" datetime="(\d{4}-\d{2}-\d{2})">[^<]*<\/time>\s*<span class="news__cat">([^<]*)<\/span>\s*<span class="news__title">([^<]*)<\/span>/g;
  let m;
  while ((m = re.exec(list[1]))) {
    // datetime は日本時間の日付。並べ替え用に、その日の0時（日本時間）にする
    items.push({ link: m[1], time: Date.parse(m[2] + 'T00:00:00+09:00'), cat: m[3], title: decode(m[4]), external: false });
  }
  return items;
}

function text(body, tag) {
  const m = body.match(new RegExp('<' + tag + '>([\\s\\S]*?)</' + tag + '>'));
  if (!m) return '';
  const v = m[1].trim();
  const cdata = v.match(/^<!\[CDATA\[([\s\S]*)\]\]>$/);
  if (cdata) return cdata[1].trim();
  return decode(v);
}

function decode(v) {
  return v
    .replace(/&#x([0-9a-f]+);/gi, (_, h) => String.fromCodePoint(parseInt(h, 16)))
    .replace(/&#(\d+);/g, (_, d) => String.fromCodePoint(parseInt(d, 10)))
    .replace(/&quot;/g, '"').replace(/&apos;/g, "'")
    .replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&');
}

function esc(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

// 日付は日本時間で表示する（[表示用, datetime 属性用]）
function jstDate(ms) {
  const d = new Date(ms + 9 * 3600 * 1000);
  const p = (n) => String(n).padStart(2, '0');
  const y = d.getUTCFullYear(), mo = p(d.getUTCMonth() + 1), da = p(d.getUTCDate());
  return [y + '.' + mo + '.' + da, y + '-' + mo + '-' + da];
}

function anchor(item) {
  return '<a href="' + esc(item.link) + '"' + (item.external ? ' target="_blank" rel="noopener"' : '') + '>';
}

// index.html の既存マークアップと同じ形で出力する
export function renderNews(item) {
  const [label, iso] = jstDate(item.time);
  return '<li class="news__item">' + anchor(item)
    + '<time class="news__date" datetime="' + iso + '">' + label + '</time>'
    + '<span class="news__cat">' + esc(item.cat) + '</span>'
    + '<span class="news__title">' + esc(item.title) + '</span>'
    + ARROW + '</a></li>';
}

export function renderTicker(item, i) {
  const [label, iso] = jstDate(item.time);
  return '<li class="hero-ticker__item' + (i === 0 ? ' is-active' : '') + '">' + anchor(item)
    + '<time class="hero-ticker__date" datetime="' + iso + '">' + label + '</time>'
    + '<span class="hero-ticker__track"><span class="hero-ticker__title">' + esc(item.title) + '</span></span>'
    + '</a></li>';
}
