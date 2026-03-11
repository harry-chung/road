# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Korean road name analysis and visualization system. Parses a large pipe-delimited road name dataset (`TN_SPRD_RDNM.txt`, CP949 encoding) and produces choropleth maps + data tables as PNG files using geopandas and matplotlib.

## Running Scripts

No build system — run scripts directly:

```bash
python bcherry_map.py
python jungang_map.py
python seoul_map.py
python dong_map.py
python chart.py
python map_chart.py
```

**Dependencies**: `geopandas`, `matplotlib`, `pandas`

```bash
pip install geopandas matplotlib pandas
```

## Key Data Files

| File | Description |
|------|-------------|
| `TN_SPRD_RDNM.txt` | Main dataset: 369,597 lines, pipe-delimited (`|`), CP949 encoding |
| `korea_sido.json` | 34.8 MB GeoJSON with Korean administrative boundaries |
| `top200_road_names.csv` | Top 200 most common road names with province-level counts |

**Critical field indices in `TN_SPRD_RDNM.txt`**:
- `[3]` = Road name (도로명)
- `[5]` = Province (시도명)
- `[6]` = District (구군명)
- `[9]` = Ward (동명)

## Architecture

All scripts follow the same ETL + visualization pipeline:

1. **Parse** `TN_SPRD_RDNM.txt` (CP949, pipe-delimited) → filter by road name pattern → count by geographic level
2. **Merge** counts with `korea_sido.json` GeoJSON
3. **Normalize** administrative names (e.g., `강원도` → `강원특별자치도`; strip ward numbers like `독산1동` → `독산동`)
4. **Render** choropleth map (left) + data table with bar charts (right) → save as PNG at 150 DPI

### Script Roles

- `bcherry_map.py` / `jungang_map.py` — province-level analysis for specific road names
- `seoul_map.py` — district-level analysis within Seoul
- `dong_map.py` — ward-level analysis within Geumcheon-gu
- `chart.py` — simple pie chart only
- `map_chart.py` — parameterized version; accepts `road_name`, `colormap`, `output_path` arguments for batch generation

## Platform Notes

- Scripts use Windows font path (`malgun.ttf` / Malgun Gothic) for Korean text rendering
- File paths in scripts are hardcoded to `C:/test/` — update these when running in a different environment
- Output PNGs use Korean filenames (e.g., `벚꽃_시도별지도.png`)
