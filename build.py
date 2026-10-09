#!/usr/bin/env python3
"""Builds the static website macrolia.app into ./docs (served by GitHub Pages).

Inputs: brand files, Play listing screenshots and the in-app legal texts.
Run: python3 build.py <play-listing dir> <brand dir> <policy_bg.json>
"""
import json, os, shutil, sys, html
from PIL import Image

PLAY, BRAND, POLICY = sys.argv[1:4]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")
EMAIL = "support@macrolia.app"

LANGS = {
    "en": {"dir": "", "locale": "en-US", "name": "English"},
    "bg": {"dir": "bg/", "locale": "bg", "name": "Български"},
    "de": {"dir": "de/", "locale": "de-DE", "name": "Deutsch"},
}

T = {
    "en": dict(
        title="Macrolia: Calories & Macros",
        desc="Precise calories and macros from the label. Your recipes, portions and goals.",
        soon="Coming soon to Google Play",
        lead="A food diary for people who want exact numbers, not estimates. Every product comes from the label on the pack in your hand: enter it once, and every day and every recipe is calculated correctly for years.",
        contact="Write to us",
        shots="A look inside",
        why="Why Macrolia",
        feats=[
            ("Accuracy from the label", "You copy the values per 100 g from the pack, so the numbers match what you actually eat. No borrowed, outdated or wrong data."),
            ("Your family cookbook", "Collect recipes from grandma's notebook, your cookbooks and favourite websites. Macrolia works out the calories and macros of every portion."),
            ("The exact portion of a cooked dish", "Weigh the finished dish together with the pot. Macrolia subtracts the pot and calculates exactly how much you ate."),
            ("For life, not just for one diet", "Lose, maintain or gain weight. When you reach your goal, Macrolia switches to maintenance and helps you keep the result."),
            ("Safe goals", "Your daily target follows the Mifflin-St Jeor equation and clinical guidelines, with a safe pace and a calorie floor."),
            ("Calories from activity", "Through Health Connect, from your phone alone, a watch or a fitness app. You choose how much is added to your target."),
        ],
        data_h="Your data stays yours",
        data="Everything stays on your phone. No sign-up, name or email needed, no ads and no tracking. You can save a backup, move your data to a new phone, and delete everything with one tap.",
        sub_h="Subscription",
        sub="Macrolia works with a monthly or yearly subscription, both with a 7-day free trial. Cancel any time in Google Play.",
        langs="Available in 12 languages, with a light and a dark theme.",
        disclaimer="Macrolia is not a medical device. If you are over 65, pregnant, have a medical condition or take medication, talk to your doctor before changing your diet.",
        privacy="Privacy Policy", terms="Terms of Use",
        legal_note="This text is currently available in Bulgarian, the original language of the app. Translations will follow.",
        back="Back to home",
        nf="Page not found.",
    ),
    "bg": dict(
        title="Macrolia: калории и макроси",
        desc="Точни калории и макроси от етикета. Вашите рецепти, порции и цели.",
        soon="Скоро в Google Play",
        lead="Дневник на храненето за хора, които искат точни числа, а не приблизителни. Всеки продукт идва от етикета на опаковката, която държите в ръка: въвеждате го веднъж и всеки ден и всяка рецепта се изчисляват вярно години напред.",
        contact="Пишете ни",
        shots="Как изглежда",
        why="Защо Macrolia",
        feats=[
            ("Точност от етикета", "Преписвате стойностите на 100 г от опаковката, затова числата съвпадат с това, което реално ядете. Без чужди, остарели или грешни данни."),
            ("Домашна готварска книга", "Съберете рецептите от тетрадката на баба, от готварските книги и любимите сайтове. Macrolia смята калориите и макросите на всяка порция."),
            ("Точна порция от сготвеното ястие", "Претеглете готовото ястие заедно със съда. Macrolia изважда теглото на съда и изчислява колко точно сте изяли."),
            ("За цял живот, не само за една диета", "Отслабване, задържане или качване на тегло. Когато стигнете целта, Macrolia минава на „Задържане“ и Ви помага да запазите резултата."),
            ("Безопасни цели", "Дневната цел се изчислява по формулата на Mifflin-St Jeor и клиничните препоръки, с безопасно темпо и долна граница за калориите."),
            ("Калории от движение", "Чрез Health Connect: от телефона (стига и без часовник), от часовник или фитнес приложение. Вие избирате колко да се добавят към целта."),
        ],
        data_h="Вашите данни са само Ваши",
        data="Всичко остава на Вашия телефон. Не е нужна регистрация, име или имейл, няма реклами и проследяване. Можете да запазите резервно копие, да пренесете данните си на нов телефон и да изтриете всичко с едно докосване.",
        sub_h="Абонамент",
        sub="Macrolia се ползва с месечен или годишен абонамент, и двата със 7 дни безплатен пробен период. Отказвате по всяко време в Google Play.",
        langs="На 12 езика, със светла и тъмна тема.",
        disclaimer="Macrolia не е медицинско изделие. Ако сте над 65 години, бременна, имате заболяване или приемате лекарства, консултирайте се с лекар, преди да промените храненето си.",
        privacy="Политика за поверителност", terms="Условия за ползване",
        legal_note="",
        back="Към началната страница",
        nf="Страницата не е намерена.",
    ),
    "de": dict(
        title="Macrolia: Kalorien & Makros",
        desc="Genaue Kalorien und Makros vom Etikett. Ihre Rezepte, Portionen und Ziele.",
        soon="Bald bei Google Play",
        lead="Ein Ernährungstagebuch für Menschen, die genaue Zahlen wollen, keine Schätzungen. Jedes Produkt stammt vom Etikett der Packung in Ihrer Hand: einmal eingeben, und jeder Tag und jedes Rezept wird über Jahre richtig berechnet.",
        contact="Schreiben Sie uns",
        shots="Ein Blick in die App",
        why="Warum Macrolia",
        feats=[
            ("Genau vom Etikett", "Sie übernehmen die Werte pro 100 g von der Packung, deshalb stimmen die Zahlen mit dem überein, was Sie wirklich essen. Keine fremden, veralteten oder falschen Daten."),
            ("Ihr Familienkochbuch", "Sammeln Sie Rezepte aus Omas Heft, aus Kochbüchern und von Ihren Lieblingsseiten. Macrolia berechnet Kalorien und Makros jeder Portion."),
            ("Die genaue Portion vom gekochten Gericht", "Wiegen Sie das fertige Gericht mitsamt Topf. Macrolia zieht den Topf ab und berechnet genau, wie viel Sie gegessen haben."),
            ("Fürs ganze Leben, nicht nur für eine Diät", "Abnehmen, Gewicht halten oder zunehmen. Am Ziel wechselt Macrolia auf „Gewicht halten“ und hilft Ihnen, das Ergebnis zu halten."),
            ("Sichere Ziele", "Ihr Tagesziel folgt der Mifflin-St-Jeor-Formel und klinischen Empfehlungen, mit sicherem Tempo und einer Kalorienuntergrenze."),
            ("Kalorien aus Bewegung", "Über Health Connect: vom Handy (auch ohne Uhr), von der Smartwatch oder einer Fitness-App. Sie wählen, wie viel zum Tagesziel dazukommt."),
        ],
        data_h="Ihre Daten gehören Ihnen",
        data="Alles bleibt auf Ihrem Handy. Keine Registrierung, kein Name, keine E-Mail, keine Werbung und kein Tracking. Sie können eine Sicherung speichern, Ihre Daten auf ein neues Handy übertragen und mit einem Tippen alles löschen.",
        sub_h="Abo",
        sub="Macrolia funktioniert mit einem Monats- oder Jahresabo, beide mit 7 Tagen kostenlosem Test. Jederzeit in Google Play kündbar.",
        langs="In 12 Sprachen, mit hellem und dunklem Design.",
        disclaimer="Macrolia ist kein Medizinprodukt. Wenn Sie über 65, schwanger oder krank sind oder Medikamente nehmen, sprechen Sie mit Ihrer Ärztin oder Ihrem Arzt, bevor Sie Ihre Ernährung umstellen.",
        privacy="Datenschutzerklärung", terms="Nutzungsbedingungen",
        legal_note="Dieser Text ist derzeit auf Bulgarisch verfügbar, der Originalsprache der App. Übersetzungen folgen.",
        back="Zur Startseite",
        nf="Seite nicht gefunden.",
    ),
}

