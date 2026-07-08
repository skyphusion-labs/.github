#!/usr/bin/env python3
"""Generate Skyphusion Labs social preview and X banner PNGs from SVG templates."""

from __future__ import annotations

import json
import subprocess
import textwrap
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
OUT = ROOT / "output"
REPOS_JSON = ROOT / "repos.json"
RSVG = "/opt/homebrew/bin/rsvg-convert"

MOTIFS: dict[str, str] = {
    "org": """
      <g transform="translate(0,0)">
        <circle cx="120" cy="120" r="100" fill="none" stroke="url(#motifGrad)" stroke-width="8" opacity="0.85"/>
        <path d="M60 70 L180 120 L60 170 Z" fill="url(#motifGrad)" opacity="0.55"/>
        <path d="M30 210 L90 210 L120 130 L150 210 L210 210 L120 40 Z" fill="url(#motifGrad)" opacity="0.35"/>
      </g>
    """,
    "film": """
      <g transform="translate(20,10)">
        <rect x="20" y="40" width="200" height="140" rx="12" fill="none" stroke="url(#motifGrad)" stroke-width="10"/>
        <path d="M95 70 L170 110 L95 150 Z" fill="url(#motifGrad)" opacity="0.8"/>
        <rect x="0" y="20" width="240" height="28" rx="6" fill="url(#motifGrad)" opacity="0.25"/>
        <rect x="0" y="172" width="240" height="28" rx="6" fill="url(#motifGrad)" opacity="0.25"/>
      </g>
    """,
    "gpu": """
      <g transform="translate(30,20)">
        <rect x="20" y="30" width="180" height="160" rx="18" fill="none" stroke="url(#motifGrad)" stroke-width="10"/>
        <rect x="50" y="60" width="120" height="100" rx="8" fill="url(#motifGrad)" opacity="0.35"/>
        <path d="M70 90 H150 M70 110 H150 M70 130 H150" stroke="url(#motifGrad)" stroke-width="8" stroke-linecap="round"/>
        <circle cx="40" cy="50" r="8" fill="url(#motifGrad)"/>
        <circle cx="180" cy="50" r="8" fill="url(#motifGrad)"/>
        <circle cx="40" cy="170" r="8" fill="url(#motifGrad)"/>
        <circle cx="180" cy="170" r="8" fill="url(#motifGrad)"/>
      </g>
    """,
    "lipsync": """
      <g transform="translate(40,30)">
        <path d="M40 120 Q120 40 200 120 Q120 200 40 120 Z" fill="none" stroke="url(#motifGrad)" stroke-width="10"/>
        <path d="M60 120 Q120 90 180 120" fill="none" stroke="url(#motifGrad)" stroke-width="8" stroke-linecap="round"/>
        <path d="M20 60 Q60 20 100 60 T180 60" fill="none" stroke="url(#motifGrad)" stroke-width="6" opacity="0.6"/>
        <path d="M20 180 Q60 220 100 180 T180 180" fill="none" stroke="url(#motifGrad)" stroke-width="6" opacity="0.6"/>
      </g>
    """,
    "upscale": """
      <g transform="translate(50,20)">
        <path d="M120 200 L120 40 M80 80 L120 40 L160 80" fill="none" stroke="url(#motifGrad)" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/>
        <rect x="40" y="120" width="60" height="60" rx="8" fill="url(#motifGrad)" opacity="0.35"/>
        <rect x="140" y="80" width="80" height="80" rx="8" fill="url(#motifGrad)" opacity="0.55"/>
      </g>
    """,
    "audio": """
      <g transform="translate(30,40)">
        <path d="M20 120 L40 80 L60 140 L80 60 L100 150 L120 90 L140 120 L160 70 L180 130 L200 100" fill="none" stroke="url(#motifGrad)" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>
        <circle cx="110" cy="110" r="70" fill="none" stroke="url(#motifGrad)" stroke-width="6" opacity="0.35"/>
      </g>
    """,
    "discord": """
      <g transform="translate(40,30)">
        <rect x="20" y="40" width="180" height="120" rx="28" fill="url(#motifGrad)" opacity="0.25"/>
        <circle cx="70" cy="100" r="18" fill="url(#motifGrad)"/>
        <circle cx="150" cy="100" r="18" fill="url(#motifGrad)"/>
        <path d="M40 60 Q110 20 180 60" fill="none" stroke="url(#motifGrad)" stroke-width="8" stroke-linecap="round"/>
      </g>
    """,
    "prism": """
      <g transform="translate(20,10)">
        <path d="M120 30 L210 200 L30 200 Z" fill="none" stroke="url(#motifGrad)" stroke-width="10"/>
        <path d="M120 30 L120 200" stroke="url(#motifGrad)" stroke-width="6" opacity="0.5"/>
        <path d="M75 115 L165 115" stroke="url(#motifGrad)" stroke-width="6" opacity="0.5"/>
        <circle cx="60" cy="80" r="16" fill="#38bdf8" opacity="0.8"/>
        <circle cx="170" cy="90" r="16" fill="#f472b6" opacity="0.8"/>
        <circle cx="120" cy="170" r="16" fill="#fbbf24" opacity="0.8"/>
      </g>
    """,
    "email": """
      <g transform="translate(35,35)">
        <rect x="20" y="50" width="190" height="120" rx="14" fill="none" stroke="url(#motifGrad)" stroke-width="10"/>
        <path d="M20 60 L115 130 L210 60" fill="none" stroke="url(#motifGrad)" stroke-width="10" stroke-linejoin="round"/>
      </g>
    """,
    "search": """
      <g transform="translate(35,25)">
        <circle cx="100" cy="100" r="70" fill="none" stroke="url(#motifGrad)" stroke-width="12"/>
        <path d="M150 150 L210 210" stroke="url(#motifGrad)" stroke-width="14" stroke-linecap="round"/>
        <path d="M70 100 H130 M100 70 V130" stroke="url(#motifGrad)" stroke-width="6" opacity="0.35"/>
      </g>
    """,
    "mud": """
      <g transform="translate(25,20)" font-family="JetBrains Mono" font-size="22" fill="url(#motifGrad)" opacity="0.75">
        <text x="20" y="40">&gt; enter grid</text>
        <text x="20" y="80" opacity="0.8">  world: hollow</text>
        <text x="20" y="120" opacity="0.65">  faction: dawn</text>
        <text x="20" y="160" opacity="0.5">  agents: 3 online</text>
        <rect x="10" y="185" width="210" height="4" fill="url(#motifGrad)" opacity="0.4"/>
      </g>
    """,
    "thread": """
      <g transform="translate(40,30)">
        <circle cx="60" cy="80" r="24" fill="url(#motifGrad)" opacity="0.5"/>
        <circle cx="140" cy="60" r="24" fill="url(#motifGrad)" opacity="0.65"/>
        <circle cx="180" cy="150" r="24" fill="url(#motifGrad)" opacity="0.8"/>
        <path d="M78 92 L118 72 L156 132" fill="none" stroke="url(#motifGrad)" stroke-width="8" stroke-linecap="round"/>
        <path d="M40 130 Q90 200 150 170" fill="none" stroke="url(#motifGrad)" stroke-width="6" opacity="0.45"/>
      </g>
    """,
    "blog": """
      <g transform="translate(50,25)">
        <path d="M40 200 L40 40 L150 40 L190 80 L190 200 Z" fill="none" stroke="url(#motifGrad)" stroke-width="10" stroke-linejoin="round"/>
        <path d="M150 40 L150 80 L190 80" fill="none" stroke="url(#motifGrad)" stroke-width="8"/>
        <path d="M70 110 H160 M70 140 H160 M70 170 H130" stroke="url(#motifGrad)" stroke-width="8" stroke-linecap="round"/>
      </g>
    """,
}


