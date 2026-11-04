"""Build an offline Demo2 index.html with its original image assets embedded."""

import base64
import json
import mimetypes
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"


def script_safe(source):
    return source.replace("</script", "<\\/script")


def main():
    images = {}
    for path in sorted(ASSETS.rglob("*")):
        if not path.is_file():
            continue
        mime = mimetypes.guess_type(path.name)[0]
        if not mime or not mime.startswith("image/"):
            continue
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        images[f"assets/{path.relative_to(ASSETS).as_posix()}"] = f"data:{mime};base64,{encoded}"

    css = (ROOT / "styles.css").read_text(encoding="utf-8")
    app = (ROOT / "app.js").read_text(encoding="utf-8")
    account = (ROOT / "account-pages.js").read_text(encoding="utf-8")
    asset_map = json.dumps(images, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    hydrate = """
const embeddedAssets = ASSET_DATA;
function hydrateAssets() {
  document.querySelectorAll('img[src^="assets/"]').forEach(image => {
    const embedded = embeddedAssets[image.getAttribute('src')];
    if (embedded) image.src = embedded;
  });
}
hydrateAssets();
const renderWithAssets = render;
render = function () { renderWithAssets(); hydrateAssets(); };
""".replace("ASSET_DATA", asset_map)

    output = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
  <meta name="theme-color" content="#003b1e">
  <title>Gogo · Interactive H5 Demo 2</title>
  <style>{css}</style>
</head>
<body>
  <div id="app"></div>
  <script>{script_safe(app)}</script>
  <script>{script_safe(account)}</script>
  <script>{script_safe(hydrate)}</script>
</body>
</html>
"""
    (ROOT / "index.html").write_text(output, encoding="utf-8")
    print(f"Embedded {len(images)} original images in {ROOT / 'index.html'}")


if __name__ == "__main__":
    main()
