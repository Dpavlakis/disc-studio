# PS2 Disc Studio

Editable upright optical disc models in blue, silver, gold, and near-black finishes, with replaceable label artwork, etched branding, a geometric barcode, clear hubs and rims, and a separate PS2 label band.

## Use the preview

Open `outputs/disc-preview.html` in a browser. It embeds the five models and needs internet to load the model-viewer library.

Use the **PS1**, **PS2**, and **Xbox 360** sections to browse their disc models. Artwork selections are kept separately for each system during the browser session. Xbox 360 uses the supplied Xbox SVG and X360 by Redge font for its holographic center ring, with its own artwork boundary and no PS2 label band. The supplied underside photographs guide its reversed holographic ring, chrome lip, dark mastering band and two geometric barcode rows. The barcode spacing is representative rather than an exact pressing ID. A varying thin-film thickness produces light-dependent color shifts; it is an artistic approximation of the reference hologram.

- Choose a disc finish and upload a square image under **Top artwork**.
- **Show artwork** hides or restores the print and PS2 band. With the print hidden, underside branding can be seen mirrored from the opposite side.
- **Front view** and **Back view** frame the disc straight on.
- **Download PNG** captures the current view with transparency.
- **Download edited GLB** exports the customized 3D model.
- The expanded viewer supports **Full screen**, **Fit disc**, and zoom buttons/a slider up to 12×.
- **Lights** selects the original studio environment or 1–4 HDR softboxes; **Brightness** adjusts their overall exposure. PNG exports include the chosen lighting. GLB exports preserve model materials; lighting is a viewer setting.

The preview uses 2× supersampling and maintains full rendering resolution. Appearance depends on the browser, GPU and lighting. The underside's rainbow response is an artistic approximation of optical disc diffraction.

The Xbox 360 clear hub includes the user-confirmed **IFPI KKA0** molded code as surface relief, without opaque lettering. Its center wordmarks have faint outline treatment; the hologram uses neutral base colors and thin-film response rather than a painted rainbow.

The Xbox mastering band has independently patterned outer and inner barcode tracks plus a shorter middle group, based on the supplied close-ups. These are geometric reflective marks, not duplicated rows or a functional machine-readable disc ID.

## Files

- `outputs/*.glb`: portable models with embedded textures; units are meters, 120 mm disc diameter and 15 mm center hole.
- `outputs/branding-source/`: original supplied SVG branding assets.
- `outputs/*.png`: textures and detail preview.
- `outputs/create-blender-scene.py`: optional Blender 4.x setup; run from Blender's Scripting workspace with the other output files alongside it. This setup has been syntax checked but not run in Blender.
- `work/build_disc.py`, `work/make_hub.py`: model and texture builders.
- `work/render_logos.cjs`: renders the supplied SVGs into working texture assets.
- `work/barcode-runs.json`: barcode spacing measured from the supplied reference.
- `work/package.py`: builds the standalone preview, validates the GLB structure and creates a ZIP locally.

## Rebuild

Install Python with NumPy and Pillow. Rendering the label fonts currently requires Windows fonts: Arial, OCR-A Extended and Times New Roman, under `C:/Windows/Fonts`. Existing generated models and the preview can be used without these dependencies.

```sh
python -m pip install -r requirements.txt
npm install
npm run logos
npm run build
```

The small logo PNGs are already included, so the Node step is optional unless the source SVGs change. The Xbox font is stored in `outputs/branding-source/X360.ttf` and loaded directly without installing it. The ZIP is generated locally and excluded from Git because its contents are already tracked.

Supplied PlayStation logos remain third-party assets; no ownership or redistribution license is asserted for them. Personal game-art samples are excluded from the repository.

## Clean a matching disc-art library

`work/clean_disc_library.py` supports the uniform 1280×1280 template used in the supplied library. It removes the pictured hub and perimeter, aligns the printed annulus with bilinear radial resampling, and preserves source lettering without generation or OCR. Original bottom bands stay beneath the model's separate branding overlay. Cleaned files carry a version marker to prevent repeated remapping.

First create samples, then apply only to a backed-up library. `--apply` overwrites PNGs recursively in the selected `Disc` folder, with per-file checks and a CSV report:

```sh
python work/clean_disc_library.py --source "C:/path/to/Disc" --report outputs/disc-cleanup-report.csv --samples work/cleanup-samples
python work/clean_disc_library.py --source "C:/path/to/Disc" --report outputs/disc-cleanup-report.csv --apply
```
