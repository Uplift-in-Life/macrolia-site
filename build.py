#!/usr/bin/env python3
"""Builds the static website macrolia.app into ./docs (served by GitHub Pages).

Inputs: brand files, Play listing screenshots, app screens in assets/ and the in-app legal texts.
Run: python3 build.py <play-listing dir> <brand dir> <policy_bg.json>
"""
import json, os, re, shutil, sys, html
from PIL import Image

PLAY, BRAND, POLICY = sys.argv[1:4]
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "docs")
ASSETS = os.path.join(ROOT, "assets")
EMAIL = "support@macrolia.app"

LANGS = {
    "en": {"dir": "", "locale": "en-US", "name": "English"},
    "bg": {"dir": "bg/", "locale": "bg", "name": "Български"},
    "de": {"dir": "de/", "locale": "de-DE", "name": "Deutsch"},
    "es": {"dir": "es/", "locale": "es-ES", "name": "Español"},
    "fr": {"dir": "fr/", "locale": "fr-FR", "name": "Français"},
    "it": {"dir": "it/", "locale": "it-IT", "name": "Italiano"},
    "pl": {"dir": "pl/", "locale": "pl-PL", "name": "Polski"},
    "nl": {"dir": "nl/", "locale": "nl-NL", "name": "Nederlands"},
    "ro": {"dir": "ro/", "locale": "ro", "name": "Română"},
    "el": {"dir": "el/", "locale": "el-GR", "name": "Ελληνικά"},
    "ru": {"dir": "ru/", "locale": "ru-RU", "name": "Русский"},
    "uk": {"dir": "uk/", "locale": "uk", "name": "Українська"},
    "tr": {"dir": "tr/", "locale": "en-US", "name": "Türkçe"},   # no Play listing yet: English share image
    "sr": {"dir": "sr/", "locale": "en-US", "name": "Srpski"},
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
        langs="Available in 14 languages, with a light and a dark theme.",
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
        langs="In 14 Sprachen, mit hellem und dunklem Design.",
        disclaimer="Macrolia ist kein Medizinprodukt. Wenn Sie über 65, schwanger oder krank sind oder Medikamente nehmen, sprechen Sie mit Ihrer Ärztin oder Ihrem Arzt, bevor Sie Ihre Ernährung umstellen.",
        privacy="Datenschutzerklärung", terms="Nutzungsbedingungen",
        legal_note="Dieser Text ist derzeit auf Bulgarisch verfügbar, der Originalsprache der App. Übersetzungen folgen.",
        back="Zur Startseite",
        nf="Seite nicht gefunden.",
    ),
}



# Switched on in January 2027, when the company exists and marketing starts (Дани 2026-10-24):
# the anonymous founder story and the videos are ready but not published before that.
JANUARY = False