def wrap_tagline(text: str, width: int = 46) -> list[str]:
    lines = textwrap.wrap(text, width=width)
    return lines[:2] if lines else [text]


def logo_mark() -> str:
    return """
      <g transform="translate(0,0)">
        <rect width="56" height="56" rx="12" fill="url(#logoBg)"/>
        <path d="M8 45L19.6 45L28 19L28 10Z" fill="url(#logoSky)"/>
        <path d="M22.4 45L33.6 45L28 19Z" fill="url(#logoSky)"/>
        <path d="M36.4 45L48 45L28 10L28 19Z" fill="url(#logoSky)"/>
      </g>
    """


def social_preview_svg(
    *,
    width: int,
    height: int,
    display: str,
    tagline: str,
    accent: str,
    accent2: str,
    chip: str,
    motif: str,
    footer: str,
    org_label: str = "SKYPHUSION LABS",
) -> str:
    motif_svg = MOTIFS.get(motif, MOTIFS["org"])
    tag_lines = wrap_tagline(tagline, 44 if width >= 1200 else 38)
    tag_y = 360 if height >= 600 else 250
    name_size = 72 if len(display) <= 18 else 58
    name_y = 280 if height >= 600 else 200

    tag_text = "\n".join(
        f'<text x="72" y="{tag_y + i * 38}" font-family="DM Sans 9pt" font-size="28" fill="#8fa3be">{escape(line)}</text>'
        for i, line in enumerate(tag_lines)
    )

    chip_w = max(120, len(chip) * 14 + 40)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <defs>
    <radialGradient id="bg" cx="24%" cy="16%" r="95%">
      <stop offset="0%" stop-color="#0e1730"/>
      <stop offset="55%" stop-color="#070b14"/>
      <stop offset="100%" stop-color="#05080f"/>
    </radialGradient>
    <linearGradient id="logoSky" x1="8" y1="45" x2="48" y2="10" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#1d4ed8"/>
      <stop offset="100%" stop-color="#06b6d4"/>
    </linearGradient>
    <radialGradient id="logoBg" cx="50%" cy="35%" r="70%">
      <stop offset="0%" stop-color="#17243d"/>
      <stop offset="100%" stop-color="#0a0f1e"/>
    </radialGradient>
    <linearGradient id="accent" x1="0" y1="{height}" x2="{width}" y2="0" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="{accent}"/>
      <stop offset="100%" stop-color="{accent2}"/>
    </linearGradient>
    <linearGradient id="motifGrad" x1="0" y1="240" x2="240" y2="0" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="{accent}"/>
      <stop offset="100%" stop-color="{accent2}"/>
    </linearGradient>
    <pattern id="grid" width="48" height="48" patternUnits="userSpaceOnUse">
      <path d="M48 0H0V48" fill="none" stroke="#1e2d45" stroke-width="1" opacity="0.35"/>
    </pattern>
    <filter id="blur" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="70"/>
    </filter>
  </defs>

  <rect width="{width}" height="{height}" fill="url(#bg)"/>
  <rect width="{width}" height="{int(height * 0.55)}" fill="url(#grid)" opacity="0.45"/>
  <circle cx="120" cy="30" r="200" fill="{accent}" opacity="0.16" filter="url(#blur)"/>
  <circle cx="{width - 120}" cy="{int(height * 0.45)}" r="220" fill="{accent2}" opacity="0.14" filter="url(#blur)"/>

  <g transform="translate(72,56)">
    {logo_mark()}
    <text x="72" y="36" font-family="JetBrains Mono" font-size="18" font-weight="700" letter-spacing="5" fill="url(#accent)">{escape(org_label)}</text>
  </g>

  <text x="72" y="{name_y}" font-family="JetBrains Mono" font-size="{name_size}" font-weight="700" fill="#e8edf5">{escape(display)}</text>
  {tag_text}

  <g transform="translate(72,{height - 88})" font-family="JetBrains Mono" font-size="18" font-weight="500">
    <rect width="{chip_w}" height="42" rx="8" fill="#0c1220" stroke="#2d4266"/>
    <text x="{chip_w / 2:.0f}" y="28" text-anchor="middle" fill="{accent}">{escape(chip)}</text>
  </g>

  <text x="{width - 72}" y="{height - 36}" text-anchor="end" font-family="JetBrains Mono" font-size="18" letter-spacing="1" fill="#4a5d78">{escape(footer)}</text>

  <g transform="translate({width - 340},{int(height * 0.22)})" opacity="0.22">
    {motif_svg}
  </g>
