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
| `assets/img/themes/<pack>-{360,540,1080}.webp`, `<pack>-bigplay-1080.webp`, `neon-coast-bigplay-360.webp`, `neon-coast-win-360.webp`, and `assets/media/theme-<pack>.jpg`, for the eight Theme Packs | screen captures of the released build 2.5.0 (58), `themes/stills/<pack>.png`, `<pack>-bigplay.png` and `neon-coast-win.png` in the footage folder (its `themes/INDEX.md` describes each) | The game's own screens on each table. The emulator's status bar and camera cut-out (top 100 rows) and navigation handle (bottom 48 rows) are cropped away; nothing in the picture is altered. Made by `tools/build_themes.py`. |
| `assets/img/decks/{champions-deck,heirloom,afterglow,deco-sunburst,crown-jewels}-640.webp` | frames of `themes/collection-3.mp4` (sha256 `f29e6006…230e3723`) at 45, 53, 59.5, 64.5 and 69.5 s | The game's Collection preview banner, showing each card deck on Neon Coast. Cropped to the banner; nothing altered. |
| `assets/video/neon-coast.mp4`, `neon-coast-poster.webp` | `themes/neon-coast-4.mp4` (sha256 `4997a248…a59e4427`) 1.6–6.0 s and `themes/neon-coast-6.mp4` (sha256 `3025ee25…f2d8b933`) 2.2–6.1 s | Real play on Neon Coast: a deal, then the last card played and the 1st-place medal. Bars cropped, a dip to the table's dark blue at each end; passes `tools/video_check.py`. |
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
