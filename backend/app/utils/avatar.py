import base64
import hashlib

# Colors drawn from Nepali cultural motifs: the flag's crimson/blue, Dashain
# marigold, terraced-hill green, and prayer-flag purple.
NEPALI_PALETTES = [
    ("#DC143C", "#6E0C1E"),  # flag crimson
    ("#003893", "#001F4D"),  # flag blue
    ("#F4A300", "#8A5600"),  # marigold / saffron
    ("#2E7D32", "#123317"),  # terraced hills
    ("#6A0DAD", "#33053D"),  # prayer flag purple
]

AGENT_TYPE_LABELS = {
    "reasoning": "Reasoning",
    "planning": "Planning",
    "execution": "Execution",
    "monitoring": "Monitoring",
}


def _initials(name: str) -> str:
    words = [w for w in (name or "").split() if w]
    if not words:
        return "AI"
    if len(words) == 1:
        return words[0][:2].upper()
    return (words[0][0] + words[1][0]).upper()


def generate_agent_avatar(name: str, agent_type: str = "reasoning") -> str:
    """Generate a deterministic Himalaya/prayer-flag styled SVG avatar for
    an agent, returned as a base64 data URI. Same name+type always renders
    the same avatar; different agents get different palette variants."""
    seed = int(hashlib.md5(f"{name}:{agent_type}".encode()).hexdigest(), 16)
    primary, secondary = NEPALI_PALETTES[seed % len(NEPALI_PALETTES)]
    initials = _initials(name)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 128 128">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{primary}"/>
      <stop offset="100%" stop-color="{secondary}"/>
    </linearGradient>
  </defs>
  <rect width="128" height="128" rx="22" fill="url(#bg)"/>
  <!-- prayer flag bunting -->
  <g opacity="0.55">
    <path d="M0,14 L128,14" stroke="#FFFFFF" stroke-width="1.5"/>
    <polygon points="10,14 18,14 14,24" fill="#F4A300"/>
    <polygon points="30,14 38,14 34,22" fill="#FFFFFF"/>
    <polygon points="50,14 58,14 54,26" fill="#2E7D32"/>
    <polygon points="70,14 78,14 74,21" fill="#DC143C"/>
    <polygon points="90,14 98,14 94,25" fill="#003893"/>
    <polygon points="110,14 118,14 114,23" fill="#F4A300"/>
  </g>
  <!-- sun -->
  <circle cx="100" cy="34" r="9" fill="#FFD700" opacity="0.95"/>
  <!-- crescent moon -->
  <circle cx="27" cy="34" r="8" fill="#FFFFFF" opacity="0.9"/>
  <circle cx="30.5" cy="31" r="6.5" fill="{primary}"/>
  <!-- initials -->
  <text x="64" y="70" font-family="'Segoe UI', Arial, sans-serif" font-size="34" font-weight="700"
        fill="#FFFFFF" text-anchor="middle" dominant-baseline="middle">{initials}</text>
  <!-- himalayan skyline -->
  <polygon points="0,128 16,100 32,116 52,90 72,114 92,96 112,112 128,102 128,128"
           fill="{secondary}" opacity="0.95"/>
  <polygon points="16,100 24,106 32,116" fill="#FFFFFF" opacity="0.4"/>
  <polygon points="52,90 60,98 68,96" fill="#FFFFFF" opacity="0.4"/>
</svg>"""

    encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"
