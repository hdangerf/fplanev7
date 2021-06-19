#V6
#
#
#
#Modified 03-May-2019
#Removed list all and added list month function
#Added links to airline and type
#Changing regular expression
#Added search for aircraft details
#Added length results added latest entries and duplicates
#Played about with styles
#Tied up and bufixes

from flask import Flask, render_template, request
import sqlite3 as sql
import re

import os
from subprocess import check_call
import sys

aircraftdblocation = '/home/pi/pi13-share/fplaneshared/aircraft.db'
symboldblocation = '/home/pi/pi13-share/fplaneshared/symbols.db'
masterlogfolderlocation = '/home/pi/pi13-share/fplaneshared/MasterLogText/'


def finddatefile(searchterm, dirstart):
    #e.g.  searchterm=20120903    dirstart=/home/pi/pishare/fplaneshared/MasterLogText
    print('*findfile ', searchterm)
    print(dirstart)
    searching = 0
    
    for root, dirs, files in os.walk(dirstart,followlinks=True,topdown=True):
        
        for element in files:       
            m = re.search(searchterm, element)
            # See if success.
            if m:
                foundfname = os.path.join(root, element)
                
                searching = 1
                break
    
    if searching == 0 :
        foundfname = None
        print('*findfile-Not Found')
    
    #foundfname = /home/pi/pishare/MasterLog/All 2014/201409/20140912 SpottingSeptember-2014.odt
    print('*findfile-END')
    return foundfname;

def searchforreg (searchtext, filetosearch):
    # e.g  searchtext = G-EUUW   filetosearch = 20110307 Spotting 7-Mar-2011.txt
    
    #modified 3-Jul-2017
    lines = [] # Declare an empty list named "lines"
    print('*searchforreg ',searchtext, '  in file  ', filetosearch)
    try:
        with open (filetosearch, 'rt') as in_file: # Open file lorem.txt for reading of text data.
            for line in in_file:      # For each line of text, store it in a string variable named "line", and 
                lines.append(line) # add that line to our list of lines. 
    except EnvironmentError: # parent of IOError, OSError 
        print('*searchforreg-Problem opening file  ', filetosearch)
        foundtext = ('Problem opening file')
        return foundtext;
      
    lineno = 0
    searching = 1
    found = 1
    in_file.close()
    
    for line in lines:

#Note the use of re.escape so that if your text has special characters, they won't be interpreted as such.
#e.g German Air Force 10+23
############################# 
        myregex = r'(.*)' + re.escape(searchtext)
        matchObj = re.search(myregex ,line,  re.I)
############################        

        #matchObj = re.search(r'(.*)%s' % searchtext ,line, re.I)
        #print(line)
    #matchObj = re.search(r'.*JY-AGR',line)
        if matchObj:
            #print('*searchforreg-Found at line number:- ', lineno)
            found = lineno
            searching = 0
        lineno += 1
    #print('*searchforreg-Lines in file  ', str(lineno))
    
    finished = 0
    freg = found
    
    while finished == 0:
        if lines[freg] in ['\n', '\r\n']:
            finished = 1
        else:
            freg = freg - 1
        #print(lines[freg])
        if freg == 0:
            finished = 1
    starttext = freg
    #####
    finished = 0
    freg = found
    while finished == 0:
        if lines[freg] in ['\n', '\r\n']:
            finished = 1
        else:
            freg = freg + 1 
        #print(lines[freg])
        if freg == lineno:
            finished = 1
    endtext = freg
    #print('SEARCHFORREG-Start text ', starttext, '   Endtext ', endtext)
    
    foundtext = ('')
    for i in range(starttext,endtext,1):
        foundtext = foundtext + lines[i]
    
    #print('>>>>  ',foundtext)
    # foundtext 14:53:05 .... then extracted details form text file
    print('*searchforreg END')
    return foundtext;

def extracttext (rows):
    rowslen = len(rows)
    print('*extracttext ', rowslen)
    #print(rows)
    #print(rowslen)
    
    if rowslen == 1:
        texttodisp=''
        for row in rows:
            texttodisp = row["reg"] + '  '+ row["date"]
            #print(texttodisp)
        
            dirstart = masterlogfolderlocation
                    #searchterm ='20160418.*'   row[date] in format 180417    
            searchterm = row["date"]
            stl = searchterm.split('/')
            searchterm = '20' + stl[2] + stl[1] + stl[0]
            reg = row["reg"]
                         #reg = 'ei-frb'
            foundfname = finddatefile(searchterm, dirstart)
            if foundfname is None:
                #print('***** File Not Found ......End')
                result = '*extracttext ***** Sorry File Not Found ......'
            else:

                foundfnametxt = foundfname.replace('odt', 'txt')
                
                #print('**** ', foundfnametxt)
               
                result = searchforreg (reg, foundfnametxt)
                if result is None:
                    #print('Reg Not Found')
                    result = '*extracttext Reg Not Found'
                else:
                    print('*extracttext - Here')
                    
    elif rowslen == 0:
        result = 'No text'
        #PUT IN DUMMY INFOR FOR DISPLAY
        rows = [0]
        rowlen = 1
    else:
        result = 'Nothing to display'
    print('*extracttext end with rowslen=', rowslen)       
    #print('EXTRACTTEXT-extracttext result = ', result)        
    return (rows, rowslen, result);



