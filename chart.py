import sys, re, collections
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

sys.stdout.reconfigure(encoding='utf-8')

# 한글 폰트 설정 (Windows)
font_path = 'C:/Windows/Fonts/malgun.ttf'
font_prop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()
plt.rcParams['axes.unicode_minus'] = False

def extract_base(name):
    m = re.search('[로길]', name)
    return name[:m.end()] if m else name

counter = collections.Counter()
with open('C:/test/TN_SPRD_RDNM.txt', 'r', encoding='cp949') as f:
    for line in f:
        row = line.rstrip('\r\n').split('|')
        if len(row) >= 6 and row[3] and extract_base(row[3]) == '중앙로':
            counter[row[5]] += 1

labels = list(counter.keys())
sizes = list(counter.values())
total = sum(sizes)

# 5% 미만은 기타로 묶기
threshold = total * 0.05
main_labels, main_sizes, other = [], [], 0
for l, s in zip(labels, sizes):
    if s >= threshold:
        main_labels.append(l)
        main_sizes.append(s)
    else:
        other += s
if other:
    main_labels.append('기타')
    main_sizes.append(other)

# 파이차트
fig, ax = plt.subplots(figsize=(9, 7))
wedges, texts, autotexts = ax.pie(
    main_sizes,
    labels=main_labels,
    autopct=lambda p: f'{p:.1f}%\n({int(round(p*total/100))}건)',
    startangle=140,
    pctdistance=0.75,
    textprops={'fontproperties': font_prop, 'fontsize': 11}
)
for at in autotexts:
    at.set_fontproperties(font_prop)
    at.set_fontsize(9)

ax.set_title(f'중앙로 시도별 분포 (전체 {total:,}건)', fontproperties=font_prop, fontsize=14, pad=20)
plt.tight_layout()
plt.savefig('C:/test/중앙로_시도별분포.png', dpi=150, bbox_inches='tight')
print('저장 완료: C:/test/중앙로_시도별분포.png')

from feedback import prompt_feedback
prompt_feedback('chart')
