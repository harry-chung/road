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

# 금천구 벚꽃로 동별 카운트
counter = collections.Counter()
with open('C:/test/TN_SPRD_RDNM.txt', 'r', encoding='cp949') as f:
    for line in f:
        row = line.rstrip('\r\n').split('|')
        if (len(row) >= 10 and row[3] and extract_base(row[3]) == '벚꽃로'
                and row[5] == '서울특별시' and row[6] == '금천구'):
            dong = row[9] if row[9] else '(미부여)'
            counter[dong] += 1

print('동별 카운트:', dict(counter))

# 금천구 행정동 GeoJSON
gdf = gpd.read_file('C:/test/korea_sido.json')
gdf_gmc = gdf[(gdf['sidonm'] == '서울특별시') & (gdf['sggnm'] == '금천구')].copy()

# adm_nm에서 동 이름 추출 (예: '서울특별시 금천구 가산동' → '가산동')
# 행정동 이름에서 숫자 제거해 법정동으로 변환 (독산1동→독산동)
gdf_gmc['dongnm_admin'] = gdf_gmc['adm_nm'].str.split().str[-1]
gdf_gmc['dongnm'] = gdf_gmc['dongnm_admin'].str.replace(r'\d+동$', '동', regex=True)
dong_gdf = gdf_gmc.dissolve(by='dongnm').reset_index()
dong_gdf['count'] = dong_gdf['dongnm'].map(counter).fillna(0).astype(int)

print('동 목록:', dong_gdf['dongnm'].tolist())

all_data = sorted(
    [(row['dongnm'], row['count']) for _, row in dong_gdf.iterrows()],
    key=lambda x: -x[1]
)
total = sum(c for _, c in all_data)
max_count = dong_gdf['count'].max() if dong_gdf['count'].max() > 0 else 1

cmap = plt.get_cmap('RdPu')
norm = mcolors.Normalize(vmin=0, vmax=max_count)

# 레이아웃
fig = plt.figure(figsize=(14, 9))
ax_map = fig.add_axes([0.0, 0.0, 0.62, 1.0])
ax_tbl = fig.add_axes([0.63, 0.15, 0.35, 0.72])

# ── 지도 ──
dong_gdf.plot(column='count', cmap=cmap, norm=norm,
              linewidth=0.8, edgecolor='#555555', ax=ax_map)

for _, row in dong_gdf.iterrows():
    centroid = row.geometry.centroid
    ax_map.annotate(
        row['dongnm'],
        xy=(centroid.x, centroid.y),
        ha='center', va='center',
        fontproperties=fp(9),
        color='white' if row['count'] >= max_count * 0.5 else '#333333'
    )

sm = cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
ax_cbar = fig.add_axes([0.05, 0.05, 0.35, 0.025])
cbar = fig.colorbar(sm, cax=ax_cbar, orientation='horizontal')
cbar.set_label('도로명 수 (건)', fontproperties=fp(9))
cbar.ax.tick_params(labelsize=8)

ax_map.set_title('금천구 벚꽃로 동별 분포', fontproperties=fp(15), pad=12)
ax_map.axis('off')

# ── 테이블 ──
ax_tbl.axis('off')
ax_tbl.set_xlim(0, 1)
ax_tbl.set_ylim(0, 1)

col_x = [0.02, 0.62]
header_y = 0.94

ax_tbl.axhline(y=0.99, xmin=0, xmax=1, color='#333333', linewidth=1.5)
for x, h in zip(col_x, ['동명', '건수']):
    ax_tbl.text(x, header_y + 0.02, h, fontproperties=fp(11), fontweight='bold', va='center')
ax_tbl.axhline(y=header_y - 0.015, xmin=0, xmax=1, color='#333333', linewidth=1.0)

row_h = (header_y - 0.038 - 0.05) / len(all_data)
for i, (dongnm, cnt) in enumerate(all_data):
    y = header_y - 0.038 - (i + 0.7) * row_h
    bg = '#FDF0F5' if i % 2 == 0 else 'white'
    ax_tbl.add_patch(mpatches.FancyBboxPatch(
        (0, y - row_h * 0.45), 1, row_h * 0.9,
        boxstyle='square,pad=0', facecolor=bg, edgecolor='none', zorder=0
    ))
    if cnt > 0:
        bar_w = cnt / max_count * 0.25
        ax_tbl.add_patch(mpatches.FancyBboxPatch(
            (col_x[1] - 0.02, y - row_h * 0.3), bar_w, row_h * 0.6,
            boxstyle='square,pad=0', facecolor=cmap(norm(cnt)), edgecolor='none', zorder=1, alpha=0.7
        ))
    ax_tbl.text(col_x[0], y, dongnm, fontproperties=fp(10), va='center', zorder=2)
    ax_tbl.text(col_x[1] + 0.12, y, f'{cnt:,}', fontproperties=fp(10), va='center', ha='right', zorder=2)

ax_tbl.axhline(y=header_y - 0.038 - len(all_data) * row_h, xmin=0, xmax=1, color='#aaaaaa', linewidth=0.8)
y_total = header_y - 0.038 - (len(all_data) + 0.7) * row_h
ax_tbl.text(col_x[0], y_total, '합계', fontproperties=fp(10), fontweight='bold', va='center')
ax_tbl.text(col_x[1] + 0.12, y_total, f'{total:,}', fontproperties=fp(10), fontweight='bold', va='center', ha='right')
ax_tbl.set_title('동별 건수', fontproperties=fp(13), pad=10)

plt.savefig('C:/test/금천구_벚꽃로_동별지도.png', dpi=150, bbox_inches='tight', facecolor='white')
print('저장 완료: C:/test/금천구_벚꽃로_동별지도.png')
