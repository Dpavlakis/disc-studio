# PS2 Disc Studio

Editable upright optical disc models in blue, silver, gold, and near-black finishes, with replaceable label artwork, etched branding, a geometric barcode, clear hubs and rims, and a separate PS2 label band.

## Use the preview

Open `outputs/disc-preview.html` in a browser. It embeds the four models and needs internet to load the model-viewer library.

- Choose a disc finish and upload a square image under **Top artwork**.
- **Show artwork** hides or restores the print and PS2 band. With the print hidden, underside branding can be seen mirrored from the opposite side.
- **Front view** and **Back view** frame the disc straight on.
- **Download PNG** captures the current view with transparency.
- **Download edited GLB** exports the customized 3D model.
- The expanded viewer supports **Full screen**, **Fit disc**, and zoom buttons/a slider up to 12×.
- **Lights** selects the original studio environment or 1–4 HDR softboxes; **Brightness** adjusts their overall exposure. PNG exports include the chosen lighting. GLB exports preserve model materials; lighting is a viewer setting.

The preview uses 2× supersampling and maintains full rendering resolution. Appearance depends on the browser, GPU and lighting. The underside's rainbow response is an artistic approximation of optical disc diffraction.

## Files

- `outputs/*.glb`: portable models with embedded textures; units are meters, 120 mm disc diameter and 15 mm center hole.
- `outputs/branding-source/`: original supplied SVG branding assets.
- `outputs/*.png`: textures, detail preview and example 007 artwork.
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

The small logo PNGs are already included, so the Node step is optional unless the source SVGs change. The ZIP is generated locally and excluded from Git because its contents are already tracked.

The 007 samples were cleaned and extended with image generation; small lettering may differ from the original source. Supplied PlayStation logos and game artwork remain third-party assets; no ownership or redistribution license is asserted for them.
