#Authors: Max Remetz, Adam Bannat, Kirk Visser, Shashank Mysore Bhagwan
#We pledge our honor that we have abided by the Stevens Honor System
#Date: 2/6/2018

import os
import collections
import datetime
import dateutil.relativedelta
from prettytable import PrettyTable

#Dictionaries to store unsorted individuals and families
indis = {}
fams = {}

#dictionaries holding tags and respective values for easier handling of dicts
dateTags = {"BIRT": "Birthday", "DEAT": "Death", "MARR": "Marriage", "DIV": "Divorce"}
indiTags = {"NAME": "Name", "SEX": "Gender", "FAMC": "Child", "FAMS": "Spouse"}
famTags = {"HUSB": ["Husband ID", "Husband Name"], "WIFE": ["Wife ID", "Wife Name"]}
monthNums = {"JAN": "01", "MAR": "03", "MAY": "05", "JUL": "07", "AUG": "08", "OCT": "10", "DEC": "12", "APR": "04", "JUN": "06", "SEP" : "09","NOV": "11", "FEB": "02"}

def afterDate(d1, d2):
	if not isinstance(d1, datetime.date):
		d1 = datetime.datetime.strptime(d1, '%d %b %Y').date()
	if not isinstance(d2, datetime.date):
		d2 = datetime.datetime.strptime(d2, '%d %b %Y').date()
	if d1 > d2:
		return 0 #invalid date
	elif d1 < d2:
		return 1
	else:
		return 0
    
    
def days_difference(d1, d2, type):
	if afterDate(d1,d2):
		return -1
	else:
		typeDict = {"years": 365, "weeks": 7, "months": 30.4, "days": 1} #returning months,days and years
		return str(((d2-d1)/typeDict[type]).days)

printErrors = []

#Main function which parses through GEDCOM file, stores individuals and
#families in dictionaries, sorts dictionaries into collections
#then finally pretty prints collections
def gedcomParser():
    infile = open("badTree.ged", "r")
    currId = "0"
    currDict = {}
    Date = ""
    for line in infile:
        if line[0] == "0":
            parts = zeroLine(line.split())
            if parts[1] == "INDI":
                currId = parts[2]
                #US22
                if currId in indis.keys():
                    printErrors.append("ERROR: INDIVIDUAL: US22: id " + currId + " already found. Previous individual has been replaced.")
                indis[currId] = {"Death": "N/A", "Alive": "True", "Spouse":
                                 "N/A/", "Child": "N/A"}
                currDict = indis
            if parts[1] == "FAM":
                currId = parts[2]
                fams[currId] = {"Children": [], "Divorce": "N/A"}
                currDict = fams
        elif line[0] == "1":
            parts = oneLine(line.split())
            if parts[1] in dateTags.keys():
                Date = dateTags[parts[1]]
                if Date == "Death":
                    indis[currId]["Alive"] = "False"
            elif parts[1] in indiTags.keys():
                tag = indiTags[parts[1]]
                value = ""
                for s in parts[2:-1]:
                    value += s + " "
                indis[currId][tag] = value[:-1]
            else:
                if parts[1] in famTags:
                    tags = famTags[parts[1]]
                    fams[currId][tags[0]] = parts[2]
                    fams[currId][tags[1]] = indis[parts[2]]["Name"]
                else:
                    fams[currId]["Children"].append(parts[2])
        elif line[0] == "2":
            parts = twoLine(line.split())
            dateStr = parts[4] + '-' + monthNums[parts[3]] + '-' + parts[2]
            currDict[currId][Date] = dateStr
            printErrors.append(dateHasPassed(dateStr, currDict, currId, Date))
        else:
            parts = line.split()
            parts.append("N")
    for i in indis:
        indis[i]["Age"] = getAge(i)

    individuals = collections.OrderedDict(sorted(indis.items()))
    prettyIndi = PrettyTable(["Id", "Name", "Birthday", "Gender", "Age",
                             "Alive", "Death", "Child", "Spouse"])
    for k,v in individuals.items():
        row = list([k, v["Name"], v["Birthday"], v["Gender"], v["Age"], v["Alive"],
              v["Death"], v["Child"], v["Spouse"]])
        prettyIndi.add_row(row)
    print("Individuals")
    print(prettyIndi)
    families = collections.OrderedDict(sorted(fams.items()))
    prettyFam = PrettyTable(["Id", "Married", "Divorced", "Husband ID",
                             "Husband Name", "Wife ID", "Wife Name",
                             "Children"])
    for k,v in families.items():
        row = list([k, v["Marriage"], v["Divorce"], v["Husband ID"],
                             v["Husband Name"], v["Wife ID"], v["Wife Name"],
                             v["Children"]])
        prettyFam.add_row(row)
    print("Families")
    print(prettyFam)

    #Invalid date errors
    for err in printErrors:
        if len(err) > 0:
            print(err)

    #Individual Checks
    for k,v in individuals.items():
        birthBeforeDeath(k, v["Birthday"], v["Death"])
        ageLessThanOneFifty(k, v["Age"])
        

    #Family checks
    for k,v in families.items():
        marriageBeforeDivorce(k, v["Marriage"], v["Divorce"])
        marriageBeforeDeath(k, v['Marriage'],v['Husband ID'], individuals[v['Husband ID']]['Death'], v['Wife ID'], individuals[v['Wife ID']]['Death'])
        divorceBeforeDeath(k, v['Divorce'], v['Husband ID'], individuals[v['Husband ID']]['Death'], v['Wife ID'], individuals[v['Wife ID']]['Death'])
        birthBeforeMarriage(k, v['Marriage'], v['Husband ID'], individuals[v['Husband ID']]['Birthday'], v['Wife ID'], individuals[v['Wife ID']]['Birthday'])
        
        for child in v['Children']: 
            birthBeforeMarriageOfParents(v['Husband ID'], v['Wife ID'], v['Marriage'],child, individuals[child]['Birthday'])
            birthBeforeDeathOfParent(v['Husband ID'], individuals[v['Husband ID']]['Death'], v['Wife ID'], individuals[v['Wife ID']]['Death'], child,individuals[child]['Birthday'])
            parentsAgeCheck(v['Husband ID'], individuals[v['Husband ID']]['Birthday'], v['Wife ID'], individuals[v['Wife ID']]['Birthday'], child, individuals[child]['Birthday'])
     
     
        husbWifeNotSiblings(k, v['Husband ID'], indis[v['Husband ID']]['Child'], v['Wife ID'], indis[v['Wife ID']]['Child'])
        husbWifeNotCousins(k, v['Husband ID'], indis[v['Husband ID']]['Child'], v['Wife ID'], indis[v['Wife ID']]['Child'])