# Texts of the new home page. A language without an entry here still gets the first, simple page (T).
N = {
    "bg": dict(
        soon="Скоро в Google Play",
        h1a="Не още една диета.", h1b="Твоята система за цял живот.",
        lead="Macrolia смята калориите и макросите точно от етикета на продукта, който държите в ръка. Въвеждате го веднъж и всеки ден, всяка рецепта и всяка порция са верни години напред.",
        how_btn="Вижте как работи", video_btn="Гледайте видеото",
        label=dict(t="Хранителна стойност на 100 г", rows=[("Енергия", "61 kcal"), ("Мазнини", "2 г"), ("Въглехидрати", "4,7 г"), ("Белтъчини", "4 г"), ("Сол", "0,1 г")],
                   note="Кисело мляко 2%: от етикета направо в приложението"),
        hero_alt="Дневният калкулатор в Macrolia",
        why="Защо Macrolia",
        yoyo_a="Йо-йо не идва от режима. Идва, когато спреш.",
        yoyo_b="С Macrolia няма от какво да спираш, защото режимът е за цял живот.",
        how="Как работи",
        how_h="Всичко, от което имате нужда, без излишни неща",
        feats=[
            ("label", "Продукти", "Точно от етикета, не от чужди бази",
             "Преписвате стойностите на 100 г от опаковката или просто снимате етикета. Числата съвпадат с това, което реално ядете.",
             "📷 AI снимка на етикета попълва полетата вместо Вас"),
            ("rec", "Рецепти", "Вашата електронна готварска книга",
             "Рецептите от тетрадката на баба, от книгите на рафта и от любимите групи, на едно място. Въвеждате ги веднъж и ги ползвате винаги.", ""),
            ("cook", "Порция", "Точната порция от цялата тенджера",
             "Претегляте готовото ястие заедно със съда. Macrolia изважда съда и смята колко точно сте изяли.", ""),
            ("plan", "План за утре", "Планирате, пазарувате, ядете",
             "Още от днес въвеждате какво ще ядете утре. Купувате само нужното, а в полунощ планът става Вашият ден.", ""),
            ("mode", "Цел", "Отслабване, задържане или качване",
             "Когато стигнете целта, минавате на „Задържане“. Ако животът се промени, просто сменяте режима. Дневният лимит е по формулата Mifflin-St Jeor и клиничните препоръки, с безопасно темпо.", ""),
            ("rest", "Ресторант и кафе", "И навън знаете какво ядете",
             "Снимате чинията и AI разпознава какво има в нея. Стойността е приблизителна и е отбелязана с ≈. По-добре приблизително, отколкото нищо.", ""),
        ],
        alts=dict(label="Нов продукт със снимка на етикета", rec="Рецепти", cook="Порция от сготвено ястие", plan="План за утре", mode="Смяна на режим", rest="Снимка на ястие с AI"),
        more=[
            ("Калории от движение", "Чрез Health Connect от телефона, часовник или фитнес приложение. Вие избирате колко да се добавят към лимита."),
            ("Тегло, графика, отчет", "Графика на теглото, снимки „преди и след“ само за Вас и отчет в PDF и Excel."),
            ("Съвети за баланс", "Кратки подсказки, когато протеинът или мазнините са извън целта. Помага, не командва."),
        ],
        who="За кого е",
        who_h="За всяка, която иска да остане в режим",
        groups=[
            ("Уморената от йо-йо", "Йо-йо не идва от режима. Идва, когато спреш."),
            ("Младата майка", "След бебето пак влизаш в режим."),
            ("Жената над 50", "Годините не са причина да се откажеш."),
            ("Пътуващата и забързаната", "И в ресторанта знаеш какво да поръчаш."),
            ("Точната", "Който точно спазва плана, получава точен резултат."),
        ],
        video="Видео", video_h="След бебето",
        video_p="Животът се променя, режимът остава. Една смяна на режима и сте отново на път.",
        video_tag="AI анимация · илюстрация",
        story="Как започна всичко", story_big="25 кг", story_small="за 7 месеца",
        story_p="Macrolia започна като една Excel таблица. С нея създателката на приложението свали 25 кг за 7 месеца и задържа резултата. Таблицата стана приложение, за да може същата система да помогне и на други.",
        story_disc="Резултатите са различни при всеки човек.",
        data_h="Вашите данни са само Ваши",
        data="Всичко остава на телефона Ви. Без регистрация, без реклами и проследяване. Снимката за AI анализ се изпраща само за изчислението и не се пази.",
        sub_h="Абонамент",
        sub="Месечен или годишен абонамент, и двата със 7 дни безплатно. Отказвате по всяко време в Google Play.",
        langs="На 14 езика, със светла и тъмна тема.",
        faq_h="Въпроси",
        faq=[
            ("Кога излиза приложението?", "Подготвяме пускането в Google Play. Пишете ни и ще Ви кажем, когато е готово."),
            ("Има ли версия за iPhone?", "Засега само за Android. Версия за iPhone планираме след това."),
            ("Защо няма скенер за баркод?", "Базите с баркодове се попълват от потребители и често са грешни или остарели. В Macrolia всяка стойност идва от етикета, затова числата са точни."),
            ("Колко AI снимки мога да направя?", "До 100 снимки на месец, общо за етикети и ястия."),
        ],
    ),
}

