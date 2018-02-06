#Authors: Max Remetz, Adam Bannat, Kirk Visser
#We pledge our honor that we have abided by the Stevens Honor System
#Date: 2/6/2018

import os
import collections
import datetime
from prettytable import PrettyTable


indis = {}
fams = {}

#indiGen = {'Name': '', 'Gender': '', 'Birthday': '', 'Age': '', 'Alive': 'True', 'Child': '', 'Spouse': ''}

#famGen = {'Married': '', 'Divorced': '', 'Husband ID': '', 'Husband Name': '', 'Wife Id': '', 'Wife Name': '', 'Children': []}

dateTags = {'BIRT': 'Birthday', 'DEAT': 'Death', 'MARR': 'Marriage', 'DIV': 'Divorce'}

indiTags = {'NAME': 'Name', 'SEX': 'Gender', 'FAMC': 'Child', 'FAMS': 'Spouse'}
famTags = {'HUSB': ['Husband ID', 'Husband Name'], 'WIFE': ['Wife ID', 'Wife Name']}
monthNums = {'JAN': '01', 'MAR': '03', 'MAY': '05', 'JUL': '07', 'AUG': '08', 'OCT': '10', 'DEC': '12', 'APR': '04', 'JUN': '06', 'SEP' : '09','NOV': '11', 'FEB': '02'}

def gedcomParser():
    infile = open('testfile.ged', 'r')
    currId = "0"
    currDict = {}
    Date = ''
    for line in infile:
        if line[0] == '0':
            parts = zeroLine(line.split())
            if parts[1] == 'INDI':
                currId = parts[2]
                indis[currId] = {'Death': 'N/A', 'Alive': 'True', 'Spouse':
                                 'N/A/', 'Child': 'N/A'}
                currDict = indis
            if parts[1] == 'FAM':
                currId = parts[2]
                fams[currId] = {'Children': [], 'Divorce': 'N/A'}
                currDict = fams
        elif line[0] == '1':
            parts = oneLine(line.split())
            if parts[1] in dateTags.keys():
                Date = dateTags[parts[1]]
                if Date == 'Death':
                    indis[currId]['Alive'] = 'False'
            elif parts[1] in indiTags.keys():
                tag = indiTags[parts[1]]
                value = ''
                for s in parts[2:-1]:
                    value += s + ' '
                indis[currId][tag] = value[:-1]
            else:
                if parts[1] in famTags:
                    tags = famTags[parts[1]]
                    fams[currId][tags[0]] = parts[2]
                    fams[currId][tags[1]] = indis[parts[2]]['Name']
                else:
                    fams[currId]['Children'].append(parts[2])
        elif line[0] == '2':
            parts = twoLine(line.split())
            currDict[currId][Date] = parts[4] + '-' + monthNums[parts[3]] + '-' + parts[2]
        else:
            parts = line.split()
            parts.append('N')
    for i in indis:
        indis[i]['Age'] = getAge(i)

    individuals = collections.OrderedDict(sorted(indis.items()))
    prettyIndi = PrettyTable(["Id", "Name", "Birthday", 'Gender', 'Age',
                             'Alive', 'Death', 'Child', 'Spouse'])
    for k,v in individuals.items():
        row = list([k, v['Name'], v['Birthday'], v['Gender'], v['Age'], v['Alive'],
              v['Death'], v['Child'], v['Spouse']])
        prettyIndi.add_row(row)
    print('Individuals')
    print(prettyIndi)
    families = collections.OrderedDict(sorted(fams.items()))
    prettyFam = PrettyTable(["Id", 'Married', 'Divorced', 'Husband ID',
                             'Husband Name', 'Wife ID', 'Wife Name',
                             'Children'])
    for k,v in families.items():
        row = list([k, v['Marriage'], v['Divorce'], v['Husband ID'],
                             v['Husband Name'], v['Wife ID'], v['Wife Name'],
                             v['Children']])
        prettyFam.add_row(row)
    print('Families')
    print(prettyFam)

def getAge(Id):
    currDate = datetime.date.today()
    birth = list(map(int, indis[Id]['Birthday'].split('-')))
    birthDate = datetime.date(birth[0], birth[1], birth[2])
    days = 0
    if indis[Id]['Alive'] == 'False':
        death = list(map(int, indis[Id]['Death'].split('-')))
        currDate = datetime.date(death[0], death[1], death[2])
    days = (currDate-birthDate).days
    years = days/365
    return(str(int(years)))

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

"""def buildLine(arr):
    string = '<-- ' + arr[0] + '|' + arr[1] + '|' + arr[-1] + '|'
    if len(arr) > 3:
        string = string + arr[2]
        for i in arr[3:-1]:
            string = string + ' ' + i
    return string"""

gedcomParser()