</svg>"""


def x_banner_svg() -> str:
    projects = [
        "vivijure",
        "postern",
        "prism",
        "the-hollow-grid",
        "common-thread",
        "slate",
    ]
    chips = "\n".join(
        f"""<g transform="translate({80 + i * 230}, 380)">
      <rect width="210" height="42" rx="8" fill="#0c1220" stroke="#2d4266"/>
      <text x="105" y="28" text-anchor="middle" font-family="JetBrains Mono" font-size="16" fill="#7b8da8">{escape(name)}</text>
    </g>"""
        for i, name in enumerate(projects)
    )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="500" viewBox="0 0 1500 500">
  <defs>
    <radialGradient id="bg" cx="20%" cy="30%" r="95%">
      <stop offset="0%" stop-color="#0e1730"/>
      <stop offset="55%" stop-color="#070b14"/>
      <stop offset="100%" stop-color="#05080f"/>
    </radialGradient>
    <linearGradient id="logoSky" x1="8" y1="45" x2="48" y2="10" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#1d4ed8"/>
      <stop offset="100%" stop-color="#06b6d4"/>
    </linearGradient>
    <radialGradient id="logoBg" cx="50%" cy="35%" r="70%">
      <stop offset="0%" stop-color="#17243d"/>
      <stop offset="100%" stop-color="#0a0f1e"/>
    </radialGradient>
    <linearGradient id="accent" x1="0" y1="500" x2="1500" y2="0" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#06b6d4"/>
      <stop offset="55%" stop-color="#60a5fa"/>
      <stop offset="100%" stop-color="#a78bfa"/>
    </linearGradient>
    <pattern id="grid" width="48" height="48" patternUnits="userSpaceOnUse">
      <path d="M48 0H0V48" fill="none" stroke="#1e2d45" stroke-width="1" opacity="0.35"/>
    </pattern>
    <filter id="blur" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="60"/>
    </filter>
  </defs>

  <rect width="1500" height="500" fill="url(#bg)"/>
  <rect width="1500" height="320" fill="url(#grid)" opacity="0.4"/>
  <circle cx="180" cy="80" r="180" fill="#1d4ed8" opacity="0.18" filter="url(#blur)"/>
  <circle cx="1320" cy="220" r="200" fill="#7c3aed" opacity="0.16" filter="url(#blur)"/>

  <g transform="translate(72,72)">
    {logo_mark()}
    <text x="72" y="36" font-family="JetBrains Mono" font-size="22" font-weight="700" letter-spacing="6" fill="url(#accent)">SKYPHUSION LABS</text>
  </g>

  <text x="72" y="210" font-family="JetBrains Mono" font-size="54" font-weight="700" fill="#e8edf5">We build things you can keep.</text>
  <text x="72" y="270" font-family="DM Sans 9pt" font-size="26" fill="#8fa3be">Free AGPL open source. Not for sale. Developed in the open.</text>

  {chips}

  <g transform="translate(1180,120)" opacity="0.18">
    {MOTIFS["org"]}
  </g>

  <text x="1428" y="468" text-anchor="end" font-family="JetBrains Mono" font-size="18" letter-spacing="2" fill="#4a5d78">@skyphusion · skyphusion.org</text>
</svg>"""