CSS = """
:root{--bg:#f5f6f4;--card:#fff;--tx:#1c2622;--mut:#5f6c65;--ln:#e2e6e2;--ac:#2e7d5b;--acD:#245f45;--hero:#e8f4ea}
@media (prefers-color-scheme:dark){:root{--bg:#0f1c1e;--card:#172a2b;--tx:#eaf1ed;--mut:#9aa9a1;--ln:#25393a;--ac:#57c98c;--acD:#3d9a68;--hero:#132527}}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--tx);font:17px/1.6 system-ui,-apple-system,"Segoe UI",Roboto,"Noto Sans",Arial,sans-serif}
a{color:var(--ac)}
.wrap{max-width:1040px;margin:0 auto;padding:0 20px}
header{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:16px 0}
.logo img{height:34px;width:auto;display:block}
@media (prefers-color-scheme:dark){.logo img{filter:brightness(0) invert(1)}}
nav.lang{display:flex;gap:6px;flex-wrap:wrap}
nav.lang a{font-size:14px;text-decoration:none;color:var(--mut);padding:4px 10px;border:1px solid var(--ln);border-radius:999px}
nav.lang a[aria-current]{color:var(--ac);border-color:var(--ac);font-weight:600}
.hero{background:var(--hero);border-radius:24px;padding:48px 28px;display:grid;grid-template-columns:1fr auto;gap:32px;align-items:center}
.hero img.icon{width:150px;height:150px;border-radius:34px;box-shadow:0 10px 30px rgba(0,0,0,.15)}
h1{font-size:clamp(30px,5vw,46px);line-height:1.15;margin:0 0 14px}
.lead{font-size:clamp(17px,2.2vw,20px);color:var(--mut);margin:0 0 24px;max-width:620px}
.btns{display:flex;gap:12px;flex-wrap:wrap}
.btn{display:inline-block;padding:12px 20px;border-radius:12px;font-weight:600;text-decoration:none}
.btn.pri{background:var(--ac);color:#fff}
@media (prefers-color-scheme:dark){.btn.pri{color:#0f1c1e}}
.btn.sec{border:1.5px solid var(--ac);color:var(--ac)}
h2{font-size:clamp(24px,3.4vw,30px);margin:56px 0 18px}
.shots{display:flex;gap:14px;overflow-x:auto;scroll-snap-type:x mandatory;padding-bottom:10px}
.shots img{width:220px;height:auto;flex:0 0 auto;border-radius:16px;scroll-snap-align:start;border:1px solid var(--ln)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px}
.card{background:var(--card);border:1px solid var(--ln);border-radius:18px;padding:20px 22px}
.card h3{margin:0 0 6px;font-size:19px}
.card p{margin:0;color:var(--mut)}
.small{font-size:15px;color:var(--mut)}
footer{margin-top:64px;padding:28px 0 40px;border-top:1px solid var(--ln);font-size:15px;color:var(--mut)}
footer .links{display:flex;gap:18px;flex-wrap:wrap;margin-bottom:10px}
.legal{max-width:760px}
.legal .note{background:var(--hero);border-radius:12px;padding:12px 16px;font-size:15px}
.legal .mut{color:var(--mut)}
.legal ul{color:var(--mut)}
@media (max-width:640px){.hero{grid-template-columns:1fr;padding:32px 20px}.hero img.icon{width:96px;height:96px;border-radius:22px;order:-1}.shots img{width:62vw}}
"""


