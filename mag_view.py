import os
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

fd = 'd:/SynologyDrive/현안/할일/2025_chosim1762_영상만들기/mychip'
fn = 'inverter.mag'
fpath = os.path.join(fd, fn)

with open(fpath, 'r') as f:
    content = f.readlines()

#print(content)

infos = {}
layers = []
num_rect = 0
for line in content:
    elems = line.replace('\n','').split(' ')
    match elems[0]:
        case 'magic':
            infos['type'] = 'magic'
        case 'timestamp':
            dt_object = datetime.fromtimestamp(int(line.split(' ')[1]))
            infos['created'] = dt_object
        case '<<':
            layer = elems[1]
            if layer != 'end' and layer != 'labels' and layer != 'checkpaint':
                layers.append(layer)
                infos[layer] = []
        case 'rect':
            if layer != 'labels' and layer != 'checkpaint':
                elems.pop(0)
                coord_list = [int(x) for x in elems]
                infos[layer].append(coord_list)
                num_rect += 1

infos['num_rect'] = num_rect
infos['layers'] = layers
infos['colors'] = sns.color_palette('flare', len(infos['layers']))
print(infos)


fig = plt.figure(figsize=(8,8))
ax = fig.add_subplot(111)

for layer_name in infos['layers']:
    for i, coord in enumerate(infos[layer_name]):
        rect = Rectangle((coord[0], coord[1]), coord[2]-coord[0], coord[3]-coord[1], edgecolor=infos['colors'][i], facecolor=infos['colors'][i], linewidth=1)
        ax.add_patch(rect)
plt.gca().autoscale(enable=True, axis='both', tight=False)
plt.show()

