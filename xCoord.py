#!/usr/bin/env python3
import sys
import os

def read_mag(file_mag_in):
    with open(file_mag_in, 'r') as fread:
        lines = fread.readlines()
    fread.close()

    mag = {'block': [], 'structure': []}
    buffer = []
    block_name = 'header'
    for line in lines:
        if line[:2] == '<<' or line[:3] == 'use':
            if len(buffer) > 0:
                if 'header' not in mag.keys():
                    mag['header'] = buffer
                else:
                    mag['block'].append(block_name)
                    mag['structure'].append(buffer)
                buffer = []

            if line[:2] == '<<':
                block_name = line.split(' ')[1].strip()
            else:
                block_name = line.replace("\r", "").replace("\n", "")
        else:
            buffer.append(line.replace("\r", "").replace("\n", ""))

    return mag


def get_location(design):
    bignum = 10000000000000
    CoreX = bignum
    CoreY = bignum
    PinRouteX = bignum
    PinRouteY = bignum
    PadX = bignum
    PadY = bignum
    pads_keys = ['PIC', 'POB', 'PBC', 'PAN', 'PVD', 'PVS', 'PCO', 'IOF']
    for i, struct in enumerate(design['block']):
        if struct[:3] == 'met':
            for j, rects in enumerate(design['structure'][i]):
                rect = rects.split(' ')        
                if PinRouteX > int(rect[1]):
                    PinRouteX = int(rect[1])
                if PinRouteY > int(rect[2]):
                    PinRouteY = int(rect[2])
                if CoreX > int(rect[1]):
                    CoreX = int(rect[1])
                if CoreY > int(rect[2]):
                    CoreY = int(rect[2])

        check = False
        if struct[:3] == 'use':
            check = struct[4:7] in pads_keys
            unit_struct = design['structure'][i]
            carry = int(unit_struct[1].split(' ')[1])
            Xc = int(unit_struct[1].split(' ')[3])
            Yc = int(unit_struct[1].split(' ')[6])
            Xl = int(unit_struct[2].split(' ')[1])
            Yl = int(unit_struct[2].split(' ')[2])
            if carry == 1:
                PadX0 = Xl + Xc
                PadY0 = Yl + Yc
            else:
                PadX0 = Yl + Xc
                PadY0 = Xl + Yc

            if check:
                if PadX > PadX0 :
                    PadX = PadX0
                if PadY > PadY0:
                    PadY = PadY0
            else:
                if CoreX > PadX0 :
                    CoreX = PadX0
                if CoreY > PadY0:
                    CoreY = PadY0

    for i, struct in enumerate(design['block']):
        if 'Core' in struct:
            unit_struct = design['structure'][i]
            carry = int(unit_struct[1].split(' ')[1])
            Xc = int(unit_struct[1].split(' ')[3])
            Yc = int(unit_struct[1].split(' ')[6])
            Xl = int(unit_struct[2].split(' ')[1])
            Yl = int(unit_struct[2].split(' ')[2])
            if carry == 1:
                CoreX = Xl + Xc
                CoreY = Yl + Yc
            else:
                CoreX = Yl + Xc
                CoreY = Xl + Yc

    print('PAD_X = %.2f' % (PadX/100.0))
    print('PAD_Y = %.2f' % (PadY/100.0))
    print('PIN_ROUTE_X = %.3f' % (PinRouteX/100.0))
    print('PIN_ROUTE_Y = %.3f' % (PinRouteY/100.0))
    print('CORE_X = %.3f' % (CoreX/100.0))
    print('CORE_Y = %.3f' % (CoreY/100.0))
    print('\n')

    fpath = ''
    fname = 'Makefile'

    with open(os.path.join(fpath, fname), 'r') as fread:
        lines = fread.readlines()

    new_lines = []
    for i, line in enumerate(lines):
        if line.startswith('PAD_X'):
            new_line = line[:line.find('=') + 2] + '%.2f' % (PadX/100) + '\n'
            new_lines.append(new_line)
        elif line.startswith('PAD_X'):
            new_line = line[:line.find('=') + 2] + '%.2f' % (PadY/100) + '\n'
            new_lines.append(new_line)
        elif line.startswith('PIN_ROUTE_X'):
            new_line = line[:line.find('=') + 2] + '%.3f' % (PinRouteX/100) + '\n'
            new_lines.append(new_line)
        elif line.startswith('PIN_ROUTE_Y'):
            new_line = line[:line.find('=') + 2] + '%.3f' % (PinRouteY/100) + '\n'
            new_lines.append(new_line)
        elif line.startswith('CORE_X'):
            new_line = line[:line.find('=') + 2] + '%.3f' % (CoreX/100) + '\n'
            new_lines.append(new_line)
        elif line.startswith('CORE_Y'):
            new_line = line[:line.find('=') + 2] + '%.3f' % (CoreY/100) + '\n'
            new_lines.append(new_line)
        else:
            new_lines.append(line)

    try:
        with open(os.path.join(fpath, fname), 'w', encoding='utf-8') as file:
            file.write("".join(new_lines))
        print("Successful in updating the Makefile. Now you can generate the GDS file by make generate_gds")
    except OSError as e:
        print("Failure in updating the Makefile. Please update manually with new coordinates.")


# -----------------------------------------------------------
# Main start-up
# -----------------------------------------------------------

if len(sys.argv)!=2:
    print("Usage: xCore <core name>")
    print("     Extracting New Core from chip-top")
    exit()

file_mag_in  = str(sys.argv[1])+'_Top.mag'
print(file_mag_in)
get_location(read_mag(file_mag_in))