from texts_i18n import TX, NX, KEYS
for _l, _t in TX.items():
    T[_l] = _t
for _l, _n in NX.items():
    _n["feats"] = [(k,) + f for k, f in zip(KEYS, _n["feats"])]
    N[_l] = _n

CSS = """
/* A calm green field: one big statement, then the app shown screen by screen, alternating sides. */
:root{--bg:#f6f8f4;--paper:#fff;--ink:#17251f;--mut:#56665d;--line:#dfe6df;--brand:#1f5c43;--ac:#2e7d5b;--tint:#e6f2e8;--deep:#163f30;--onDeep:#eef6f0;--onDeepAc:#9fe2bd;--approx:#e07b18;--p:#e05a6b;--c:#d4911f;--f:#3d8fd6;--salt:#7d8b85;
--body:system-ui,-apple-system,"Segoe UI",Roboto,"Noto Sans",Arial,sans-serif}
@media (prefers-color-scheme:dark){:root{--bg:#0f1b17;--paper:#16261f;--ink:#e9f2ec;--mut:#9fb1a6;--line:#25382f;--brand:#7fd3a6;--ac:#57c98c;--tint:#173026;--deep:#0b2a1f;--onDeep:#e3f3e9;color-scheme:dark}}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.6 var(--body)}
img{max-width:100%}
a{color:var(--ac)}
.w,.wrap{max-width:1080px;margin:0 auto;padding-left:max(18px,env(safe-area-inset-left,0px));padding-right:max(18px,env(safe-area-inset-right,0px))}
h1,h2,h3{text-wrap:balance;margin:0}
h2{font-size:clamp(26px,3.6vw,36px);line-height:1.15;font-weight:800;letter-spacing:-.01em}
.eyebrow{font-size:13px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--ac)}
section{padding-block:56px}
header{display:flex;align-items:center;justify-content:space-between;gap:12px;padding-block:18px}
.logo img{height:30px;width:auto;display:block}
@media (prefers-color-scheme:dark){.logo img{filter:brightness(0) invert(1)}}
details.lang{position:relative}
details.lang summary{list-style:none;cursor:pointer;font-size:14px;color:var(--mut);border:1px solid var(--line);border-radius:999px;padding:5px 12px;background:var(--paper)}
details.lang summary::-webkit-details-marker{display:none}
details.lang div{position:absolute;right:0;top:calc(100% + 6px);background:var(--paper);border:1px solid var(--line);border-radius:12px;padding:6px;display:grid;grid-template-columns:1fr 1fr;width:max-content;max-width:calc(100vw - 36px);z-index:5;box-shadow:0 10px 30px rgba(0,0,0,.12)}
details.lang a{padding:6px 10px;border-radius:8px;text-decoration:none;color:var(--ink);font-size:15px}
details.lang a[aria-current]{color:var(--ac);font-weight:700}
details.lang a:hover{background:var(--tint)}
.hero{display:grid;grid-template-columns:1.15fr .85fr;gap:40px;align-items:center;padding-block:28px 48px}
.hero h1{font-size:clamp(36px,6vw,64px);line-height:1.04;font-weight:900;letter-spacing:-.02em;margin-top:12px}
.hero h1 span{color:var(--ac);display:block}
.lead{font-size:clamp(17px,2.1vw,20px);color:var(--mut);max-width:34em;margin:20px 0 26px}
.btns{display:flex;gap:12px;flex-wrap:wrap}
.btn{display:inline-flex;align-items:center;padding:13px 20px;border-radius:12px;font-weight:700;text-decoration:none;font-size:16px}
.btn.pri{background:var(--brand);color:var(--onDeep)}
@media (prefers-color-scheme:dark){.btn.pri{color:#0f1b17}}
.btn.sec{border:1.5px solid var(--ac);color:var(--ac)}
.btn:focus-visible,a:focus-visible,summary:focus-visible{outline:3px solid var(--approx);outline-offset:2px}
.phone{background:var(--paper);border:8px solid #1c2622;border-radius:34px;overflow:hidden;box-shadow:0 18px 40px rgba(20,50,35,.18)}
.phone img{display:block;width:100%;height:auto}
.heroArt{position:relative;justify-self:center;max-width:330px;width:100%}
.label{position:absolute;left:-44px;bottom:30px;background:#fff;color:#111;border:2px solid #111;border-radius:6px;padding:10px 12px;width:200px;font-size:13px;line-height:1.35;box-shadow:0 12px 30px rgba(0,0,0,.2)}
.label b{display:block;font-size:14px;border-bottom:6px solid #111;padding-bottom:4px;margin-bottom:4px}
.label p{display:flex;justify-content:space-between;border-bottom:1px solid #ddd;padding:2px 0;margin:0;font-variant-numeric:tabular-nums}
.label small{display:block;color:#555;margin-top:6px;font-size:12px}
.band{background:var(--deep);color:var(--onDeep)}
.band .w{padding-block:44px;display:grid;gap:10px}
.band .eyebrow{color:var(--onDeepAc)}
.band p{margin:0;font-size:clamp(22px,3.2vw,32px);line-height:1.25;font-weight:700;max-width:28em;text-wrap:balance}
.band em{font-style:normal;color:var(--onDeepAc)}
.feats{display:grid;gap:64px;margin-top:40px}
.feat{display:grid;grid-template-columns:1fr 1fr;gap:48px;align-items:center}
.feat:nth-child(even) .shot{order:2}
.feat .shot{background:var(--tint);border-radius:28px;padding:32px 15% 0;overflow:hidden;max-height:520px}
.feat .phone{border-bottom:0;border-radius:30px 30px 0 0}
.feat h3{font-size:clamp(22px,2.8vw,28px);line-height:1.2;font-weight:800;margin:8px 0 10px}
.feat p{margin:0;color:var(--mut);max-width:32em}
.ai{display:inline-block;margin-top:14px;font-size:15px;font-weight:600;color:var(--brand);background:var(--tint);padding:6px 12px;border-radius:10px}
.approx{color:var(--approx);font-weight:800;font-size:1.3em;line-height:1}
.more{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:28px;margin-top:56px}
.more div{border-top:2px solid var(--ac);padding-top:12px}
.more h3{font-size:19px;margin-bottom:6px}
.more p{margin:0;color:var(--mut);font-size:16px}
.who{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));gap:12px;margin-top:28px}
.who div{background:var(--paper);border:1px solid var(--line);border-radius:16px;padding:18px 20px}
.who small{display:block;font-size:13px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--mut)}
.who q{display:block;font-size:20px;font-weight:700;line-height:1.3;margin-top:6px}
.vid{display:grid;grid-template-columns:auto 1fr;gap:40px;align-items:center}
.vid video{width:280px;max-width:100%;aspect-ratio:9/16;border-radius:22px;background:var(--deep);display:block}
.vid p{color:var(--mut);margin:10px 0 0;max-width:30em}
.tag{display:inline-block;font-size:13px;font-weight:700;color:var(--mut);border:1px solid var(--line);border-radius:999px;padding:2px 10px;margin-top:12px}
.story{background:var(--tint);border-radius:28px;padding:40px clamp(20px,4vw,48px);display:grid;grid-template-columns:auto 1fr;gap:32px;align-items:start}
.story .big{font-weight:900;font-size:clamp(56px,9vw,96px);line-height:.9;color:var(--brand);font-variant-numeric:tabular-nums;white-space:nowrap}
.story .big small{display:block;font-size:18px;font-weight:700;color:var(--mut);margin-top:8px}
.story p{margin:12px 0 0;max-width:36em}
.story .disc{font-size:15px;color:var(--mut)}
.two{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.two>div,.card{background:var(--paper);border:1px solid var(--line);border-radius:18px;padding:24px}
.two h3,.card h3{font-size:21px;margin-bottom:8px}
.two p,.card p{margin:0 0 8px;color:var(--mut)}
.faq{max-width:780px;margin-top:20px}
.faq details{border-bottom:1px solid var(--line);padding-block:14px}
.faq summary{cursor:pointer;font-weight:700;font-size:18px;list-style:none;display:flex;justify-content:space-between;gap:16px}
.faq summary::-webkit-details-marker{display:none}
.faq summary::after{content:"+";color:var(--ac);font-weight:800}
.faq details[open] summary::after{content:"–"}
.faq details p{color:var(--mut);margin:8px 0 0;max-width:42em}
footer{margin-top:40px;padding-block:28px 44px;border-top:1px solid var(--line);font-size:15px;color:var(--mut)}
footer .links{display:flex;gap:18px;flex-wrap:wrap;margin-bottom:10px}
footer p{margin:0 0 10px;max-width:48em;font-size:14px}
/* first, simple page (languages without the new texts yet) */
.hero1{background:var(--tint);border-radius:24px;padding:48px 28px;display:grid;grid-template-columns:1fr auto;gap:32px;align-items:center}
.hero1 img.icon{width:150px;height:150px;border-radius:34px;box-shadow:0 10px 30px rgba(0,0,0,.15)}
.hero1 h1{font-size:clamp(30px,5vw,46px);line-height:1.15;margin:0 0 14px}
.shots{display:flex;gap:14px;overflow-x:auto;scroll-snap-type:x mandatory;padding-bottom:10px}
.shots img{width:220px;height:auto;flex:0 0 auto;border-radius:16px;scroll-snap-align:start;border:1px solid var(--line)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,280px),1fr));gap:16px}
.h2{margin:56px 0 18px}
.small{font-size:15px;color:var(--mut)}
.legal{max-width:760px}
.legal .note{background:var(--tint);border-radius:12px;padding:12px 16px;font-size:15px}
.legal ul{color:var(--mut)}
@media (max-width:760px){
.hero,.feat,.vid,.story,.two,.hero1{grid-template-columns:1fr}
.feat{gap:24px}.feat:nth-child(even) .shot{order:0}
.heroArt{max-width:270px}.label{left:-14px;width:165px;font-size:12px}
.more{grid-template-columns:1fr}
.vid video{width:240px;margin:0 auto}
section{padding-block:40px}
.hero1{padding:32px 20px}.hero1 img.icon{width:96px;height:96px;border-radius:22px;order:-1}.shots img{width:62vw}}
@media (prefers-reduced-motion:no-preference){.btn{transition:transform .15s}.btn:hover{transform:translateY(-1px)}}
"""


