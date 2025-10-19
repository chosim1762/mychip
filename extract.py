import sys
import os
from datetime import datetime
import time

def collect_structures(structures):
    all_layers = []
    for sn in structures.keys():
        for layer in structures[sn]['layer']:
            if layer not in all_layers:
                all_layers.append(layer)

    all_structures = {}
    for layer in all_layers:
        all_structures[layer] = []

    for sn in structures.keys():
        for layer in structures[sn]['layer']:
            for rects in structures[sn][layer]:
                all_structures[layer].append(rects)
    return all_structures

def transform(mode, x, mag, xc):
    if mode == 'to_top':
        return mag * x + xc
    if mode == 'to_core':
        return (x - xc) / mag
    if mode == 'same':
        return x

def get_sn(mode, fn):
    if mode == 'top':
        return fn[fn.rfind('/'):-8]
    if mode == 'core':
        return fn[fn.rfind('/'):-4]
    if mode == 'same':
        return fn[fn.rfind('/'):-4]


def read_structures(fpath, mag, xc, yc):
    with open(fpath, 'r') as f:
        content = f.readlines()
    infos = {}
    layers = []
    num_rect = 0
    for line in content:
        elems = line.replace('\n', '').split(' ')
        if elems[0] == 'magic':
            infos['type'] = 'magic'
        elif elems[0] == 'timestamp':
            dt_object = datetime.fromtimestamp(int(line.split(' ')[1]))
            infos['created'] = dt_object
        elif elems[0] == '<<':
            layer = elems[1]
            if layer != 'end' and layer != 'labels' and layer != 'checkpaint':
                layers.append(layer)
                infos[layer] = []
        elif elems[0] == 'rect':
            if layer != 'labels' and layer != 'checkpaint':
                elems.pop(0)
                if mag > 1:
                    coord_list = [mag*int(elems[0])+xc, mag*int(elems[1])+yc, mag*int(elems[2])+xc, mag*int(elems[3])+yc]
                elif mag < 1:
                    coord_list = [int((int(elems[0])-xc)/mag),int((int(elems[1])-xc)/mag),int((int(elems[2])-xc)/mag),int((int(elems[3])-xc)/mag)] 
                else:
                    coord_list = [int(x) for x in elems]
                infos[layer].append(coord_list)
                num_rect += 1
    infos['num_rect'] = num_rect
    infos['layer'] = layers
    return infos

def compose_magic(all_structures):
    timestamp = time.time()
    magic = 'magic\ntech scmos\ntimestamp %d\n' % timestamp
    for key in all_structures.keys():
        for i, rect in enumerate(all_structures[key]):
            if i == 0:
                magic += '<< %s >>\n' % key
            magic += 'rect %d %d %d %d\n' % (rect[0], rect[1], rect[2], rect[3])

    magic += '<< end >>'
    return magic

def get_Topfile(fname, sn):
    with open(fname, 'r') as f:
        content = f.readlines()
    infos = {}
    line_info = []
    structures = []
    passes = True
    i = 0
    for line in content:
        elems = line.replace('\n', '').split(' ')
        if passes:
            if elems[0] == 'timestamp':
                infos['timestamp'] = int(elems[1])
            elif elems[0] == 'magscale':
                infos['magscale'] = [int(elems[1]), int(elems[2])]
            elif elems[0] == 'use':
                if elems[1][:len(sn)] == sn:
                    infos[elems[1]] = {}
                    structures.append(elems[1])
                    passes = False
                    i += 1
        else:
            if elems[0] == 'timestamp':
                infos[structures[i-1]]['timestamp'] = int(elems[1])
            elif elems[0] == 'transform':
                infos[structures[i-1]]['transform'] = [int(elems[3]), int(elems[6])]
            elif elems[0] == 'box':
                infos[structures[i-1]]['box'] = [int(x) for x in elems[1:5]]
                passes = True
            
    return infos

def join_structures(top_structures,added_structures, mag):
    top_keys = top_structures.keys()
    added_keys = added_structures.keys()
    all_keys = []
    except_keys = ['type', 'created', 'layer', 'num_rect']
    all_structures = {}
    for key in top_structures.keys():
        if key not in all_keys and key not in except_keys:
            all_keys.append(key)
            all_structures[key] = []
    for key in added_structures.keys():
        if key not in all_keys and key not in except_keys:
            all_keys.append(key)
            all_structures[key] = []

    for layer in top_structures.keys():
        if layer not in except_keys:
            for rect in top_structures[layer]:
                all_structures[layer].append([int(mag*x) for x in rect])
    for layer in added_structures.keys():
        if layer not in except_keys:
            for rect in added_structures[layer]:
                all_structures[layer].append([int(mag*x) for x in rect])

    return all_structures


def main():
    args = sys.argv[1:]
    if not args:
        print("Enter the arguement")
        return
    cur_dir = os.getcwd()
    fpath =os.path.join(cur_dir, args[0])

    top_fname = "%s_Top.mag" % args[0]
    top_fpath = os.path.join(cur_dir, top_fname)

    top_infos = get_Topfile(top_fpath, args[0])

    Top_structures = read_structures(top_fpath, 1, 0, 0)

    files = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
    structures = {}
    for file in files:
        fname = "%s_%s.mag" % (fpath, file)
        name = "%s_%s" % (args[0], file)
        mag = top_infos['magscale'][1]
        cen = top_infos[name]['transform']

        structures[name] = read_structures(fname, mag, cen[0], cen[1])

    each_structures = collect_structures(structures)

    all_structures = join_structures(Top_structures, each_structures, 1/mag)

    magic = compose_magic(all_structures)
    print(magic)

    fn = os.path.join(cur_dir, 'test.mag')
    with open(fn, 'w') as f:
        f.write(magic)

if __name__ == "__main__":
    main()