#Function to calculate age of Individual
def getAge(Id):
    currDate = datetime.date.today()
    birth = list(map(int, indis[Id]["Birthday"].split("-")))
    birthDate = datetime.date(birth[0], birth[1], birth[2])
    days = 0
    if indis[Id]["Alive"] == "False":
        death = list(map(int, indis[Id]["Death"].split("-")))
        currDate = datetime.date(death[0], death[1], death[2])
    days = (currDate-birthDate).days
    years = days/365
    return(str(int(years)))

#Function to evaluate and reformat 0 level lines
def zeroLine(ln):
    if len(ln) > 2:
        if ln[2] == "INDI" or ln[2] == "FAM":
            return [ln[0], ln[2], ln[1], "Y"]
        elif ln[1] == "NOTE":
            ln.append("Y")
            return ln
        else:
            ln.append("N")
            return ln
    elif ln[1] == "HEAD" or ln[1] == "TRLR":
        if len(ln) == 2:
            ln.append("Y")
            return ln
        else:
            ln.append("N")
            return ln
    else:
        ln.append("N")
        return ln

#Function to evaluate and reformat 1 level lines
def oneLine(ln):
    if ln[1] == "NAME":
        if len(ln) == 2 or (len(ln) > 2 and ln[-1][0] + ln[-1][-1] != "//"):
            ln.append("N")
            return ln
        ln.append("Y")
        return ln
    if ln[1] == "SEX":
        if len(ln) == 3 and (ln[2] == "M" or ln[2] == "F"):
            ln.append("Y")
            return ln
        ln.append("N")
        return ln
    if ln[1] == "BIRT" or ln[1] == "DEAT" or ln[1] == "MARR" or ln[1] == "DIV":
        if len(ln) == 2:
            ln.append("Y")
            return ln
        ln.append("N")
        return ln
    if ln[1] == "FAMC" or ln[1] == "FAMS" or ln[1] == "HUSB" or ln[1] == "WIFE" or ln[1] == "CHIL" :
        if len(ln) == 3:
            ln.append("Y")
            return ln
        ln.append("N")
        return ln
    ln.append("N")
    return ln

