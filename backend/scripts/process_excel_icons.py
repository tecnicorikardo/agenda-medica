"""Processa ícones Excel: remove fundo branco e gera versão 32x32 para o menu."""
from pathlib import Path
from PIL import Image
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / "frontend" / "icons"
DEST.mkdir(exist_ok=True)

for name, out_name in [("excel-export.png", "excel-export.png"), ("excel-import.png", "excel-import.png")]:
    img = Image.open(ROOT / name).convert("RGBA")
    data = np.array(img)

    # Remove fundo branco/claro — pixels com R,G,B todos > 240 viram transparentes
    r, g, b, a = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]
    mask = (r > 235) & (g > 235) & (b > 235)
    data[mask] = [0, 0, 0, 0]

    result = Image.fromarray(data)

    # Salva versão grande (para uso futuro)
    result.save(DEST / out_name)

    # Salva versão 28x28 para o menu dropdown
    small = result.resize((28, 28), Image.LANCZOS)
    small.save(DEST / f"sm-{out_name}")

    print(f"  {out_name} ✓  (+ sm-{out_name})")

print(f"\nSalvos em {DEST}")