def render_svg(svg: str, out_path: Path, width: int, height: int) -> None:
    svg_path = out_path.with_suffix(".svg")
    svg_path.write_text(svg, encoding="utf-8")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [RSVG, "-w", str(width), "-h", str(height), str(svg_path), "-o", str(out_path)],
        check=True,
    )


def main() -> None:
    repos = json.loads(REPOS_JSON.read_text(encoding="utf-8"))
    preview_dir = OUT / "social-preview"
    preview_dir.mkdir(parents=True, exist_ok=True)

    for entry in repos:
        owner = entry["owner"]
        repo = entry["repo"]
        safe_name = repo.replace(".", "_")
        footer = f"github.com/{owner}/{repo}"
        org_label = entry.get("org_label", "SKYPHUSION LABS")

        svg = social_preview_svg(
            width=1280,
            height=640,
            display=entry["display"],
            tagline=entry["tagline"],
            accent=entry["accent"],
            accent2=entry["accent2"],
            chip=entry["chip"],
            motif=entry["motif"],
            footer=footer,
            org_label=org_label,
        )
        out = preview_dir / f"{owner}__{safe_name}.png"
        render_svg(svg, out, 1280, 640)
        print(f"social-preview: {out}")

    banner_dir = OUT / "x-banner"
    banner_dir.mkdir(parents=True, exist_ok=True)
    banner_svg = x_banner_svg()
    banner_out = banner_dir / "skyphusion-x-banner.png"
    render_svg(banner_svg, banner_out, 1500, 500)
    print(f"x-banner: {banner_out}")


if __name__ == "__main__":
    main()