#Function to evaluate and reformat 2 level lines
def twoLine(ln):
    months = ["JAN", "MAR", "MAY", "JUL", "AUG", "OCT", "DEC", "APR", "JUN",
              "SEP","NOV", "FEB"]
    if ln[1] == "DATE" and len(ln) == 5:
        if ln[3] not in months or int(ln[2]) > 31 or int(ln[2]) < 1:
            ln.append("N")
            return ln
        elif int(ln[2]) == 31 and ln[3] not in months[0:]:
            ln.append("N")
            return ln
        elif int(ln[2]) > 29 and ln[3] == "FEB":
            ln.append("N")
            return ln
        else:
            ln.append("Y")
            return ln
    ln.append("N")
    return ln

#US01: Function to check if a date is before the current date
def dateHasPassed(date, currDict, currId, dateType):
    currDate = datetime.date.today()
    checkDate = list(map(int, date.split('-')))
    if (datetime.date(checkDate[0], checkDate[1], checkDate[2]) -
        currDate).days > 0:
        if(currDict == fams):
            return("Error: Invalid "+ dateType + "for FAMILY" + currId + ": " + date + " has not happened yet as of " + str(datetime.date.today()))
        if(currDict == indis):
            return("Error: Invalid "+ dateType + "for INDIVIDUAL" + currId + ": " + date + " has not happened yet as of " + str(datetime.date.today()))
    return ""

#US02: Function to check that birth is before marriage
def birthBeforeMarriage(k, marriage, husbandId, husbandBirth, wifeId, wifeBirth):
    #Do not compare if null
    if marriage == "N/A":
        return 0

    error = 0
    #check husband birth
    if husbandBirth != "N/A" and husbandBirth > marriage:
        print("ERROR: FAMILY: US06: " + str(k) + ": Married " + str(marriage) + \
        " before husband's (" + husbandId + ") birth on " + str(husbandBirth))
        error = 1
    #check wife birth
    if wifeBirth != "N/A" and wifeBirth > marriage:
        print("ERROR: FAMILY: US06: " + str(k) + ": Married " + str(marriage) + \
        " before wife's (" + wifeId + ") birth on " + str(wifeBirth))
        error = 1

    return error


#US03: Function to check that birth comes before death
def birthBeforeDeath(k, birthday, death):
    #Do not compare if null
    if death == "N/A" or birthday == "N/A":
        return 0

    if death < birthday:
        print ("ERROR: INDIVIDUAL: US03: " + str(k) + " Died " + str(death) + " before Born " + str(birthday))
        return 1
    else:
        return 0

#US04 -- marriage before divorce
#same as US03, may want to simpley combined these stories to create one
def marriageBeforeDivorce(familyItem, marriage,divorce ):
    status_na = "N/A"

    if marriage == "N/A" or divorce == "N/A":
            return 0
    
    elif marriage > divorce:
        print ("ERROR: FAMILY: USO4: " + str(familyItem) + " Divorced " + str(divorce) + " before Married " + str(marriage))
        return 1

    else:
        return 0

#US05
def marriageBeforeDeath(familyItem, marriage, husbandId, husbandDeath, wifeId, wifeDeath):
    if marriage == "N/A":
        return 0
    
    binary_bol = 0
    if husbandDeath != "N/A" and husbandDeath < marriage:
        print("ERROR: FAMILY: US05: " + str(familyItem) + ": marriage " + str(marriage) +  "after husband's (" + husbandId + ") death on " + str(husbandDeath))
        binary_bol = 1
    if  wifeDeath != "N/A" and wifeDeath < marriage: 
        print("Error: FAMILY: US05 " + str(familyItem) + ": marriage " + str(marriage) + "after wife's (" + wifeId + ") death on " + str(wfieDeath))
        binary_bol = 1 

    return binary_bol



#US06
def divorceBeforeDeath(k, divorce, husbandId, husbandDeath, wifeId, wifeDeath):
    #Do not compare if null
    if divorce == "N/A":
        return 0

    error = 0
    #check husband death
    if husbandDeath != "N/A" and husbandDeath < divorce:
        print("ERROR: FAMILY: US06: " + str(k) + ": Divorced " + str(divorce) + \
        " after husband's (" + husbandId + ") death on " + str(husbandDeath))
        error = 1
    #check wife death
    if wifeDeath != "N/A" and wifeDeath < divorce:
        print("ERROR: FAMILY: US06: " + str(k) + ": Divorced " + str(divorce) + \
        " after wife's (" + wifeId + ") death on " + str(wifeDeath))
        error = 1

    return error


