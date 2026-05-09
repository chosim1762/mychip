#!/usr/bin/env python3
import sys

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

    print('PinRouteX: %.2f PinRouteY: %.2f' % (PinRouteX/100.0, PinRouteY/100.0))
    print('PadX: %.2f PadY: %.2f' % (PadX/100.0, PadY/100.0))
    print('Attach the core design to the position of %.2f, %.2f' % (CoreX/100.0, CoreY/100.0))


# -----------------------------------------------------------
# Main start-up
# -----------------------------------------------------------

if len(sys.argv)!=2:
    print("Usage: xCore <core name>")
    print("     Extracting New Core from chip-top")
    exit()
    
file_mag_in  = str(sys.argv[1])+'_Top.mag'
#file_mag_out = str(sys.argv[1])+'_Core.mag'

# open Magic file for output
#file_out = open(file_mag_out, 'w')

#read_heading_use(file_mag_in)
get_location(read_mag(file_mag_in))

#file_out.write("")
#file_out.close()