app = Flask(__name__)

@app.route('/')
def home():
   return render_template('home.html')


@app.route('/enternew')
def my_form():
    print('@enternew')
    return render_template("my-form.html")


@app.route('/lister', methods=['POST'])
def lister():
    
    text = request.form['text']
    print('@lister  ', text)
    #processed_text = str(text) + '%'
    processed_text = re.sub('-', '', str(text)) + '%'   #remove - from registration
    print('@lister  ', processed_text)
    con = sql.connect(aircraftdblocation)
    con.row_factory = sql.Row
    cur = con.cursor()
    if 'getreg' in request.form:
       #cur.execute("SELECT * FROM planes WHERE reg like ? ORDER BY reg", [processed_text])
       cur.execute("SELECT * FROM planes WHERE replace(reg, '-', '')  like ? ORDER BY reg", [processed_text])
       #Now compare reg with - removed  with databse reg with - removed
       #print('Reg')
    elif 'gettype' in request.form:
       cur.execute("SELECT * FROM planes WHERE type like ? ORDER BY reg", [processed_text])
       #print('Type')
    elif 'getairline' in request.form:
       cur.execute("SELECT * FROM planes WHERE airline like ? ORDER BY reg", [processed_text])
       #print('Airline')
    
    rows = cur.fetchall()
    rowslen = len(rows) 
    
    if rowslen == 0:
        result = 'No data found'
        #PUT IN DUMMY INFO FOR DISPLAY
        rows = [0]
        rowlen = 1
        
    else: 
        rows, rowslen, result = extracttext(rows)
    print('@lister-END----', rowslen)    
    return render_template("list.html",rows = rows, rowslen=rowslen, result = result)



@app.route('/listone/<string:sel_reg>')
def listone(sel_reg):
    print('@listone ', sel_reg)
    
    processed_text = sel_reg
    con = sql.connect(aircraftdblocation)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM planes WHERE reg like ? ORDER BY reg", [processed_text])

    rows = cur.fetchall()
    rowslen = len(rows)
    
    rows, rowslen, result = extracttext(rows)
    print('@listone-END----', rowslen)
    return render_template("list.html",rows = rows, rowslen=rowslen, result = result)
   # return render_template('query-output.html', name = processed_text)
   
@app.route('/listid/<string:sel_id>')
def listid(sel_id):
    print('@listid ', sel_id)
    
    processed_text = sel_id
    con = sql.connect(aircraftdblocation)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM planes WHERE id like ? ORDER BY id", [processed_text])

    rows = cur.fetchall()
    rowslen = len(rows)
    
    rows, rowslen, result = extracttext(rows)
    print('@listid-END----', rowslen)
    return render_template("list.html",rows = rows, rowslen=rowslen, result = result)
   # return render_template('query-output.html', name = processed_text)

   
@app.route('/listairline/<string:sel_airline>')
def listairline(sel_airline):
    print('@listairline')
    
    processed_text = sel_airline
    con = sql.connect(aircraftdblocation)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM planes WHERE airline like ? ORDER BY reg", [processed_text])

    rows = cur.fetchall()
    rowslen = len(rows)
    print('@listairline-here----', rowslen)
    rows, rowslen, result = extracttext(rows)
            
    return render_template("list.html",rows = rows, rowslen=rowslen, result = result)
   # return render_template('query-output.html', name = processed_text)
    
    
@app.route('/listtype/<string:sel_type>')
def listtype(sel_type):
    print('@listtype')
    
    processed_text = sel_type
    con = sql.connect(aircraftdblocation)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM planes WHERE type like ? ORDER BY reg", [processed_text])
    #print('Type')

    rows = cur.fetchall()
    rowslen = len(rows)
    
    rows, rowslen, result = extracttext(rows)
    print('@listtype-end')
            
    return render_template("list.html",rows = rows, rowslen=rowslen, result = result)
   # return render_template('query-output.html', name = processed_text)

    
@app.route('/sqlquery')
def my_form_sql():
    return render_template("my-form-sql.html")

@app.route('/sqlister', methods=['POST'])
def sqlister():
    text = request.form['text']
    print('@sqlister')
    processed_text = str(text)
    print(processed_text)
    con = sql.connect(aircraftdblocation)
    con.row_factory = sql.Row
    cur = con.cursor()
    sqlquery = ('SELECT * FROM planes WHERE '+ processed_text + ' ORDER BY reg')
    #print(sqlquery)
    cur.execute(sqlquery)
    
    rows = cur.fetchall()
    rowslen = len(rows)
    #print(rowslen)
    print('@sqlister-END')   
    return render_template("list.html",rows = rows, rowslen=rowslen)
        

@app.route('/list')
def list():
   print('@list')
   con = sql.connect(aircraftdblocation)
   con.row_factory = sql.Row
   
   cur = con.cursor()
   cur.execute("select * from planes")
   
   rows = cur.fetchall()
   rowslen = len(rows)
   
   return render_template("list.html",rows = rows, rowslen=rowslen)


