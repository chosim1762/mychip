import numpy as np

class mag_layout:
    def __init__(self, layout=''):
        self.lam = 1
        self.layout = layout

    def get_structure(self):
        return self.layout

    def make_well(self, scale):
        lam = self.lam
        self.scale = scale
        well = (-12*scale*lam, -12*scale*lam, 12*scale*lam, 12*scale*lam)
        element = {'WELL': {'well1': {'rect': well, 'color': 'black', 'label': 'well'}}}
        self.layout = element
        return element

    def unit_mos(self, scale, pos):
        lam = self.lam
        self.scale = scale
        contact = (-scale*lam, -scale*lam, scale*lam, scale*lam)
        metal = (-3*scale*lam, -3*scale*lam, 3*scale*lam, 3*scale*lam)
        diff = (-9*scale*lam, -4*scale*lam, 9*scale*lam, 4*scale*lam)
        poly = (-scale*lam, -7*scale*lam, scale*lam, 7*scale*lam)
        element = {'MOS': {}}
        element['MOS']['contact1'] = {'rect': self.__shift_rect(contact, -5*scale*lam, 0), 'color': 'blue', 'label': 'dcontact'}
        element['MOS']['contact2'] = {'rect': self.__shift_rect(contact, 5*scale*lam, 0), 'color': 'blue', 'label': 'dcontact'}
        element['MOS']['diffusion'] = {'rect': element['MOS']['contact1']['rect'][0:2] + element['MOS']['contact2']['rect'][2:4], 'color': 'magenta', 'label': 'diffusion'}

        if pos == 'ul':
            element['MOS']['substratecontact'] = {'rect': self.__shift_rect(contact, -5*scale*lam, 10*scale*lam), 'color': 'black', 'label': 'substratecontact'}
        if pos == 'dl':
            element['MOS']['substratecontact'] =  {'rect': self.__shift_rect(contact, -5*scale*lam, -10*scale*lam), 'color': 'black', 'label': 'substratecontact'}
        if pos == 'ur':
            element['MOS']['substratecontact'] = {'rect': self.__shift_rect(contact, 5*scale*lam, 10*scale*lam), 'color': 'black', 'label': 'substratecontact'}
        if pos == 'dr':
            element['MOS']['substratecontact'] =  {'rect': self.__shift_rect(contact, 5*scale*lam, -10*scale*lam), 'color': 'black', 'label': 'substratecontact'}
        self.layout = element
        return element

    def common_gate(self,length):
        lam = self.lam
        gate = (-lam, -round(length*lam/2), lam, round(length*lam/2))
        element = {'MOS': {'gate': {'rect': gate, 'color': 'red', 'label': 'polysilicon'}}}
        self.layout = element
        return element

    def dopant(self, doping):
        self.doping = doping
        structure = self.layout
        for key in structure.keys():
            if key == 'MOS':
                for k in structure[key].keys():
                    label = structure[key][k]['label']
                    if label == 'dcontact' or label == 'diffusion':
                        structure[key][k]['label'] = doping + label
            if key == 'WELL':
                for k in structure[key].keys():
                    label = structure[key][k]['label']
                    if label == 'well':
                        structure[key][k]['label'] = doping + label
        self.layout = structure
        return structure

    def __shift_rect(self, rect, x_shift, y_shift):
        return (rect[0] + x_shift, rect[1] + y_shift, rect[2] + x_shift, rect[3] + y_shift)

    def __rotate_rect(self, rect, x_center, y_center, angle):
        theta = angle / 180 * np.pi
        xleft_new = round(np.cos(theta) * (rect[0] - x_center) - np.sin(theta) * (rect[1] - y_center) + x_center)
        yleft_new = round(np.sin(theta) * (rect[0] - x_center) + np.cos(theta) * (rect[1] - y_center) + y_center)
        xright_new = round(np.cos(theta) * (rect[2] - x_center) - np.sin(theta) * (rect[3] - y_center) + x_center)
        yright_new = round(np.sin(theta) * (rect[2] - x_center) + np.cos(theta) * (rect[3] - y_center) + y_center)
        return xleft_new, yleft_new, xright_new, yright_new


    def shift_structure(self, x_shift, y_shift):
        structure = self.layout
        new_struct = {}
        for category in structure.keys():
            new_struct[category] = {}
            for layername in structure[category].keys():
                one_rect = {}
                for key in structure[category][layername].keys():
                    if key == 'rect':
                        one_rect['rect'] = self.__shift_rect(structure[category][layername][key], x_shift, y_shift)
                    else:
                        one_rect[key] = structure[category][layername][key]
                new_struct[category][layername] = one_rect
        self.layout = new_struct
        return new_struct


    def rotate_structure(self, x_center, y_center, angle):
        structure = self.layout
        new_struct = {}
        for category in structure.keys():
            new_struct[category] = {}
            for layername in structure[category].keys():
                one_rect = {}
                for key in structure[category][layername].keys():
                    if key == 'rect':
                        one_rect['rect'] = self.__rotate_rect(structure[category][layername][key], x_center, y_center, angle)
                    else:
                        one_rect[key] = structure[category][layername][key]
                new_struct[category][layername] = one_rect
        self.layout = new_struct
        return new_struct

structures = []

pmos = mag_layout()
pmos.unit_mos(scale=10, pos='ur')
pmos.dopant(doping='p')
pmos.shift_structure(x_shift=0, y_shift=80)
print(pmos.get_structure())
structures.append(pmos.get_structure())

nmos = mag_layout()
nmos.unit_mos(scale=10, pos='dl')
nmos.dopant(doping='n')
nmos.shift_structure(x_shift=0, y_shift=0)
print(nmos.get_structure())
structures.append(nmos.get_structure())

gate = mag_layout()
gate.common_gate(120)
print(gate.get_structure())
gate.shift_structure(x_shift=0, y_shift=40)
structures.append(gate.get_structure())

nwell = mag_layout()
nwell.make_well(10)
nwell.dopant(doping='n')
nwell.shift_structure(x_shift=0, y_shift=80)
print(nwell.get_structure())
structures.append(nwell.get_structure())

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

def append_plt_struct(ax, structures):
    for structure in structures:
        for category in structure.keys():
            for key, info in  structure[category].items():
                shape = info['rect']
                color = info['color']
                rect = Rectangle((shape[0], shape[1]), shape[2]-shape[0], shape[3]-shape[1], edgecolor=color, facecolor='none', linewidth=1)
                ax.add_patch(rect)
    return ax

fig = plt.figure(figsize=(8,8))

ax = fig.add_subplot(111)
ax = append_plt_struct(ax, structures)
#ax = append_plt_struct(ax, shift_struct(element['NMOS'], 30, 0))
#ax = append_plt_struct(ax, rotate_struct(shift_struct(element['NMOS'], 30, 0), 0, 0, 90))
#ax.set_xlim(-10, 40)
#ax.set_ylim(-10, 40)
plt.gca().autoscale(enable=True, axis='both', tight=False)
plt.show()