def page(lang, path_depth, title, desc, body, canonical):
    up = "../" * path_depth
    t = T[lang]
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="https://macrolia.app/{canonical}">
<link rel="icon" type="image/png" href="{up}img/icon-192.png">
<link rel="apple-touch-icon" href="{up}img/icon-192.png">
<meta name="theme-color" content="#2e7d5b">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:image" content="https://macrolia.app/img/og-{lang}.png">
<meta property="og:url" content="https://macrolia.app/{canonical}">
<link rel="stylesheet" href="{up}style.css">
</head>
<body>
<div class="wrap">
{body}
<footer>
<div class="links"><a href="{up}{LANGS[lang]['dir']}privacy/">{t['privacy']}</a><a href="{up}{LANGS[lang]['dir']}terms/">{t['terms']}</a><a href="mailto:{EMAIL}">{EMAIL}</a></div>
<div>© 2026 Macrolia · Uplift in Life</div>
</footer>
</div>
</body>
</html>
"""


def header(lang, depth, sub=""):
    up = "../" * depth
    links = "".join(
        f'<a href="{up}{LANGS[l]["dir"]}{sub}"{" aria-current=\"page\"" if l == lang else ""} hreflang="{l}">{LANGS[l]["name"]}</a>'
        for l in LANGS)
    return f'<header><a class="logo" href="{up}{LANGS[lang]["dir"]}"><img src="{up}img/logo.png" alt="Macrolia" width="152" height="34"></a><nav class="lang">{links}</nav></header>'


def home(lang):
    t = T[lang]
    depth = 1 if LANGS[lang]["dir"] else 0
    up = "../" * depth
    shots = "".join(f'<img src="{up}img/{lang}/{n}.webp" alt="" loading="lazy" width="540" height="960">' for n in range(1, 9))
    feats = "".join(f'<div class="card"><h3>{h}</h3><p>{p}</p></div>' for h, p in t["feats"])
    body = f"""{header(lang, depth)}
