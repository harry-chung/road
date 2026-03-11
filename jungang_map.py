import sys, re, collections
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

# 중앙로 + 중앙대로 시도별 카운트
target = {'중앙로', '중앙대로'}
counter = collections.Counter()
type_counter = {'중앙로': collections.Counter(), '중앙대로': collections.Counter()}

with open('C:/test/TN_SPRD_RDNM.txt', 'r', encoding='cp949') as f:
    for line in f:
        row = line.rstrip('\r\n').split('|')
        if len(row) >= 6 and row[3]:
            base = extract_base(row[3])
            if base in target:
                counter[row[5]] += 1
                type_counter[base][row[5]] += 1

total_ro  = sum(type_counter['중앙로'].values())
total_dae = sum(type_counter['중앙대로'].values())
total     = sum(counter.values())
print(f'중앙로: {total_ro}건, 중앙대로: {total_dae}건, 합계: {total}건')

# GeoJSON 로드
gdf = gpd.read_file('C:/test/korea_sido.json')
sido_gdf = gdf.dissolve(by='sidonm').reset_index()
name_map = {'강원도': '강원특별자치도', '전라북도': '전북특별자치도'}
sido_gdf['sidonm_new'] = sido_gdf['sidonm'].replace(name_map)
sido_gdf['count']     = sido_gdf['sidonm_new'].map(counter).fillna(0).astype(int)
sido_gdf['count_ro']  = sido_gdf['sidonm_new'].map(type_counter['중앙로']).fillna(0).astype(int)
sido_gdf['count_dae'] = sido_gdf['sidonm_new'].map(type_counter['중앙대로']).fillna(0).astype(int)

all_data = sorted(
    [(row['sidonm_new'], row['count'], row['count_ro'], row['count_dae'])
     for _, row in sido_gdf.iterrows()],
    key=lambda x: -x[1]
)
max_count = sido_gdf['count'].max() if sido_gdf['count'].max() > 0 else 1

cmap = plt.get_cmap('Blues')
norm = mcolors.Normalize(vmin=0, vmax=max_count)

# 레이아웃
fig = plt.figure(figsize=(16, 11))
ax_map = fig.add_axes([0.0, 0.0, 0.58, 1.0])
ax_tbl = fig.add_axes([0.60, 0.08, 0.40, 0.84])

# ── 지도 ──
sido_gdf.plot(column='count', cmap=cmap, norm=norm,
              linewidth=0.8, edgecolor='#555555', ax=ax_map)

sm = cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
ax_cbar = fig.add_axes([0.04, 0.06, 0.33, 0.025])
cbar = fig.colorbar(sm, cax=ax_cbar, orientation='horizontal')
cbar.set_label('도로명 수 (건)', fontproperties=fp(9))
cbar.ax.tick_params(labelsize=8)

ax_map.set_title('중앙로 + 중앙대로 시도별 분포', fontproperties=fp(15), pad=12)
ax_map.axis('off')

# ── 테이블 ──
ax_tbl.axis('off')
ax_tbl.set_xlim(0, 1)
ax_tbl.set_ylim(0, 1)

col_x   = [0.02, 0.48, 0.65, 0.82]
headers = ['시도명', '합계', '중앙로', '중앙대로']
header_y = 0.94

ax_tbl.axhline(y=0.99, xmin=0, xmax=1, color='#333333', linewidth=1.5)
for x, h in zip(col_x, headers):
    ax_tbl.text(x, header_y + 0.02, h, fontproperties=fp(10), fontweight='bold', va='center')
ax_tbl.axhline(y=header_y - 0.015, xmin=0, xmax=1, color='#333333', linewidth=1.0)

row_h = (header_y - 0.038 - 0.05) / len(all_data)
for i, (sidonm, cnt, cnt_ro, cnt_dae) in enumerate(all_data):
    y = header_y - 0.038 - (i + 0.7) * row_h
    bg = '#EEF4FB' if i % 2 == 0 else 'white'
    ax_tbl.add_patch(mpatches.FancyBboxPatch(
        (0, y - row_h * 0.45), 1, row_h * 0.9,
        boxstyle='square,pad=0', facecolor=bg, edgecolor='none', zorder=0
    ))
    if cnt > 0:
        bar_w = cnt / max_count * 0.20
        ax_tbl.add_patch(mpatches.FancyBboxPatch(
            (col_x[1] - 0.02, y - row_h * 0.3), bar_w, row_h * 0.6,
            boxstyle='square,pad=0', facecolor=cmap(norm(cnt)), edgecolor='none', zorder=1, alpha=0.6
        ))
    ax_tbl.text(col_x[0], y, sidonm,        fontproperties=fp(9.5), va='center', zorder=2)
    ax_tbl.text(col_x[1]+0.10, y, f'{cnt:,}',     fontproperties=fp(9.5), va='center', ha='right', zorder=2, fontweight='bold')
    ax_tbl.text(col_x[2]+0.10, y, f'{cnt_ro:,}',  fontproperties=fp(9.5), va='center', ha='right', zorder=2)
    ax_tbl.text(col_x[3]+0.10, y, f'{cnt_dae:,}', fontproperties=fp(9.5), va='center', ha='right', zorder=2)

ax_tbl.axhline(y=header_y - 0.038 - len(all_data) * row_h, xmin=0, xmax=1, color='#aaaaaa', linewidth=0.8)
y_total = header_y - 0.038 - (len(all_data) + 0.7) * row_h
ax_tbl.text(col_x[0],    y_total, '합계',          fontproperties=fp(10), fontweight='bold', va='center')
ax_tbl.text(col_x[1]+0.10, y_total, f'{total:,}',     fontproperties=fp(10), fontweight='bold', va='center', ha='right')
ax_tbl.text(col_x[2]+0.10, y_total, f'{total_ro:,}',  fontproperties=fp(10), fontweight='bold', va='center', ha='right')
ax_tbl.text(col_x[3]+0.10, y_total, f'{total_dae:,}', fontproperties=fp(10), fontweight='bold', va='center', ha='right')
ax_tbl.set_title('시도별 건수', fontproperties=fp(13), pad=10)

plt.savefig('C:/test/중앙_시도별지도.png', dpi=150, bbox_inches='tight', facecolor='white')
print('저장 완료: C:/test/중앙_시도별지도.png')

from feedback import prompt_feedback
prompt_feedback('jungang_map')
