"""Gera ícones PWA a partir do logo.png"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SRC  = ROOT / "logo.png"
DEST = ROOT / "frontend" / "icons"
DEST.mkdir(exist_ok=True)

SIZES = [72, 96, 128, 144, 152, 192, 384, 512]

img = Image.open(SRC).convert("RGBA")

for size in SIZES:
    out = img.resize((size, size), Image.LANCZOS)
    out.save(DEST / f"icon-{size}.png", "PNG")
    print(f"  icon-{size}.png ✓")

# Badge pequeno (72x72 monocromático para Android)
badge = img.resize((72, 72), Image.LANCZOS)
badge.save(DEST / "badge-72.png", "PNG")
print("  badge-72.png ✓")
print(f"\nÍcones salvos em {DEST}")
