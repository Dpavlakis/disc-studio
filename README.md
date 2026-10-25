# Disc Studio

Run the rebuild command below, then open **Open Studio.html**. First use needs internet for the 3D viewer library.

The generated studio page exceeds GitHub's per-file repository limit and is excluded from source control. `npm run build` creates it and a ready-to-use `outputs/optical-disc-pack.zip` alongside the model-only export.

The studio includes PlayStation, PlayStation 2, PlayStation 3, PlayStation 4, original Xbox, Xbox 360 and GameCube discs. Upload artwork, adjust its rotation and coverage, choose lighting, and export an edited GLB or transparent PNG. GameCube branding has separate seal, rating, panel colour and four-character game-code controls.

Left-drag orbits the view, middle-drag rotates the disc itself, right-drag pans, and the wheel zooms.

## Project folders

- `outputs/studio.html`: current self-contained studio; older generated page copies were removed.
- `outputs/*.glb`: current disc models, with embedded textures. Units are metres; full-size discs are 120 mm, GameCube is 80 mm, centre holes are 15 mm.
- `outputs/*.png`: working model textures.
- `outputs/previews/`: design studies and comparison renders, including the unapplied GameCube construction draft.
- `outputs/branding-source/`: supplied logos, fonts and editable branding masks.
- `outputs/artwork-samples/`: retained test artwork.
- `outputs/lighting/`: HDR environments and source credits.
- `work/`: source, checks, model builders, retained local dependencies and cleanup samples.

## Rebuild the studio

Run `python work/package.py` or `npm run build`. This packages the current models without regenerating their geometry. `python work/export_latest.py` refreshes the model-only ZIP. Older model builders are retained for reference and are not part of the packaging command.


Install Python dependencies with `python -m pip install -r requirements.txt` before rebuilding. Run `npm test` for the interaction, geometry and material checks. Font rendering uses Windows fonts. No dependency installation is required to open the generated studio.

The viewer's office surroundings and other environments affect lighting, but are not embedded in exported GLBs. Rainbow effects approximate optical-disc diffraction. Reference artwork and supplied branding remain third-party assets. The optional Blender setup is included in `outputs/create-blender-scene.py` and has not been run in Blender here.

The PS1 centre hub and moulded centre rings use 40% optical transmission; the black data area remains opaque.

The studio starts with the approved platform-specific placeholder covers for all seven systems. Uploading your own image replaces the placeholder. The approved covers are also embedded in the models so the old placeholders cannot flash during loading. Cover replacement preserves the disc geometry and optical finish.

Original Xbox has an additional **Disc-matched security** finish: the X, Xbox and genuine lettering, outer security dashes and serial text use the same reflective data material as the disc. The geometric background lines and checkerboard squares use a separate faint silver finish at 20% opacity so they only subtly catch the light. The original Xbox model remains a separate option.

Xbox 360 also offers a separate **Disc-matched security** finish, with disc-textured Xbox logos, XBOX 360 lettering, security dashes and serial text over a faint 20%-opacity version of its original circular swirl pattern. The existing Xbox 360 finishes remain available.

The approved disc-matched Xbox finishes are selected by default. Disc Studio remembers your finish choices when browser storage is available. The Xbox 360 starter cover uses the supplied Xbox 360 wordmark.

Artwork and separate branding visibility are independent: you can display either layer alone, both, or neither. This applies to GameCube branding and the separate PS2 label band.

GameCube security dashes and ring text match the disc data material on both sides. The moulded clear hub lettering retains its plastic finish.

Starter covers are generated from editable SVG layouts and rendered to 4096px with supersampled antialiasing. The Original Xbox accent follows the lower rim, and the GameCube placeholder text sits above the centre hub so the lower branding panel cannot cover it.
