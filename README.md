# Albert 8

A responsive Dash compound-interest calculator with light/dark Bootstrap themes,
matching Plotly templates, and comparisons before fees, after fees, and against
contributions alone. The second chart applies inflation using the original model.

## Run locally

Use Python 3.12. On Windows:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Open <http://127.0.0.1:8050>. On macOS/Linux, use `python3.12` to create the
environment and `.venv/bin/python` for subsequent commands.

The light/dark switch uses `dash_bootstrap_templates.ThemeSwitchAIO` with Flatly
and Darkly. It changes both the interface and both charts without resetting the
plan. Bootstrap theme stylesheets and the switch icons load from a CDN, so the
browser needs internet access. Inputs retain their original defaults and ranges.
Currency selection changes labels only; it does not convert values.

## Shared-link previews / Linkin esikatselu / 链接预览

The initial server-rendered HTML includes Open Graph and Twitter card metadata,
a 1200 x 630 PNG sharing image, and a matching app icon. Crawlers do not need
JavaScript. Sharing copy is in English regardless of the browser's saved language.
Set `PUBLIC_URL` to the public HTTPS app root (for example
`https://your-app.example`) in the hosting environment, especially behind an
HTTPS-terminating reverse proxy. Without it, URLs use the incoming request's
scheme and host. Do not set it to localhost in production.

Suomi: Linkin mukana näytetään Albert 8:n esikatselukuva, nimi ja kuvaus.
Aseta palvelimen `PUBLIC_URL`-ympäristömuuttujaan sovelluksen julkinen HTTPS-osoite.
Esikatselu toimii vasta, kun muutokset ja kuva ovat julkisesti saatavilla.
Jakopalvelut voivat säilyttää vanhan esikatselun välimuistissaan; päivitys voi
vaatia palvelun oman linkkitarkistimen käyttöä. Selainkohtainen kielivalinta
ei vaikuta englanninkieliseen esikatseluun.

中文：分享链接包含 Albert 8 的预览图片、标题和说明。请将服务器环境变量
`PUBLIC_URL` 设为应用的公开 HTTPS 地址。部署后图片必须可公开访问；
分享平台可能缓存旧预览，需要使用该平台的链接检查工具刷新。
预览文案使用英语，不受浏览器语言选项影响。

## Languages / Kielet / 语言

Choose **English**, **中文（简体）** (Simplified Chinese), or **Suomi** (Finnish)
in the labelled header selector. The choice is saved in this browser. Switching
language updates interface copy, accessible labels, the page title and document
language, year labels, chart legends, axes, hover text, and Plotly controls without
resetting the plan, currency, or light/dark theme. Finnish uses decimal commas.
Plotly's Finnish and Chinese locale bundles also load from its CDN; browser
internet access is required. There is no separate empty-state or validation
message in the slider-based calculator.

Translations live in `translations.py`; calculation functions do not depend on
the selected language. The tests check translation coverage and verify identical
chart values across all three languages, both themes, and all four currencies.

### Suomi

Valitse yläreunan **Kieli**-valikosta **Suomi**, **English** tai **中文（简体）**.
Valinta tallennetaan selaimeen. Kielen vaihtaminen ei nollaa suunnitelmaa,
valuuttaa eikä vaaleaa tai tummaa teemaa. Käyttöliittymä, saavutettavat nimet,
sivun otsikko ja kuvaajat päivittyvät valitulle kielelle. Suomenkielisessä
esityksessä käytetään desimaalipilkkua. Valuutta muuttaa vain symbolia, ei arvoja.

Käynnistä Python 3.12 -ympäristössä yllä olevan ohjeen komennoilla ja avaa
<http://127.0.0.1:8050>. Teemat, kuvakkeet ja kuvaajien kielitiedostot tarvitsevat
internetyhteyden. Vuotuinen tuotto ja kulut jaetaan 12:lla; kuukausisäästö lisätään
kuukauden lopussa. Inflaatiokuvaaja pienentää saldoa lisäksi vuotuisen inflaation
kahdestoistaosalla ennen säästön lisäämistä. Kuukausisäästö pysyy vakiona.
Arvot esitetään vuoden lopussa. Vertailutilille ei makseta korkoa. Veroja ja
markkinoiden vaihtelua ei huomioida. Laskelmat eivät ole sijoitusneuvontaa.

Suorita tarkistukset alla olevan **Checks**-kohdan komennoilla. Käyttöympäristö on
Python 3.12 (`.python-version`). Linuxissa/Herokussa `Procfile` käyttää Gunicornia;
Gunicorn ei ole Windows-palvelin. Riippuvuudet ovat `requirements.txt`-tiedostossa
ja käännökset `translations.py`-tiedostossa.

### 中文（简体）

在页首的**语言**菜单中选择 **中文（简体）**、**English** 或 **Suomi**。
浏览器会保存您的选择。切换语言不会重置投资计划、货币或浅色/深色主题。
界面文字、无障碍标签、页面标题和图表会随语言更新。芬兰语使用逗号作为小数分隔符。
货币选项仅更改显示符号，不进行汇率换算。

使用 Python 3.12，按上方命令创建虚拟环境、安装依赖并运行应用，然后打开
<http://127.0.0.1:8050>。主题、图标和图表语言文件需要网络连接。
年收益率和年费率除以12，按月计算；每月投入在月末加入。
通胀图表还会在加入当月投入前，按年通胀率的十二分之一扣减余额。
每月投入保持不变，图表显示年末数值。对照账户不计利息，也不包含税费和市场波动。
测算仅供参考，不构成投资建议。

使用下方 **Checks** 中的命令运行测试。`.python-version` 指定 Python 3.12。
Linux/Heroku 上的 `Procfile` 使用 Gunicorn；Gunicorn 不适用于 Windows。
依赖版本列在 `requirements.txt` 中，翻译位于 `translations.py` 中。

## Calculation model

Annual returns and annual fees are divided by 12. Each month, the balance grows
by the monthly return less monthly fees, then the monthly contribution is added.
The fee-free comparison omits fees. The inflation-adjusted series additionally
multiply the monthly balance by `1 - annual_inflation / 12` before the contribution
is added. Contributions are fixed, not inflation-indexed. Charts show year-end
values. Taxes, market volatility, and interest on the bank comparison are excluded.
These are illustrative projections, not financial advice.

## Runtime and dependencies

`.python-version` selects Python **3.12**, allowing the hosting platform to apply
the latest available 3.12 security patch. It replaces Heroku's deprecated
`runtime.txt`. The existing `Procfile` still exposes `app:server` with Gunicorn
on Linux/Heroku; Gunicorn is not a Windows server. Set `secret_key` to a stable
random secret in hosting configuration if Flask sessions are needed.

Direct dependencies are pinned to the latest stable PyPI releases checked on
2026-11-10, compatible with Python 3.12. Obsolete standalone
`dash-core-components`, `dash-html-components`, and `dash-table` packages have
been removed; Dash now bundles these components. Transitive dependencies are
resolved by pip rather than retaining obsolete Python 3.9-era pins.

## Checks

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m pip check
```

Tests cover monthly compounding, fees, inflation, original defaults and limits,
currencies, Plotly templates, layout, and Dash callback responses.
