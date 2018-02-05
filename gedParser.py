#Author: Max Remetz
#Date: 1/23/2018

import os

def gedcomParser():
    infile = open('testfile.ged', 'r')
    for line in infile:
        print(('--> ' + line).strip())
        if line[0] == '0':
            parts = zeroLine(line.split())
        elif line[0] == '1':
            parts = oneLine(line.split())
        elif line[0] == '2':
            parts = twoLine(line.split())
        else:
            parts = line.split()
            parts.append('N')
        line = buildLine(parts)
        print(line)

def zeroLine(ln):
    if len(ln) > 2:
        if ln[2] == 'INDI' or ln[2] == 'FAM':
            return [ln[0], ln[2], ln[1], 'Y']
        elif ln[1] == 'NOTE':
            ln.append('Y')
            return ln
        else:
            ln.append('N')
            return ln
    elif ln[1] == 'HEAD' or ln[1] == 'TRLR':
        if len(ln) == 2:
            ln.append('Y')
            return ln
        else:
            ln.append('N')
            return ln
    else:
        ln.append('N')
        return ln

def oneLine(ln):
    if ln[1] == 'NAME':
        if len(ln) == 2 or (len(ln) > 2 and ln[-1][0] + ln[-1][-1] != '//'):
            ln.append('N')
            return ln
        ln.append('Y')
        return ln
    if ln[1] == 'SEX':
        if len(ln) == 3 and (ln[2] == 'M' or ln[2] == 'F'):
            ln.append('Y')
            return ln
        ln.append('N')
        return ln
    if ln[1] == 'BIRT' or ln[1] == 'DEAT' or ln[1] == 'MARR' or ln[1] == 'DIV':
        if len(ln) == 2:
            ln.append('Y')
            return ln
        ln.append('N')
        return ln
    if ln[1] == 'FAMC' or ln[1] == 'FAMS' or ln[1] == 'HUSB' or ln[1] == 'WIFE' or ln[1] == 'CHIL' :
        if len(ln) == 3:
            ln.append('Y')
            return ln
        ln.append('N')
        return ln
    ln.append('N')
    return ln

def twoLine(ln):
    months = ['JAN', 'MAR', 'MAY', 'JUL', 'AUG', 'OCT', 'DEC', 'APR', 'JUN',
              'SEP','NOV', 'FEB']
    if ln[1] == 'DATE' and len(ln) == 5:
        if ln[3] not in months or int(ln[2]) > 31 or int(ln[2]) < 1:
            ln.append('N')
            return ln
        elif int(ln[2]) == 31 and ln[3] not in months[0:]:
            ln.append('N')
            return ln
        elif int(ln[2]) > 29 and ln[3] == 'FEB':
            ln.append('N')
            return ln
        else:
            ln.append('Y')
            return ln
    ln.append('N')
    return ln

def buildLine(arr):
    string = '<-- ' + arr[0] + '|' + arr[1] + '|' + arr[-1] + '|'
    if len(arr) > 3:
        string = string + arr[2]
        for i in arr[3:-1]:
            string = string + ' ' + i
    return string

gedcomParser()
