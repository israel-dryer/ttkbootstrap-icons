# Third-Party Notices

`tkinter-icons` is a renderer. It ships no glyphs of its own — every icon comes from an upstream icon font redistributed by one of the sixteen icon packs, each installed as an extra:

```
pip install "tkinter-icons[material]"
```

Each pack carries its upstream license file under `LICENSES/` inside the installed package, so the terms travel with the font rather than only with this file.

Your use of the glyphs is governed by the upstream license listed below. The wrapper code in this repository — the renderer, the browser, the packs' own Python — is MIT, and each distribution declares `license = "MIT"` to describe that code; the SPDX declaration is not a claim about the font it carries.

## Icon packs

| Extra | Distribution | Upstream set | Upstream license | Files under `LICENSES/` |
|---|---|---|---|---|
| `bootstrap` | `tkinter-icons-bs` | [Bootstrap Icons](https://icons.getbootstrap.com/) | MIT | `MIT.txt` |
| `devicon` | `tkinter-icons-devicon` | [Devicon](https://devicon.dev/) | MIT | `DEVICON-LICENSE.txt` |
| `eva` | `tkinter-icons-eva` | [Eva Icons](https://akveo.github.io/eva-icons/) | MIT | `EVA-LICENSE.txt` |
| `fluent` | `tkinter-icons-fluent` | [Fluent System Icons](https://github.com/microsoft/fluentui-system-icons) | MIT | `MIT.txt` |
| `fluent-regular` | `tkinter-icons-fluent-reg` | [Fluent System Icons](https://github.com/microsoft/fluentui-system-icons) (regular only) | MIT | `MIT.txt` |
| `fontawesome` | `tkinter-icons-fa` | [Font Awesome 6 Free](https://fontawesome.com/v6/icons) | SIL OFL 1.1 (fonts), MIT (code), CC BY 4.0 (icons) | `OFL-1.1.txt`, `MIT.txt`, `CC-BY-4.0.txt` |
| `google-material` | `tkinter-icons-gmi` | [Google Material Icons](https://github.com/marella/material-design-icons) | Apache 2.0 | `Apache-2.0.txt` |
| `ionicons` | `tkinter-icons-ion` | [Ionicons v2](https://github.com/ionic-team/ionicons) | MIT | `MIT.txt` |
| `lucide` | `tkinter-icons-lucide` | [Lucide](https://lucide.dev/icons/) | ISC | `ISC.txt` |
| `material` | `tkinter-icons-mat` | [Material Design Icons](https://pictogrammers.com/library/mdi/) | Apache 2.0 | `Apache-2.0.txt` |
| `meteocons` | `tkinter-icons-meteocons` | [Meteocons](https://bas.dev/work/meteocons) | MIT | `MIT.txt` |
| `remix` | `tkinter-icons-remix` | [Remix Icon](https://remixicon.com/) | Apache 2.0 | `Apache-2.0.txt` |
| `rpg-awesome` | `tkinter-icons-rpga` | [RPG Awesome](https://nagoshiashumari.github.io/Rpg-Awesome/) | MIT | `RPGA-LICENSE.txt` |
| `simple` | `tkinter-icons-simple` | [Simple Icons](https://simpleicons.org/) | CC0 1.0 (icon set), MIT (font project) | `CC0-1.0.txt`, `MIT.txt` |
| `typicons` | `tkinter-icons-typicons` | [Typicons](https://www.s-ings.com/typicons/) | SIL OFL 1.1 (font), CC BY-SA 4.0 (artwork) | `OFL-1.1.txt`, `CC-BY-SA-4.0.txt` |
| `weather` | `tkinter-icons-weather` | [Weather Icons](https://erikflowers.github.io/weather-icons/) | SIL OFL 1.1 (font), MIT (code), CC BY 3.0 (documentation) | `OFL-1.1.txt`, `MIT.txt`, `CC-BY-3.0.txt` |

Two of these carry more than one license because upstream splits them that way. Typicons licenses the font under the OFL and the artwork under CC BY-SA — a share-alike term, so adapting the *artwork* carries obligations that using the rendered glyphs does not. Font Awesome and Weather Icons likewise separate font, code, and documentation.

## Attribution

Some upstream licenses require attribution in software that redistributes the glyphs — CC BY 4.0 (Font Awesome icons), CC BY 3.0 (Weather Icons documentation), and CC BY-SA 4.0 (Typicons artwork) all do. Shipping the pack satisfies this for the copies of the license text, but an application that displays a credits or about screen should name the icon set it draws from.

## Known gap

Five packs carry a file that *describes* the upstream license and links to its canonical text rather than reproducing it: `gmi`, `mat`, and `remix` (Apache 2.0), `simple` (CC0 1.0), and `lucide` (ISC). Three more — `devicon`, `eva`, and `rpga` — carry the full MIT text under a generic copyright line rather than upstream's own. Apache 2.0 in particular requires that recipients be given a copy of the license, which a link does not satisfy. This is tracked as a follow-up; the canonical text for each is reachable from the pack's `license_url`, which the icon browser links from every provider.

---

If an upstream license or attribution here is missing or wrong, please open an issue with the reference.