def page(lang, path_depth, title, desc, body, canonical):
    up = "../" * path_depth
    t = T[lang]
    alt = "".join(f'<link rel="alternate" hreflang="{l}" href="https://macrolia.app/{c["dir"]}">' for l, c in LANGS.items()) if canonical == LANGS[lang]["dir"] else ""
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="https://macrolia.app/{canonical}">
{alt}
<link rel="icon" type="image/png" href="{up}img/icon-192.png">
<link rel="apple-touch-icon" href="{up}img/icon-192.png">
<meta name="theme-color" content="#1f5c43">
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
<p>{t['disclaimer']}</p>
<div>© 2026 Macrolia · Uplift in Life</div>
</footer>
</div>
</body>
</html>
"""


def header(lang, depth, sub=""):
    up = "../" * depth
    links = "".join(
        f'<a href="{up}{LANGS[l]["dir"]}{sub}"{" aria-current=\"page\"" if l == lang else ""} hreflang="{l}" lang="{l}">{LANGS[l]["name"]}</a>'
        for l in LANGS)
    return (f'<header><a class="logo" href="{up}{LANGS[lang]["dir"]}"><img src="{up}img/logo.png" alt="Macrolia" width="152" height="30"></a>'
            f'<details class="lang"><summary>{LANGS[lang]["name"]} ▾</summary><div>{links}</div></details></header>')


def phone(src, alt, w=600, h=1154, lazy=True):
    return f'<div class="phone"><img src="{src}" alt="{html.escape(alt)}" width="{w}" height="{h}"{" loading=\"lazy\"" if lazy else ""}></div>'


def home_new(lang):
    n, t = N[lang], T[lang]
    depth = 1 if LANGS[lang]["dir"] else 0
    up = "../" * depth
    sh = f"{up}img/{lang}/"
    lab = "".join(f"<p><span>{a}</span><span>{b}</span></p>" for a, b in n["label"]["rows"])
    feats = ""
    for key, eb, h, p, ai in n["feats"]:
        p = p.replace("≈", '<span class="approx">≈</span>')
        extra = f'<span class="ai">{ai}</span>' if ai else ""
        feats += f'<div class="feat"><div class="shot">{phone(sh + key + ".webp", n["alts"][key])}</div><div><div class="eyebrow">{eb}</div><h3>{h}</h3><p>{p}</p>{extra}</div></div>\n'
    more = "".join(f"<div><h3>{h}</h3><p>{p}</p></div>" for h, p in n["more"])
    who = "".join(f"<div><small>{a}</small><q>{b}</q></div>" for a, b in n["groups"])
    faq = "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in n["faq"])
    video_btn = f'<a class="btn sec" href="#video">{n["video_btn"]}</a>' if JANUARY else ""
    january = ""
    if JANUARY:
        january = f"""<section id="video" style="padding-top:0"><div class="vid">
