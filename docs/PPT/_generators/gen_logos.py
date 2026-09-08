#!/usr/bin/env python3
"""Generate vendor logo PNGs for the PFF AI ARB decks (dark theme).

Authentic brand marks come from the `simpleicons` package (rendered white for the
black canvas). Brands not in Simple Icons are rendered as clean branded text chips.
Output: docs/PPT/assets/logos/*.png  (transparent, 512px marks; chip tiles for the rest)
"""
import os
import cairosvg
from PIL import Image, ImageDraw, ImageFont
from simpleicons.all import icons

OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "logos"))
os.makedirs(OUT, exist_ok=True)

WHITE = "#FFFFFF"

# name -> simpleicons key (rendered white). Azure services reuse the Azure mark + label.
ICON_MARKS = {
    "azure": "microsoftazure",
    "aks": "kubernetes",
    "kubernetes": "kubernetes",
    "redis": "redis",
    "python": "python",
    "fastapi": "fastapi",
    "sonarqube": "sonarqube",
    "azuredevops": "azuredevops",
    "opentelemetry": "opentelemetry",
    "docker": "docker",
    "openai": "openai",
}

# Azure-family services: Azure mark, shown with a text label on the slide.
AZURE_SERVICES = ["apim", "servicebus", "aisearch", "keyvault", "acr", "monitor",
                  "appinsights", "loganalytics", "blob"]

# Brands not in Simple Icons -> branded chip (bg hex, text, text color)
CHIPS = {
    "huggingface": ("#FFD21E", "Hugging Face", "#000000"),
    "langgraph":   ("#1C3C3C", "LangGraph", "#FFFFFF"),
    "langchain":   ("#1C3C3C", "LangChain", "#FFFFFF"),
    "langfuse":    ("#0A60B5", "Langfuse", "#FFFFFF"),
    "pydantic":    ("#E92063", "Pydantic", "#FFFFFF"),
    "ruff":        ("#D7FF64", "Ruff", "#000000"),
    "vllm":        ("#4B2AAF", "vLLM", "#FFFFFF"),
    "mcp":         ("#2ACCFF", "MCP", "#000000"),
}


def render_mark(key, out_path, fill=WHITE, px=512):
    ic = icons[key]
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{px}" height="{px}" '
           f'viewBox="0 0 24 24"><path d="{ic.path}" fill="{fill}"/></svg>')
    cairosvg.svg2png(bytestring=svg.encode(), write_to=out_path,
                     output_width=px, output_height=px)


def _font(size):
    for f in ("DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(f, size)
        except Exception:
            continue
    return ImageFont.load_default()


def render_chip(name, bg, text, fg, out_path, w=900, h=280, radius=44):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r, g, b = tuple(int(bg[i:i+2], 16) for i in (1, 3, 5))
    d.rounded_rectangle([4, 4, w-4, h-4], radius=radius, fill=(r, g, b, 255))
    fr, fg_, fb = tuple(int(fg[i:i+2], 16) for i in (1, 3, 5))
    size = 120
    font = _font(size)
    while font.getbbox(text)[2] > (w - 80) and size > 30:
        size -= 6
        font = _font(size)
    bbox = font.getbbox(text)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    d.text(((w-tw)/2 - bbox[0], (h-th)/2 - bbox[1]), text, font=font, fill=(fr, fg_, fb, 255))
    img.save(out_path)


def main():
    made = []
    for name, key in ICON_MARKS.items():
        p = os.path.join(OUT, f"{name}.png")
        render_mark(key, p)
        made.append(name)
    # Azure services share the azure mark image (label added on the slide)
    azure_src = os.path.join(OUT, "azure.png")
    for svc in AZURE_SERVICES:
        Image.open(azure_src).save(os.path.join(OUT, f"{svc}.png"))
        made.append(svc)
    for name, (bg, text, fg) in CHIPS.items():
        render_chip(name, bg, text, fg, os.path.join(OUT, f"{name}.png"))
        made.append(name)
    print(f"Generated {len(made)} logos in {OUT}")
    print(", ".join(sorted(made)))


if __name__ == "__main__":
    main()
