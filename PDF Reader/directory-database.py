import PyPDF2
import re
import string
import sqlite3
import os
import csv

#doesnt work without pH being included as units
unitslist = ['g/l','w/w','w/v','pH','kg','ml','g/kg']

#returns a string of text from the PDF
def extracttext(pdfFileObj):
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    pageObj = pdfReader.getPage(0)
    p_text = pageObj.extractText()
    return(p_text)

#formats array into standard format
def format_spaces(a):  #a an array
    i = 0
    while i < len(a):
        if a[i] == '+':
            if (a[i+1].isspace() == True):
                del(a[i+1])
            if (a[i-1].isspace() == True):
                del(a[i-1])
        i = i + 1
    return a

#removes unwanted text before the table of pesticides 
def pesticidepages(p):
    return (p.split('Active ingredient', 1)[1])

#removes unwanted text after the table of pesticides 
def pesticidepages2(p):
    if (p.find('Other') != -1):
        return (p.split('Other', 1)[0])
    else:
        return (p.split('Note:', 1)[0])

#returns pesticides, functions and ingredients in standardised format
#works for: 2016, 2015, 2014, 2013, 2012, 2008, 2007, 2011, 2010, 2009
def standardise(w): #w an array
    z = []
    i = 1
    while (i < len(w)):
        if (w[i][0].isupper() == True):
            tradename = w[i]
            j = 1
            while (w[i+j].isspace() == False):
                tradename = tradename + w[i+j]
                j = j + 1
            i = i + j
            if not any(word in tradename for word in unitslist):
                z.append(tradename)
                k = 2
                function = w[i+1]
                while (w[i+k].isspace() == False):
                    function = function + w[i+k]
                    k = k + 1
                z.append(function)
                y = i + k + 2
                ingredients = w[y-1]
                while y < len(w):
                    if w[y][0].isupper() == True:
                        if ((w[y] == 'P') == True) or (w[y] == 'K') == True or (len(w[y]) > 1 and (w[y][0] + w[y][1] == 'P ') == True):
                            ingredients = ingredients + w[y]
                            y = y + 1
                        else:
                            break
                    else:
                       ingredients = ingredients + w[y]
                       y = y + 1
                z.append(ingredients)
            i = y
        else:
            i = i + 1
    return z

#returns and array in the format: [[year, tradename, function, ingredients]]
def tradename_array(array, year):
    i = 0
    tradenames = []
    while (i < len(array)):
        entry = [year, array[i], array[i+1].lower(), array[i+2]]
        tradenames.append(entry)
        i = i + 3
    return tradenames

#opens CSV with list of relevent pages of each yield book and their corresponding PDFs
with open("PesticidePagesCSV.csv") as f:
    reader = csv.reader(f)
    data = [r for r in reader]
    data.pop(0) # remove header

#list of relevent PDFs to search against
docs = []
for i in range(len(data)):
    docs.append(data[i][3])

#returns list [[year, tradename, function, ingredients],...] with all pesticides for all years 
final_list = []
fileList = os.listdir(r"\\salt\r3scans")
for fname in fileList:
    for i in range(2007,2017):
        year = str(i)
        if (fname.count("YieldBook"+year) == 1):
            subfiles = os.listdir(r"\\salt\\r3scans\\"+fname+"\\PDF")
            for sfname in subfiles:
                if sfname in docs:
                    pdfFileObj = open(r"\\salt\\r3scans\\"+fname+"\\PDF\\"+sfname, 'rb')
                    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
                    pageObj = pdfReader.getPage(0)
                    p_text = pageObj.extractText()
                    if (p_text.find('Active ingredient') != -1):
                        pdf = (pesticidepages(p_text)).splitlines()
                    else: 
                        if (p_text.find('Note:') != -1):
                            pdf = (pesticidepages2(p_text)).splitlines()
                        else:
                            pdf = p_text.splitlines()
                    table_list = standardise(format_spaces(pdf))
                    table_entry = tradename_array(table_list, year)
                    final_list += table_entry #added to for each document 
                  

"""                    
#putting into database
conn = sqlite3.connect('final_database.db') #name of the database being created
c = conn.cursor()

# Create table
c.execute('''CREATE TABLE tradenames
             (year real, tradename text, function text, ingredients text)''')

# Insert a rows of data
c.executemany('''INSERT INTO tradenames (year, tradename, function, ingredients)
                      VALUES (?, ?, ?, ?)''', final_list)

# Save (commit) the changes
conn.commit()

"""