<video src="{up}video/sled-bebeto-{lang}.mp4" poster="{up}video/sled-bebeto-{lang}.jpg" controls muted playsinline preload="none"></video>
<div><div class="eyebrow">{n['video']}</div><h2 style="margin-top:8px">{n['video_h']}</h2><p>{n['video_p']}</p><span class="tag">{n['video_tag']}</span></div>
</div></section>
<section style="padding-top:0"><div class="story">
<div class="big">{n['story_big']}<small>{n['story_small']}</small></div>
<div><div class="eyebrow">{n['story']}</div><p>{n['story_p']}</p><p class="disc">{n['story_disc']}</p></div>
</div></section>
"""
    body = f"""{header(lang, depth)}
<section class="hero">
<div>
<div class="eyebrow">{n['soon']}</div>
<h1>{n['h1a']}<span>{n['h1b']}</span></h1>
<p class="lead">{n['lead']}</p>
<div class="btns"><a class="btn pri" href="#how">{n['how_btn']}</a>{video_btn}</div>
</div>
<div class="heroArt">{phone(sh + "day.webp", n["hero_alt"], lazy=False)}
<div class="label" aria-hidden="true"><b>{n['label']['t']}</b>{lab}<small>{n['label']['note']}</small></div></div>
</section>
</div>
<section class="band"><div class="w">
<div class="eyebrow">{n['why']}</div>
<p>{n['yoyo_a']} <em>{n['yoyo_b']}</em></p>
</div></section>
<div class="wrap">
<main>
<section id="how">
<div class="eyebrow">{n['how']}</div>
<h2 style="margin-top:8px">{n['how_h']}</h2>
<div class="feats">
{feats}</div>
<div class="more">{more}</div>
</section>
<section style="padding-top:0">
<div class="eyebrow">{n['who']}</div>
<h2 style="margin-top:8px">{n['who_h']}</h2>
<div class="who">{who}</div>
</section>
{january}<section style="padding-top:0"><div class="two">
<div><h3>{n['data_h']}</h3><p>{n['data']}</p></div>
<div><h3>{n['sub_h']}</h3><p>{n['sub']}</p><p>{n['langs']}</p></div>
</div></section>
<section style="padding-top:0">
<h2>{n['faq_h']}</h2>
<div class="faq">{faq}</div>
</section>
</main>"""
    return page(lang, depth, t["title"], t["desc"], body, LANGS[lang]["dir"])


def home(lang):
    t = T[lang]
    depth = 1 if LANGS[lang]["dir"] else 0
    up = "../" * depth
    shots = "".join(f'<img src="{up}img/{lang}/{n}.webp" alt="" loading="lazy" width="540" height="960">' for n in range(1, 9))
    feats = "".join(f'<div class="card"><h3>{h}</h3><p>{p}</p></div>' for h, p in t["feats"])
    body = f"""{header(lang, depth)}
