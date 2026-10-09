# Maison Calme — Type A 3 BHK interior (1750 sft, east facing)

Interactive 3D interior design of the Type-A floor plan in a calm French-luxury style.

- `index.html` — the 3D walkthrough (three.js). Pick a room, drag to look around, W A S D / scroll to walk, and use **Render photo** for a path-traced realistic image.
- `tex/` — textures used by the web model.
- `blender/` — Blender (Cycles) scene for the Bedroom 2 giraffe room: `kids_giraffe.py`, the `.blend` file, textures and finished renders in `blender/renders/`.

Run locally: `python3 -m http.server 5173` in this folder, then open http://localhost:5173.

Deploy: GitHub Pages → Settings → Pages → Deploy from branch `main`, folder `/ (root)`.

Wood floor texture and sky HDRI from Poly Haven (CC0).