@app.route('/lastpage')
def lastpage():
   print('@lastpage')
   con = sql.connect(aircraftdblocation)
   con.row_factory = sql.Row
   
   cur = con.cursor()
   cur.execute("select * from planes order by id desc limit 30")
   
   rows = cur.fetchall()
   rowslen = len(rows)
   print('LASTPAGE-',rowslen)
   return render_template("list.html",rows = rows, rowslen=rowslen)


@app.route('/duplicates')
def duplicates():
   print('@duplicates')
   con = sql.connect(aircraftdblocation)
   con.row_factory = sql.Row
   
   cur = con.cursor()
   cur.execute("select reg, count(*) from planes group by reg having count(*)>1")
   
   rows = cur.fetchall()
   rowslen = len(rows)
   print('DUPLICATES-',rowslen)

       ####Somewhere to put this temporarily
        
   #path = '/home/pi/pishare/fplaneshared/MasterLogText/All 2019/201904'
   #os.chdir(path)
   #cmdtorun = "python3 myconvertd.py"
   #check_call(cmdtorun, shell=True)
   dirstart = masterlogfolderlocation
   os.chdir(dirstart)

    #dirstart = os.getcwd()
   print('I am here  ', os.getcwd())
   searchterm = 'odt'
   print('Start Conversion')
   filecount = 0
   for root, dirs, files in os.walk(dirstart):
      for element in files:
        
         m = re.search(searchterm, element)
            # See if file an odt file
         if m:
            foundfname = os.path.join(element)
            fpconv =os.path.join(root,element)  #Full path file to convert
            print(element)
            fpconvm = '\''+ fpconv + '\''  #for command to run
                  
            fpopoutcmd = " --outdir " + '\''+root + '\''   #libre office to set output dir
                     
            cmdtorun = "/usr/bin/libreoffice --headless --convert-to txt:Text " + fpconvm + " " + fpopoutcmd
                    #print ('Running command', cmdtorun)
            check_call(cmdtorun, shell=True)
            filecount += 1
            print("*****  " + fpconv)
            
            if os.path.exists(fpconv):
               os.remove(fpconv)
               print('Deleted ' + fpconv) 
            else:
               print("The file does not exist")
         
            
                       
   print('Finished ', filecount, ' files converted')

#   odtfiles = os.listdir(dirstart)
#   for file in odtfiles:
#      if file.endswith(".odt"):
        #os.remove(os.path.join(dirstart, file))
#        print('Deleted ', os.path.join(dirstart, file))
     
    
         ####End Insert 
    
   return render_template("list.html",rows = rows, rowslen=rowslen)


@app.route('/entertype')
def symbol_form():
    print('@entertype')
    return render_template("symbol-form.html")



@app.route('/symlist', methods=['POST'])
def symlist():
    
    #text = request.form['text']
    #planetype='be9l'
    
    planetype  = request.form['text']
    print('@symlist ', planetype)
    
    con = sql.connect(symboldblocation)
    con.row_factory = sql.Row
    cur = con.cursor()

    cur.execute("SELECT * FROM symbols WHERE icaotype=:Id", {"Id": planetype.upper()})
    #cur.execute("SELECT * FROM symbols WHERE icaotype LIKE planetype")  
    rows = cur.fetchall()
    rowslen = len(rows)
    if rowslen == 0:
        print('@symlist  Type not found')
        symbol = 'Type not found'
    else:
        #print(rowslen)
        symbol = rows[0][1]

    print('@symlist returned symbol', symbol)
    
    return render_template("symbol-list.html",planetype = planetype, symbol=symbol)
   # return render_template('query-output.html', name = processed_text)

    
@app.route('/entermonth')
def month_form():
    print('@entermonth')
    return render_template("month-form.html")
    
    
@app.route('/mlister', methods=['POST'])
def mlister():
    text = request.form['text']
   
    print('@mlister  ', text)
    mmObj = re.match(r'^(\d{2})(\d{2})', text)
    processed_text = '%' + str(mmObj.group(1))+ '/' + str(mmObj.group(2))
    print('@mlister adjusted text ', processed_text)
    
    con = sql.connect(aircraftdblocation)
    con.row_factory = sql.Row
    cur = con.cursor()
    if 'getreg' in request.form:
       cur.execute("SELECT * FROM planes WHERE date like ? ORDER BY reg", [processed_text])
       #print('Reg')
    elif 'getdate' in request.form:
       cur.execute("SELECT * FROM planes WHERE date like ? ORDER BY date", [processed_text])
       #print('Date')
    elif 'gettype' in request.form:
       cur.execute("SELECT * FROM planes WHERE date like ? ORDER BY type", [processed_text])
       #print('Type')
    elif 'getairline' in request.form:
       cur.execute("SELECT * FROM planes WHERE date like ? ORDER BY airline", [processed_text])
       #print('Airline')
       

   
    rows = cur.fetchall()
    rowslen = len(rows)
    print(rowslen)   # for debug
    
    rows, rowslen, result = extracttext(rows)
            
    return render_template("list.html",rows = rows, rowslen=rowslen, result = result)



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
