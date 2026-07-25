#!/usr/bin/env python3
"""Generate a deterministic, hand-drawn SVG from a repository's GitHub stars."""

# Standard library
import argparse
import html
import json
import math
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


API_ROOT = "https://api.github.com"
SVG_WIDTH = 900
SVG_HEIGHT = 500
PLOT_LEFT = 82
PLOT_RIGHT = 850
PLOT_TOP = 105
PLOT_BOTTOM = 410


def github_json(path: str, token: str | None) -> tuple[object, dict[str, str]]:
    """Fetch one JSON response from GitHub."""
    headers = {
        "Accept": "application/vnd.github.star+json",
        "User-Agent": "copit-star-history",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = Request(f"{API_ROOT}{path}", headers=headers)
    with urlopen(request, timeout=30) as response:
        body = json.load(response)
        return body, dict(response.headers.items())


def fetch_star_history(
    repository: str, token: str | None
) -> tuple[datetime, list[datetime]]:
    """Return the repository creation time and every available star timestamp."""
    metadata, _ = github_json(f"/repos/{repository}", token)
    if not isinstance(metadata, dict):
        raise RuntimeError("GitHub returned invalid repository metadata")

    created_at = parse_github_time(str(metadata["created_at"]))
    expected_count = int(metadata["stargazers_count"])
    stars: list[datetime] = []

    page = 1
    while True:
        payload, _ = github_json(
            f"/repos/{repository}/stargazers?per_page=100&page={page}", token
        )
        if not isinstance(payload, list):
            raise RuntimeError("GitHub returned invalid stargazer data")

        for item in payload:
            if not isinstance(item, dict) or "starred_at" not in item:
                raise RuntimeError(
                    "GitHub omitted star timestamps; the required media type was not used"
                )
            stars.append(parse_github_time(str(item["starred_at"])))

        if len(payload) < 100:
            break
        page += 1

    if len(stars) != expected_count:
        raise RuntimeError(
            f"GitHub reported {expected_count} stars but returned {len(stars)} timestamps"
        )

    return created_at, sorted(stars)


def parse_github_time(value: str) -> datetime:
    """Parse GitHub's UTC timestamp format."""
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def nice_maximum(value: int) -> int:
    """Round the chart maximum up to a readable axis value."""
    if value <= 5:
        return 5

    magnitude = 10 ** math.floor(math.log10(value))
    for multiplier in (1, 2, 5, 10):
        candidate = multiplier * magnitude
        if candidate >= value:
            return candidate
    return value


def svg_for(repository: str, created_at: datetime, stars: list[datetime]) -> str:
    """Render the star history as a self-contained SVG."""
    count = len(stars)
    y_max = nice_maximum(count)
    actual_end = stars[-1] if stars else created_at
    plot_end = max(actual_end, created_at + timedelta(days=1))
    span = (plot_end - created_at).total_seconds()

    def x_for(instant: datetime) -> float:
        elapsed = (instant - created_at).total_seconds()
        return PLOT_LEFT + (elapsed / span) * (PLOT_RIGHT - PLOT_LEFT)

    def y_for(value: int) -> float:
        return PLOT_BOTTOM - (value / y_max) * (PLOT_BOTTOM - PLOT_TOP)

    grid_paths: list[str] = []
    y_labels: list[str] = []
    for index in range(6):
        value = round((y_max * index) / 5)
        y = y_for(value)
        grid_paths.append(
            f'<path class="grid" d="M {PLOT_LEFT} {y:.1f} H {PLOT_RIGHT}" />'
        )
        y_labels.append(
            f'<text class="axis-label" x="{PLOT_LEFT - 16}" y="{y + 5:.1f}" '
            f'text-anchor="end">{value}</text>'
        )

    x_labels: list[str] = []
    for index in range(5):
        fraction = index / 4
        instant = created_at + (actual_end - created_at) * fraction
        x = PLOT_LEFT + fraction * (PLOT_RIGHT - PLOT_LEFT)
        if actual_end.date() == created_at.date():
            label = "Launch" if index == 0 else ("Latest" if index == 4 else "")
        else:
            label = instant.strftime("%b %Y")
        if label:
            x_labels.append(
                f'<text class="axis-label" x="{x:.1f}" y="{PLOT_BOTTOM + 34}" '
                f'text-anchor="middle">{html.escape(label)}</text>'
            )

    path_parts = [f"M {PLOT_LEFT} {y_for(0):.1f}"]
    previous_count = 0
    for current_count, starred_at in enumerate(stars, start=1):
        x = x_for(starred_at)
        path_parts.append(f"L {x:.1f} {y_for(previous_count):.1f}")
        path_parts.append(f"L {x:.1f} {y_for(current_count):.1f}")
        previous_count = current_count
    path_parts.append(f"L {PLOT_RIGHT} {y_for(count):.1f}")
    history_path = " ".join(path_parts)

    repository_label = html.escape(repository)
    star_label = f"{count:,} star" if count == 1 else f"{count:,} stars"
    marker_line = ""
    if stars:
        marker_line = (
            f'  <circle class="marker" cx="{PLOT_RIGHT}" '
            f'cy="{y_for(count):.1f}" r="6" />\n'
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_WIDTH}" height="{SVG_HEIGHT}" viewBox="0 0 {SVG_WIDTH} {SVG_HEIGHT}" role="img" aria-labelledby="title description">
  <title id="title">{repository_label} star history</title>
  <desc id="description">A hand-drawn chart showing {star_label} on GitHub.</desc>
  <style>
    .background {{ fill: #fffdf7; stroke: #292524; stroke-width: 2; }}
    .grid {{ fill: none; stroke: #d6d3d1; stroke-dasharray: 5 8; stroke-width: 1; }}
    .axis {{ fill: none; stroke: #44403c; stroke-linecap: round; stroke-width: 2.2; }}
    .history {{ fill: none; stroke: #f59e0b; stroke-linecap: round; stroke-linejoin: round; stroke-width: 5; }}
    .marker {{ fill: #f59e0b; stroke: #92400e; stroke-width: 2; }}
    .title {{ fill: #1c1917; font: 700 28px "Comic Sans MS", "Bradley Hand", cursive; }}
    .subtitle {{ fill: #78716c; font: 17px "Comic Sans MS", "Bradley Hand", cursive; }}
    .axis-label {{ fill: #78716c; font: 14px "Comic Sans MS", "Bradley Hand", cursive; }}
    @media (prefers-color-scheme: dark) {{
      .background {{ fill: #1c1917; stroke: #e7e5e4; }}
      .grid {{ stroke: #44403c; }}
      .axis {{ stroke: #d6d3d1; }}
      .title {{ fill: #fafaf9; }}
      .subtitle, .axis-label {{ fill: #a8a29e; }}
    }}
  </style>
  <defs>
    <filter id="rough" x="-4%" y="-8%" width="108%" height="116%">
      <feTurbulence type="fractalNoise" baseFrequency="0.012 0.08" numOctaves="2" seed="23" result="noise" />
      <feDisplacementMap in="SourceGraphic" in2="noise" scale="2.2" xChannelSelector="R" yChannelSelector="G" />
    </filter>
  </defs>
  <rect class="background" x="5" y="5" width="890" height="490" rx="22" />
  <text class="title" x="44" y="50">Star History</text>
  <text class="subtitle" x="44" y="78">{repository_label} · {star_label}</text>
  {" ".join(grid_paths)}
  <path class="axis" filter="url(#rough)" d="M {PLOT_LEFT} {PLOT_TOP} V {PLOT_BOTTOM} H {PLOT_RIGHT}" />
  {" ".join(y_labels)}
  {" ".join(x_labels)}
  <path class="history" filter="url(#rough)" d="{history_path}" />
{marker_line}</svg>
"""


def parse_arguments() -> argparse.Namespace:
    """Parse command-line options."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repository",
        default=os.environ.get("GITHUB_REPOSITORY", "AcastaPaloma/copit"),
        help="GitHub repository in owner/name form",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("assets/star-history.svg"),
        help="destination SVG path",
    )
    return parser.parse_args()


def main() -> int:
    """Fetch GitHub stars and atomically update the SVG."""
    arguments = parse_arguments()
    token = os.environ.get("GITHUB_TOKEN")

    try:
        created_at, stars = fetch_star_history(arguments.repository, token)
        svg = svg_for(arguments.repository, created_at, stars)
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = arguments.output.with_suffix(".svg.tmp")
        temporary_path.write_text(svg, encoding="utf-8")
        temporary_path.replace(arguments.output)
    except (HTTPError, URLError, KeyError, RuntimeError, ValueError) as error:
        print(f"Unable to update star history: {error}", file=sys.stderr)
        return 1

    print(f"Wrote {arguments.output} with {len(stars)} stars")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
