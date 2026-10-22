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

Printed artwork has a satin ink finish with a subtle parallel microgroove normal map and mild anisotropy. The same finish covers the separate PS2 branding band. Use **Printed artwork → Print texture** to turn this finish on or off. The setting is remembered for each console during the session and included in edited GLB exports. Artwork pixels remain unchanged; the surface maps stay embedded in textured GLB exports. At normal viewing distances, mip filtering smooths the microscopic grooves.

Install Python dependencies with `python -m pip install -r requirements.txt` before rebuilding. Run `npm test` for the interaction, geometry and material checks. Font rendering uses Windows fonts. No dependency installation is required to open the generated studio.

The viewer's office surroundings and other environments affect lighting, but are not embedded in exported GLBs. Rainbow effects approximate optical-disc diffraction. Reference artwork and supplied branding remain third-party assets. The optional Blender setup is included in `outputs/create-blender-scene.py` and has not been run in Blender here.
