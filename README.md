# macrolia.app

Static website for the Macrolia app, served by GitHub Pages from `docs/` on `main`.

Rebuild after changing texts or images (needs Python 3 + Pillow):

    python3 build.py <play-listing dir> <brand dir> data/policy_bg.json

`data/policy_bg.json` is the `policy` object from the app's `bg.json` strings (Privacy Policy and Terms of Use).
