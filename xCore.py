#!/usr/bin/env python3
import sys

# -----------------------------------------------------------
# Function: Reading Magic file heading
def read_heading_use(file_mag_in):
    # open input Magic file
    file_in  = open(file_mag_in,  'r')

    # Magic Layout file headings
    # 1-st line must be 'magic'
    file_line = file_in.readline()
    if file_line[0:5] != "magic":
        print("1st line: NOT Magic file!")
        exit()
    #print(file_line, end="")
    file_out.write(file_line)

    # 2-nd line must be 'tech'
    file_line = file_in.readline()
    if file_line[0:10] != "tech scmos":
        print("2nd line: NOT tech scmos")
        exit()
    #print(file_line, end="")
    file_out.write(file_line)

    # 3-rd line must be 'magscale'
    file_line = file_in.readline()
    if file_line[0:8] != "magscale":
        print("3rd line: NOT magscale")
        exit()
    #print(file_line, end="")
    file_out.write(file_line)

    # 4-th line must be 'timestamp'
    file_line = file_in.readline()
    if file_line[0:9] != "timestamp":
        print("4th line: NOT timestamp")
        exit()
    #print(file_line, end="")
    file_out.write(file_line)

    # Check "use" to be excluded
#    print("Excluding use....")
    while True:
        file_line = file_in.readline()
        pads_keys = ['PIC', 'POB', 'PBC', 'PAN', 'PVD', 'PVS', 'PCO', 'IOF']
        check = False
        if file_line[0:3] == "use":
            check = file_line[4:7] in pads_keys
        if check:
#            print(file_line)
            file_line = file_in.readline()
            if file_line[0:9] != "timestamp":
                if check:
#                    print("NOT timestamp after use")
                    exit()
                else:
                    file_out.write(file_line)
            file_line = file_in.readline()
            if file_line[0:9] != "transform":
                if check:
#                    print("NOT transform after use>timestamp")
                    exit()
                else:
                    file_out.write(file_line)
            file_line = file_in.readline()
            if file_line[0:3] != "box":
                if check:
#                    print("NOT box after use>timestamp>transform")
                    exit()
                else:
                    file_out.write(file_line)
        else:
            file_out.write(file_line)
        if not file_line:   # EoF
            break

    file_in.close()

    return


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

    print('The core design file has been created! Please edit and insert to the Top file')
    print('by using getcell command at the position of (%.2f, %.2f).' % (CoreX/100.0, CoreY/100.0))


# -----------------------------------------------------------
# Main start-up
# -----------------------------------------------------------

if len(sys.argv)!=2:
    print("Usage: xCore <core name>")
    print("     Extracting New Core from chip-top")
    exit()
    
file_mag_in  = str(sys.argv[1])+'_Top.mag'
file_mag_out = str(sys.argv[1])+'_Core.mag'

# open Magic file for output
file_out = open(file_mag_out, 'w')

read_heading_use(file_mag_in)
get_location(read_mag(file_mag_in))

file_out.write("")
file_out.close()
