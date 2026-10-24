# macrolia.app

Static website for the Macrolia app, served by GitHub Pages from `docs/` on `main`.

Rebuild after changing texts or images (needs Python 3 + Pillow):

    python3 build.py <play-listing dir> <brand dir> data/policy_bg.json

`data/policy_bg.json` is the `policy` object from the app's `bg.json` strings (Privacy Policy and Terms of Use).

The new home page (languages in `N` in build.py) uses app screens from `assets/shots/<lang>/`,
rendered with the app's preview (`./gradlew --offline -p preview shots --args=site`, local "site-*"
scenes) and cropped to 600×1154 WebP. `JANUARY = False` keeps the founder story and the videos
(`assets/video/`) out of the published site until the company exists (January 2027).
