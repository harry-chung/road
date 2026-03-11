import sys, re, collections, argparse
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.colors as mcolors
import matplotlib.cm as cm
import matplotlib.patches as mpatches

sys.stdout.reconfigure(encoding='utf-8')

font_path = 'C:/Windows/Fonts/malgun.ttf'
fp = lambda size: fm.FontProperties(fname=font_path, size=size)
plt.rcParams['font.family'] = fm.FontProperties(fname=font_path).get_name()
plt.rcParams['axes.unicode_minus'] = False

def extract_base(name):
    m = re.search('[로길]', name)
    return name[:m.end()] if m else name

def make_map(road_name, cmap_name, row_bg_color, out_path):
    # 시도별 카운트
    counter = collections.Counter()
    with open('C:/test/TN_SPRD_RDNM.txt', 'r', encoding='cp949') as f:
        for line in f:
            row = line.rstrip('\r\n').split('|')
            if len(row) >= 6 and row[3] and extract_base(row[3]) == road_name:
                counter[row[5]] += 1

    # GeoJSON 로드 및 시도 병합
    gdf = gpd.read_file('C:/test/korea_sido.json')
    sido_gdf = gdf.dissolve(by='sidonm').reset_index()
    name_map = {'강원도': '강원특별자치도', '전라북도': '전북특별자치도'}
    sido_gdf['sidonm_new'] = sido_gdf['sidonm'].replace(name_map)
    sido_gdf['count'] = sido_gdf['sidonm_new'].map(counter).fillna(0).astype(int)

    table_data = sorted(
        [(row['sidonm_new'], row['count']) for _, row in sido_gdf.iterrows()],
        key=lambda x: -x[1]
    )
    total = sum(c for _, c in table_data)
    max_count = sido_gdf['count'].max() if sido_gdf['count'].max() > 0 else 1

    cmap = plt.get_cmap(cmap_name)
    norm = mcolors.Normalize(vmin=0, vmax=max_count)

    # 레이아웃
    fig = plt.figure(figsize=(15, 11))
    ax_map = fig.add_axes([0.0, 0.0, 0.62, 1.0])
    ax_tbl = fig.add_axes([0.63, 0.08, 0.35, 0.84])

    # ── 지도 ──
    sido_gdf.plot(column='count', cmap=cmap, norm=norm,
                  linewidth=0.8, edgecolor='#555555', ax=ax_map)

    sm = cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    ax_cbar = fig.add_axes([0.05, 0.06, 0.35, 0.025])
    cbar = fig.colorbar(sm, cax=ax_cbar, orientation='horizontal')
    cbar.set_label('도로명 수 (건)', fontproperties=fp(9))
    cbar.ax.tick_params(labelsize=8)

    ax_map.set_title(f'{road_name} 시도별 분포', fontproperties=fp(16), pad=12)
    ax_map.axis('off')

    # ── 테이블 ──
    ax_tbl.axis('off')
    ax_tbl.set_xlim(0, 1)
    ax_tbl.set_ylim(0, 1)

    headers = ['시도명', '건수']
    col_x = [0.02, 0.62]
    header_y = 0.94

    ax_tbl.axhline(y=0.99, xmin=0, xmax=1, color='#333333', linewidth=1.5)
    for x, h in zip(col_x, headers):
        ax_tbl.text(x, header_y + 0.02, h, fontproperties=fp(11), fontweight='bold', va='center')
    ax_tbl.axhline(y=header_y - 0.015, xmin=0, xmax=1, color='#333333', linewidth=1.0)

    row_h = (header_y - 0.038 - 0.05) / len(table_data)
    for i, (sidonm, cnt) in enumerate(table_data):
        y = header_y - 0.038 - (i + 0.7) * row_h
        bg = row_bg_color if i % 2 == 0 else 'white'
        ax_tbl.add_patch(mpatches.FancyBboxPatch(
            (0, y - row_h * 0.45), 1, row_h * 0.9,
            boxstyle='square,pad=0', facecolor=bg, edgecolor='none', zorder=0
        ))
        bar_w = cnt / max_count * 0.25
        bar_color = cmap(norm(cnt))
        ax_tbl.add_patch(mpatches.FancyBboxPatch(
            (col_x[1] - 0.02, y - row_h * 0.3), bar_w, row_h * 0.6,
            boxstyle='square,pad=0', facecolor=bar_color, edgecolor='none', zorder=1, alpha=0.6
        ))
        ax_tbl.text(col_x[0], y, sidonm, fontproperties=fp(10), va='center', zorder=2)
        ax_tbl.text(col_x[1] + 0.12, y, f'{cnt:,}', fontproperties=fp(10), va='center', ha='right', zorder=2)

    ax_tbl.axhline(y=header_y - 0.038 - len(table_data) * row_h, xmin=0, xmax=1, color='#aaaaaa', linewidth=0.8)
    y_total = header_y - 0.038 - (len(table_data) + 0.7) * row_h
    ax_tbl.text(col_x[0], y_total, '합계', fontproperties=fp(10), fontweight='bold', va='center')
    ax_tbl.text(col_x[1] + 0.12, y_total, f'{total:,}', fontproperties=fp(10), fontweight='bold', va='center', ha='right')
    ax_tbl.set_title('시도별 건수', fontproperties=fp(13), pad=10)

    plt.savefig(out_path, dpi=150, bbox_inches='tight', facecolor='white')
    print(f'저장 완료: {out_path}')
    plt.close()

# 중앙로 (파랑)
make_map('중앙로', 'Blues', '#EEF4FB', 'C:/test/중앙로_시도별지도.png')

# 벚꽃로 (핑크)
make_map('벚꽃로', 'RdPu', '#FDF0F5', 'C:/test/벚꽃로_시도별지도.png')

from feedback import prompt_feedback
prompt_feedback('map_chart')
