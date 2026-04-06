import csv
import subprocess
import time
from pathlib import Path

REPEATS = 25

root = Path(__file__).resolve().parents[1]
binary = root / 'weighted_matcher'
data_dir = root / 'data'
results_csv = data_dir / 'runtime_results.csv'
svg_graph = data_dir / 'runtime_graph.svg'



def read_strings(input_file: Path):
    lines = [line.strip() for line in input_file.read_text(encoding='utf-8').splitlines() if line.strip()]
    return lines[-2], lines[-1]


def average(values):
    return sum(values) / len(values)


def draw_svg(points, destination: Path):
    width, height = 900, 540
    left, right, top, bottom = 80, 40, 40, 70
    plot_w = width - left - right
    plot_h = height - top - bottom

    xs = [p['cells'] for p in points]
    ys = [p['avg_runtime_ms'] for p in points]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = 0.0, max(ys) if ys else 1.0
    if max_x == min_x:
        max_x += 1
    if max_y == min_y:
        max_y += 1

    def sx(x):
        return left + (x - min_x) * plot_w / (max_x - min_x)

    def sy(y):
        return height - bottom - (y - min_y) * plot_h / (max_y - min_y)

    polyline = ' '.join(f"{sx(p['cells']):.1f},{sy(p['avg_runtime_ms']):.1f}" for p in points)
    circles = '\n'.join(
        f'<circle cx="{sx(p["cells"]):.1f}" cy="{sy(p["avg_runtime_ms"]):.1f}" r="4" />'
        for p in points
    )

    x_ticks = []
    for i in range(5):
        x_val = min_x + (max_x - min_x) * i / 4
        x_pos = sx(x_val)
        x_ticks.append(
            f'<line x1="{x_pos:.1f}" y1="{height-bottom}" x2="{x_pos:.1f}" y2="{height-bottom+6}" />'
            f'<text x="{x_pos:.1f}" y="{height-bottom+24}" text-anchor="middle">{int(x_val)}</text>'
        )

    y_ticks = []
    for i in range(5):
        y_val = min_y + (max_y - min_y) * i / 4
        y_pos = sy(y_val)
        y_ticks.append(
            f'<line x1="{left-6}" y1="{y_pos:.1f}" x2="{left}" y2="{y_pos:.1f}" />'
            f'<text x="{left-12}" y="{y_pos+4:.1f}" text-anchor="end">{y_val:.3f}</text>'
        )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<style>
    text {{ font-family: Arial, sans-serif; font-size: 13px; }}
    .axis, .tick {{ stroke: black; stroke-width: 1; fill: none; }}
    .line {{ stroke: black; stroke-width: 2; fill: none; }}
    circle {{ fill: black; }}
</style>
<rect x="0" y="0" width="{width}" height="{height}" fill="white" />
<text x="{width/2}" y="24" text-anchor="middle">Runtime Across 10 Input Files ({REPEATS} runs each)</text>
<line class="axis" x1="{left}" y1="{height-bottom}" x2="{width-right}" y2="{height-bottom}" />
<line class="axis" x1="{left}" y1="{height-bottom}" x2="{left}" y2="{top}" />
{''.join(x_ticks)}
{''.join(y_ticks)}
<polyline class="line" points="{polyline}" />
{circles}
<text x="{width/2}" y="{height-20}" text-anchor="middle">DP table size (|A| × |B|)</text>
<text x="20" y="{height/2}" text-anchor="middle" transform="rotate(-90 20 {height/2})">Average runtime (ms)</text>
</svg>'''
    destination.write_text(svg, encoding='utf-8')


input_files = sorted(data_dir.glob('test*.in'))
rows = []

for input_file in input_files:
    left_word, right_word = read_strings(input_file)
    timings = []
    latest_output = ''

    for _ in range(REPEATS):
        begin = time.perf_counter()
        run = subprocess.run([str(binary), str(input_file)], capture_output=True, text=True, check=True)
        timings.append((time.perf_counter() - begin) * 1000.0)
        latest_output = run.stdout

    input_file.with_suffix('.out').write_text(latest_output, encoding='utf-8')

    rows.append({
        'file': input_file.name,
        'len_A': len(left_word),
        'len_B': len(right_word),
        'cells': len(left_word) * len(right_word),
        'avg_runtime_ms': average(timings),
        'min_runtime_ms': min(timings),
        'max_runtime_ms': max(timings),
    })

with results_csv.open('w', newline='', encoding='utf-8') as handle:
    writer = csv.DictWriter(handle, fieldnames=['file', 'len_A', 'len_B', 'cells', 'avg_runtime_ms', 'min_runtime_ms', 'max_runtime_ms'])
    writer.writeheader()
    writer.writerows(rows)

draw_svg(rows, svg_graph)


