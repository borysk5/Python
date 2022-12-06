from flask import Flask, request, render_template
from datetime import datetime
from os import listdir
from os.path import isfile, join, isdir
from flask_sqlalchemy import SQLAlchemy
from logic import Legion, LegionDB, LegionsDB, app, db, splitline, datascrepancy, dateformat, appending, updating
import sys
import hashlib
import time
import csv



#db.create_all()


#h = dict()



@app.route("/log")
def log():
    db.create_all()
    f = open("mysite/dataseries/log.txt", "r")
    page= ""
    myline = f.readline()
    while(myline):
        page +=myline+"\n<br>"
        myline = f.readline()
    return page

@app.route("/data/<id>")
def data(id):
    global h
    mypath = "mysite/dataseries"
    #readfromfolder(mypath)
    page= ""
    zh = LegionDB.query.filter_by(series=id).first()
    if zh is not None:
        for i in zh.legions:
            page+=id+' '+i.print()+' '+str(i.value)+"<br>\n"
    else: page += "No such series"
    return page

@app.route("/test")
def test():
    page= "TEST1"
    #mypath = "mysite/dataseries"
    #readfromfolder(mypath)
    #seria = LegionDB(series="i",URLpath="z")
    ##db.session.add(seria)
    #serie = LegionsDB(year=1,month=2,day=3,value=5)
    #seria.legions.append(serie)
    #db.session.add(seria)
    #legion = LegionDB.query.all()
    #for i in legion:
        #seria = LegionDB(series=i,URLpath=h[i].path)
    #    for j in i.legions:
            #serie = LegionsDB(year=j.date.year,month=j.date.month,day=j.date.day,value=j.number)
            #db.session.add(seria)
            #seria.legions.append(serie)
    #        page += "<br>" + i.series + ' ' + str(j.year) + ' ' + i.URLpath + str(j.value) + "\n"
       # db.session.add(seria)
    #comments=Comment.query.all()
    #for c in comments:
    #    page += c.content;
    #comment = Comment(content="komentarz")
    #db.session.add(comment)
   # db.session.commit()
    z = LegionDB.query.filter_by(series="SYM1").first().id
    new_vc = LegionsDB(year=12,month=10,day=20222,value=7)
    fg = LegionDB.query.with_entities(LegionDB.series)
    for f in fg:
        page += f.series;
    #z.legions.append(new_vc)
    db.session.commit()
    #page += str(z)
    return page

@app.route("/serwer", methods=['GET','POST'])
def main():
    args = request.form
    global separator
    if (not args.get("automat")) and args.get("type"):
        separator = args.get("type")
    global appending
    appending=bool(0)
    global updating
    updating=bool(0)
    global dateformat
    if "dateformat" in args:
        dateformat = args.get("dateformat")
        assert dateformat=='dmy' or dateformat=='ymd' or dateformat=='mdy'
    if args.get("appending"):
        appending = bool(1)
    if args.get("updating"):
        updating = bool(1)
	#if args.get("quantity"):
	#	page+=args.get("quantity")
    mypath = "mysite/dataseries"
    checked = ['','','','']
    if(dateformat=="dmy"):checked[0]='checked'
    elif(dateformat=="ymd"):checked[1]='checked'
    elif(dateformat=="mdy"):checked[2]='checked'
    elif(dateformat=="det"):checked[3]='checked'
    checked1 = ['','']
    if appending: checked1[0]='checked'
    if updating: checked1[1]='checked'
    #readfromfolder(mypath)


    #readfromfolder(mypath)

	#if(len(request.files)>0):
    files = []
    if(args.get("default")):
        files.append(open("mysite/insert.txt","r"))
    elif(len(request.files)>0):
        files = request.files.getlist('myfile')

    #legion = LegionDB.query.all()

    g = open("mysite/dataseries/log.txt", "a")

    g.write('\n'+str(datetime.now()))
    start = time.time()
    for f in files:
		#if(f.filename[-4:]=='.txt'):
		#myline = str(f.readline().strip(), 'utf-8')
        if(args.get("default")):
            myline = f.readline().strip()
        else:
            myline = str(f.readline().strip(), 'utf-8')
        while(myline):
            x = splitline(myline)
            if(len(x)!=3):
                g.write('\n'+'Data mismatch. Wrong format of data series in line: "'+myline+'"');
            else:
                if(appending):
                    vc = Legion(x[1],x[2]) #date,number
                    new_vc = LegionsDB(date=vc.date,value=x[2])
                    hg = LegionDB.query.filter_by(series=x[0]).first()
                    if hg is not None:
				   # if x[0] in h.keys():
                        if (hg.legions[-1].getdate()>vc.date):
                            g.write('\n'+'Data mismatch. New date '+new_vc.print() +' is not chronological')
                        else:
				            #h[x[0]].legions.append(vc)
                            zz = LegionDB.query.all()
                            LegionDB.query.filter_by(series="SYM1").first().legions.append(new_vc)
                            db.session.commit()
                            g.write('\n'+'Added new line: '+x[0]+', '+x[1]+', '+x[2])
                    else:
				        #b = []
				        #b.append(vc)
				        #h[x[0]] = Legions(b,join(mypath,x[0]))
                        new_h = LegionDB(series=x[0],URLpath=join(mypath,x[0]))
                        new_h.legions.append(new_vc)
                        db.session.add(new_h)
                        db.session.commit()
                        g.write('\n'+'Added new line: '+x[0]+', '+x[1]+', '+x[2])
                if(updating):
                    jj = Legion(x[1],x[2])
                    new_jj = LegionsDB(date=jj.date,value=x[2])
					#g.write('\n'+str(datetime.now()))
                    for xx in LegionDB.query.filter_by(series=x[0]).first().legions:
                        if(xx.print() == new_jj.print()):
                            if(datascrepancy(xx.value,new_jj.value)):
                                g.write('\n'+'Data mismatch in: '+x[0]+' '+xx.print()+'. New value ('+str(new_jj.value)+') too different from '+str(xx.value));
                            else:
                                v = xx.value
                                xx.value = new_jj.value
                                g.write('\n'+'In '+x[0]+' '+xx.print()+' replaced '+str(v)+' with new value: '+ str(new_jj.value));
                            break
                    db.session.commit()
            if(args.get("default")):
                myline = f.readline().strip()
            else:
                myline = str(f.readline().strip(), 'utf-8')
        for i in LegionDB.query.all():
            g = open(i.URLpath, "w")
            for j in i.legions[:-1]:
                g.write(i.series+', '+j.print()+', '+str(j.value)+'\n')
            g.write(i.series+', '+i.legions[-1].print()+', '+str(i.legions[-1].value))

    g.close()
    end = time.time()
    passed = end - start


	#page += display(h)
    return render_template("index.html", checked=checked, passed = passed,  checked1=checked1,legion=LegionDB.query.all())
	#return page;