#US07
def ageLessThanOneFifty(k, age):
    if age == "N/A":
        return 0

    if int(age) > 150 or int(age) < 0:
        print("ERROR: INDIVIDUAL: US07: " + str(k) + " age " + str(age) + " is older than 150 or less than 0.")
        return 1
    else:
        return 0


#US08
def birthBeforeMarriageOfParents( husbandId, wifeId, marriage, childId, childBirthday):
    
    err = 0
    
    if marriage == "N/A" or childId == "N/A":
        return err

    if marriage > childBirthday:
        print("ERROR: Family: US09: Child: " + childId + "'s birthday is before the marriage of husband " + husbandId +" and wife " + wifeId)
        err = 1

    return err 

#US09 Parents not too old 
# Mother's death should after the birth of the child
# Father's death should be after at least 9 months before the birth of the child
def birthBeforeDeathOfParent(husbandId, husbandDeath, wifeId, wifeDeath, childId, childBirthday):
     
    err = 0

    if childId == "N/A" or (husbandDeath == "N/A" and wifeDeath == "N/A"):
        return err

    if not (wifeDeath == "N/A") and wifeDeath < childBirthday:
        err = 1 
        print("ERROR: Family: US09: Child: " + childId + "'s birthday is after the death of  thier mother " + wifeId)


    if not (husbandDeath == "N/A") and (datetime.datetime.strptime(husbandDeath, '%Y-%m-%d') + dateutil.relativedelta.relativedelta(months=9)) < datetime.datetime.strptime( childBirthday, '%Y-%m-%d')  :
        err = 1
        print("ERROR: Family: US09:  Child: " + childId + "'s birthday is more than 9 months after the death of their father " + husbandId)
         
    return err

#US12 Parents
# Mother should be less than 60 years older than her children and father should be less than 80 years older than his children
def parentsAgeCheck(husbandId, husbandBirth, wifeId, wifeBirth, childId, childBirth):
    err = 0 

    if childId == 'N/A' or husbandId == 'N/A' or wifeId == 'N/A':
        return 0

    date_type_husbandBirth = datetime.datetime.strptime(husbandBirth, '%Y-%m-%d')
    date_type_wifeBirth = datetime.datetime.strptime(wifeBirth, '%Y-%m-%d')
    date_type_childBirth = datetime.datetime.strptime(childBirth,'%Y-%m-%d' )


    if dateutil.relativedelta.relativedelta(date_type_husbandBirth, date_type_childBirth).years >= 80:
        err = 1
        print("ERROR: US12: Father too old")

    if dateutil.relativedelta.relativedelta(date_type_wifeBirth, date_type_childBirth).years >= 60:
        err = 1
        print("ERROR: US12: Mother too old")

    return err
#US18
def husbWifeNotSiblings(k, husbID, husbFam, wifeID, wifeFam):
        if husbID != 'N/A' and husbID == wifeID:
                print('ERROR: FAMILY: ' + k + ": husband (" + husbID + ") and wife (" + wifeID + ") are siblings.")
                return 1
        else:
                return 0

def husbWifeNotCousins(k, husbID, husbFam, wifeID, wifeFam):
        error = 0
        if husbFam != 'N/A' and wifeFam != 'N/A':
                hDad = fams[husbFam]['Husband ID']
                hMom = fams[husbFam]['Wife ID']
                wDad = fams[wifeFam]['Husband ID']
                wMom = fams[wifeFam]['Wife ID']
                hDadFam = indis[hDad]['Child']
                hMomFam = indis[hMom]['Child']
                wDadFam = indis[wDad]['Child']
                wMomFam = indis[wMom]['Child']
                if hDadFam == wDadFam and hDadFam != 'N/A':
                        error = 1
                if hDadFam == wMomFam and hDadFam != 'N/A':
                        error = 1
                if hMomFam == wDadFam and hMomFam != 'N/A':
                        error = 1
                if hMomFam == wMomFam and hMomFam != 'N/A':
                        error = 1
        if error == 1:
                print('ERROR: FAMILY: '+ k + " Husband (" + husbID +") and wife (" + wifeID + ") are first cousins and married")
        return error

gedcomParser()
