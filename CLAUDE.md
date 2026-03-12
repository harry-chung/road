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
- **Data file is at `C:/project/road/TN_SPRD_RDNM.txt`** (not `C:/test/` — older scripts have wrong paths)
- Output PNGs use Korean filenames (e.g., `벚꽃_시도별지도.png`)

---

## 유니크도로명 분석 (세션 2025-03-12 기준)

### 분석 결과물

| 파일 | 설명 |
|------|------|
| `유니크도로명_분석.csv` | 69,682개 유니크도로명 전체 분석 (UTF-8 BOM, Excel 호환) |
| `유니크도로명_집계표.png` | 명사구분/유형별 집계표 이미지 |
| `유니크도로명_누적분포도.png` | 상위 N개 유니크도로명의 누적 도로명 커버리지 |
| `유니크도로명_유형별_파이차트.png` | 유형별 구성비 파이차트 |
| `부여사유_워드클라우드.png` | 부여사유 텍스트 기반 워드클라우드 |
| `wordcloud_road.py` | 워드클라우드 생성 스크립트 |

### 유니크도로명 정의

- `TN_SPRD_RDNM.txt` [3]번 필드(도로명)에서 첫 번째 `로` 또는 `길` 이전까지 추출
- **단, 도로명의 맨 처음이 `로`/`길`로 시작하는 것은 제외** (`m.start() > 0` 조건)
- 총 69,682개 (전체 도로명 368,847건)

```python
m = re.search('[로길]', name)
if m and m.start() > 0:
    base = name[:m.end()]
```

### CSV 컬럼 및 분류 체계

`순위, 유니크도로명, 빈도수, 명사구분, 유형, 시도, 시군구`

**명사구분/유형 분류 결과:**

| 명사구분 | 유형 | 유니크도로명 수 | 도로명 건수 |
|---------|------|-------------:|----------:|
| 고유 | 지명 | 65,393 | 340,003 |
| 고유 | 인물 | 2,572 | 12,496 |
| 고유 | 역사문화재 | 778 | 5,244 |
| 고유 | 자연경관(지형) | 572 | 4,197 |
| 고유 | 자연경관(동식물) | 263 | 1,619 |
| 일반 | 가치/이념 | 45 | 2,562 |
| 일반 | 방향/위치 | 34 | 1,818 |
| 일반 | 시설/기능 | 13 | 750 |
| 일반 | 자연경관 | 9 | 103 |
| 일반 | 기타(일반) | 3 | 55 |
| **합계** | | **69,682** | **368,847** |

### 분류 로직 핵심

```python
# 필드 인덱스
[3] = 도로명, [5] = 시도명, [6] = 시군구명, [9] = 동명, [11] = 부여사유

# 줄기(stem) 추출
stem = re.sub(r'(대로|로|길)$', '', base)

# 분류 우선순위
1. stem이 common_nouns 목록에 있으면 → 일반명사 + 해당 유형
2. 부여사유([11]) 키워드로 고유명사 유형 판별:
   - 인물 키워드: '인물','위인','장군','선생','대왕','독립운동','묘호','아호','기리기 위','기려','의병장' 등
   - 역사문화재 키워드: '역사성','역사적','문화재','서원','사찰','사당','3.1운동','국채보상운동' 등
   - 자연경관: nature_stems 집합 (벚꽃, 소나무, 두루미 등 동식물 / 지형 suffix로 구분)
3. 나머지 → 고유/지명
```

### 수동 보정 내역

- 효령로(266위): 고유/지명 → 고유/인물
- 동일로: 가치/이념 → 방향/위치 (동쪽 일번로)
- 산성로/산성대로, 향교로/향교길: 일반/기타 → 고유/역사문화재
- 고유/기타 전체(773개) → 고유/역사문화재

### 자연경관 세분류

- **자연경관(동식물)**: `nature_stems` 집합으로 판별 (벚꽃, 매화, 진달래 등 꽃/나무/조류)
- **자연경관(지형)**: terrain suffix (`산,강,호,령,폭포,천,봉,계`) + `non_nature_stems` 블랙리스트 (익산, 부산 등 지명 오탐 방지) + `known_lakes` 화이트리스트

### 워드클라우드 방법론 (`wordcloud_road.py`)

- 단순 템플릿 행 제외: 분기도로, 일련번호, 서수식, 행정구역명 인용 패턴
- 포괄적 불용어(STOP) + 추가 불용어(STOP_EXTRA) + 동사어간(VERB_STEMS) 제거
- 조사 제거 함수(`strip_josa`) 적용
- 1음절 지리명사(`산, 강, 물, 숲` 등)는 별도 허용 (ONE_CHAR_GEO)
- `wordcloud` 라이브러리 필요: `pip install wordcloud`