<main>
<section class="hero1">
<div>
<h1>{t['desc']}</h1>
<p class="lead">{t['lead']}</p>
<div class="btns"><span class="btn pri">{t['soon']}</span><a class="btn sec" href="mailto:{EMAIL}">{t['contact']}</a></div>
</div>
<img class="icon" src="{up}img/icon-512.png" alt="" width="150" height="150">
</section>
<h2 class="h2">{t['shots']}</h2>
<div class="shots">{shots}</div>
<h2 class="h2">{t['why']}</h2>
<div class="grid">{feats}</div>
<div class="grid" style="margin-top:16px">
<div class="card"><h3>{t['data_h']}</h3><p>{t['data']}</p></div>
<div class="card"><h3>{t['sub_h']}</h3><p>{t['sub']}</p><p style="margin-top:8px">{t['langs']}</p></div>
</div>
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
        if lang in N:
            # app screens rendered from the app's preview (assets/shots/<lang>/, see README)
            for f in sorted(os.listdir(os.path.join(ASSETS, "shots", lang))):
                shutil.copy(os.path.join(ASSETS, "shots", lang, f), os.path.join(OUT, "img", lang, f))
            if JANUARY:
                os.makedirs(os.path.join(OUT, "video"), exist_ok=True)
                for ext in ("mp4", "jpg"):
                    shutil.copy(os.path.join(ASSETS, "video", f"sled-bebeto-{lang}.{ext}"), os.path.join(OUT, "video"))
            write(c["dir"] + "index.html", home_new(lang))
        else:
            for n in range(1, 9):
                im = Image.open(os.path.join(src, "phoneScreenshots", f"{n}.png")).convert("RGB")
                im.resize((540, 960), Image.LANCZOS).save(os.path.join(OUT, f"img/{lang}/{n}.webp"), quality=82)
            write(c["dir"] + "index.html", home(lang))
        Image.open(os.path.join(src, "featureGraphic.png")).convert("RGB").save(os.path.join(OUT, f"img/og-{lang}.png"), optimize=True)
        for kind in ("privacy", "terms"):
            write(c["dir"] + kind + "/index.html", legal(lang, kind, policy))
    write("style.css", CSS.strip() + "\n")
    t = T["en"]
    nf = page("en", 0, "Macrolia", t["desc"], header("en", 0) + f'<main><h1>404</h1><p>{t["nf"]}</p><p><a href="/">{t["back"]}</a></p></main>', "").replace('href="img', 'href="/img').replace('href="style', 'href="/style').replace('src="img', 'src="/img')
    write("404.html", re.sub(r'href="([a-z]{2})/', r'href="/\1/', nf))
    write("CNAME", "macrolia.app\n")
    write(".nojekyll", "")
    write("robots.txt", "User-agent: *\nAllow: /\n")


if __name__ == "__main__":
    main()