<main>
<section class="hero">
<div>
<h1>{t['desc']}</h1>
<p class="lead">{t['lead']}</p>
<div class="btns"><span class="btn pri">{t['soon']}</span><a class="btn sec" href="mailto:{EMAIL}">{t['contact']}</a></div>
</div>
<img class="icon" src="{up}img/icon-512.png" alt="" width="150" height="150">
</section>
<h2>{t['shots']}</h2>
<div class="shots">{shots}</div>
<h2>{t['why']}</h2>
<div class="grid">{feats}</div>
<div class="grid" style="margin-top:16px">
<div class="card"><h3>{t['data_h']}</h3><p>{t['data']}</p></div>
<div class="card"><h3>{t['sub_h']}</h3><p>{t['sub']}</p><p style="margin-top:8px">{t['langs']}</p></div>
</div>
<p class="small" style="margin-top:28px">{t['disclaimer']}</p>
</main>"""
    return page(lang, depth, t["title"], t["desc"], body, LANGS[lang]["dir"])


def legal(lang, kind, policy):
    t = T[lang]
    depth = 2 if LANGS[lang]["dir"] else 1
    up = "../" * depth
    b = policy[kind]["body"]
    # Placeholders stay in the app until the company exists; the public site names only the brand.
    b = b.replace("[Име на фирмата], [адрес на управление]",
                  "Macrolia (Uplift in Life), Виена, Австрия; пълните данни на фирмата ще бъдат добавени след регистрацията ѝ")
    assert "[" not in b, "placeholder left in legal text"
    title_bg = policy[kind]["title"]
    note = f'<p class="note" lang="{lang}">{t["legal_note"]}</p>' if t["legal_note"] else ""
    body = f"""{header(lang, depth, kind + '/')}
<main class="legal">
{note}
<h1 lang="bg">{title_bg}</h1>
<div lang="bg">{b}</div>
<p><a href="{up}{LANGS[lang]['dir']}">{t['back']}</a></p>
</main>"""
    name = t["privacy"] if kind == "privacy" else t["terms"]
    return page(lang, depth, f"{name} · Macrolia", name, body, LANGS[lang]["dir"] + kind + "/")


def write(rel, text):
    p = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)


def main():
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(os.path.join(OUT, "img"))
    policy = json.load(open(POLICY, encoding="utf-8"))
    icon = Image.open(os.path.join(BRAND, "macrolia-icon-play-512.png")).convert("RGBA")
    icon.save(os.path.join(OUT, "img/icon-512.png"), optimize=True)
    icon.resize((192, 192), Image.LANCZOS).save(os.path.join(OUT, "img/icon-192.png"), optimize=True)
    logo = Image.open(os.path.join(BRAND, "macrolia-logo.png"))
    logo.resize((304, int(304 * logo.height / logo.width)), Image.LANCZOS).save(os.path.join(OUT, "img/logo.png"), optimize=True)
    for lang, c in LANGS.items():
        src = os.path.join(PLAY, c["locale"])
        os.makedirs(os.path.join(OUT, "img", lang))
        for n in range(1, 9):
            im = Image.open(os.path.join(src, "phoneScreenshots", f"{n}.png")).convert("RGB")
            im.resize((540, 960), Image.LANCZOS).save(os.path.join(OUT, f"img/{lang}/{n}.webp"), quality=82)
        Image.open(os.path.join(src, "featureGraphic.png")).convert("RGB").save(os.path.join(OUT, f"img/og-{lang}.png"), optimize=True)
        write(c["dir"] + "index.html", home(lang))
        for kind in ("privacy", "terms"):
            write(c["dir"] + kind + "/index.html", legal(lang, kind, policy))
    write("style.css", CSS.strip() + "\n")
    t = T["en"]
    write("404.html", page("en", 0, "Macrolia", t["desc"], header("en", 0) + f'<main><h1>404</h1><p>{t["nf"]}</p><p><a href="/">{t["back"]}</a></p></main>', "").replace('href="img', 'href="/img').replace('href="style', 'href="/style').replace('src="img', 'src="/img'))
    write("CNAME", "macrolia.app\n")
    write(".nojekyll", "")
    write("robots.txt", "User-agent: *\nAllow: /\n")


if __name__ == "__main__":
    main()
