# Credits and provenance

Everything this site serves is its own file: no outside font, script, image or
video. Every picture comes from the Tres – Pusoy Dos game repository, read at
`origin/main` commit `ed8aff989c071f1294d8da9efdebec35829eb9ae`, whose
`assets/CREDITS.md` is the record of who made each source and on what terms.
The scripts in `tools/` derive the served files from those sources.

| Served file | Source | What it is, and whose |
|---|---|---|
| `assets/fonts/space-grotesk-400.woff2`, `space-grotesk-700.woff2` | game repo `assets/fonts/SpaceGrotesk-{Regular,Bold}.ttf` | Space Grotesk, © 2020 The Space Grotesk Project Authors, SIL Open Font License 1.1 (`assets/fonts/OFL-SpaceGrotesk.txt`, kept beside it). Subset to the Latin this site sets, as WOFF2, by `tools/build_fonts.py`. |
| `assets/fonts/spectral-400.woff2` | game repo `assets/fonts/Spectral-Regular.ttf` | Spectral, © 2017 The Spectral Project Authors, SIL Open Font License 1.1 (`assets/fonts/OFL-Spectral.txt`, kept beside it). Subset as above. |
| `favicon.ico`, `apple-touch-icon.png`, `assets/img/icon-{96,256}.webp`, `assets/img/icon-192.png`, `assets/media/tres-icon-512.png` | game repo `assets/brand/tres-play-icon-512.png` | The app icon: the project owner's own rendered art of the three of clubs, as the stores show it. Resized by `tools/build_images.py`. |
| `assets/media/tres-icon-1024.png` | game repo `assets/brand/tres-store-icon-source.png` | The same art at 1024 px, from the owner's source render, for the media kit. |
| `assets/media/tres-feature-graphic-1024x500.png` and its `-preview.webp` | game repo `assets/graphic/tres-feature-graphic-1024x500.png`, served byte for byte | The Google Play feature graphic, derived in the game repo from the owner's own rendered art. |
| `assets/media/{01-solo-gameplay,03-four-table-themes,05-cosmetic-theme-shop,06-milestones-and-tokens,07-full-game-result}.jpg` and their `-preview.webp` | game repo `assets/screenshots/`, served byte for byte | The Google Play phone screenshots: layouts made in the game repo around the app's own screens. Numbers 02, 04 and 08 show a room code or QR code and are deliberately not published here. |
| `assets/img/themes/{first-light,perlas,violet-hour,manila-bay}.webp` | game repo `assets/screenshots/03-four-table-themes.jpg` | The four table tiles of the Play store screenshot "Table themes": the app's own screens, as the game repository's credits record. Cut along each tile's frame by `tools/build_images.py`. |
| `assets/img/courts/first-light-king-red.webp` | game repo `assets/cards/first-light/court-king-red.png` | First Light's king: a project-owned vector redraw of an owner-ratified court sheet. |
| `assets/img/courts/violet-hour-king-black.webp`, `manila-bay-queen-red.webp` | game repo `assets/cards/violet-hour/court-king-black.png`, `assets/cards/manila-bay/court-queen-red.png` | Court plates of the Violet Hour and Manila Bay decks: project-owned output, generated with Claude Design under the owner's art direction. |
| `assets/img/courts/evergrove-king-red.webp`, `neon-coast-queen-red.webp` | game repo `assets/cards/evergrove/court-king-red.png`, `assets/cards/neon-coast/court-queen-red.png` | Court plates of the Evergrove and Neon Coast decks: drawn by code in the game repository, project-owned. |
| `assets/video/gameplay.mp4`, `gameplay-poster.webp` | screen recordings of the released build 2.5.0 (58), `take28.mp4` (sha256 `42bb67f7…7550c62c`) and `take19.mp4` (sha256 `4fc10a88…adfb52096`) | Real play, solo against three AI opponents. Cut by `tools/build_video.sh`: the phone's status and gesture bars cropped, the holds before PLAY shortened, a dip to the felt colour between the two games. The game's picture is not altered. |
| `assets/img/share*.jpg` (one per page) | `tools/share-card.html` | The link-preview pictures, drawn for this site from the fonts above and the game's suit shapes. Rendered by `tools/build_share.sh`. |

The cards drawn on the pages themselves are HTML and SVG written for this site.
Their suit marks are the game's own shapes (`suitUnitPath` in the game's
`mobile/app/lib/table/card_face.dart`), restated as SVG paths. The colours are
the game's First Light palette (`mobile/app/lib/theme/palette.dart`).

Google Play and Android are trademarks of Google LLC. iPhone, iPad and Game
Center are trademarks of Apple Inc. App Store is a service mark of Apple Inc.
The store buttons are this site's own design; no store badge artwork is used.

The Facebook "f" mark and the Instagram glyph, trademarks of Meta Platforms,
Inc., are drawn as inline SVG in their standard shapes, in one flat colour,
only to link to the game's own pages (facebook.com/trespusoydos and
instagram.com/trespusoydos). Nothing is loaded from either company: no
script, pixel, embed or image.
