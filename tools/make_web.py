#!/usr/bin/env python3
"""Generates docs/index.html — the installable web version — from the Android page.

The only differences are the Apple/Web-App head tags, the launch images and the
service worker registration. Keeping this in one place means the two builds can
never drift apart.
"""

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SOURCE = ROOT / "android" / "assets" / "index.html"
TARGET = ROOT / "docs" / "index.html"

SPLASH = [
    ("1290x2796", "430px", "932px", 3),
    ("1179x2556", "393px", "852px", 3),
    ("1170x2532", "390px", "844px", 3),
    ("1284x2778", "428px", "926px", 3),
    ("1242x2688", "414px", "896px", 3),
    ("1125x2436", "375px", "812px", 3),
    ("828x1792", "414px", "896px", 2),
    ("750x1334", "375px", "667px", 2),
]

HEAD = """<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Habits">
<meta name="description" content="A private, offline habit tracker with streaks, statistics and a calendar.">
<link rel="manifest" href="manifest.json">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
"""

SW = """if("serviceWorker" in navigator && location.protocol.startsWith("http")){
  navigator.serviceWorker.register("sw.js").then(registration => {
    if(registration.waiting) toast("An update is ready — reopen the app");
    registration.addEventListener("updatefound", () => {
      const fresh = registration.installing;
      if(!fresh) return;
      fresh.addEventListener("statechange", () => {
        if(fresh.state === "installed" && navigator.serviceWorker.controller){
          toast("An update is ready — reopen the app");
        }
      });
    });
  }).catch(() => {});
}
"""


def main() -> None:
    html = SOURCE.read_text(encoding="utf-8")

    splash_tags = "\n".join(
        f'<link rel="apple-touch-startup-image" href="splash-{name}.png" '
        f'media="(device-width: {w}) and (device-height: {h}) and '
        f'(-webkit-device-pixel-ratio: {ratio})">'
        for name, w, h, ratio in SPLASH
    )

    html = html.replace(
        '<meta name="theme-color" content="#070d18">',
        '<meta name="theme-color" content="#070d18">\n' + HEAD + splash_tags,
        1,
    )

    html = html.replace(
        'document.addEventListener("visibilitychange", () => {',
        SW + 'document.addEventListener("visibilitychange", () => {',
        1,
    )

    if "serviceWorker" not in html:
        raise SystemExit("service worker registration was not inserted")

    TARGET.write_text(html, encoding="utf-8")
    print(f"wrote {TARGET.relative_to(ROOT)} ({len(html)} chars)")


if __name__ == "__main__":
    main()
