from flask import Flask, request, render_template
from datetime import datetime, date
from os import listdir
from os.path import isfile, join, isdir
from flask_sqlalchemy import SQLAlchemy
import sys
import hashlib
import time

app = Flask(__name__)
app.config["DEBUG"] = True

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="Borysk5",
    password="SQLPassword",
    hostname="Borysk5.mysql.eu.pythonanywhere-services.com",
    databasename="Borysk5$MyDatabase",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Comment(db.Model):

    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(4096))


class LegionDB(db.Model):
    __tablename__ = "legion"
    id = db.Column(db.Integer, primary_key=True)
    series = db.Column(db.String(4096))
    URLpath = db.Column(db.String(4096))
    legions = db.relationship("LegionsDB",backref="legion")

class LegionsDB(db.Model):
    __tablename__ = "legions"
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer)
    month = db.Column(db.Integer)
    day = db.Column(db.Integer)
    value = db.Column(db.Integer)
    legion_id = db.Column(db.Integer, db.ForeignKey("legion.id"))
    def getdate(self):
        mv = Data(self.year,self.month,self.day)
        return mv
    def print(self):
        global dateformat
        if(dateformat == 'ymd'):
            s = str(self.year)+'.'+str(self.month)+'.'+str(self.day)
        elif(dateformat == 'dmy'):
            s = str(self.day)+'.'+str(self.month)+'.'+str(self.year)
        elif(dateformat == 'mdy'):
            s = str(self.month)+'.'+str(self.day)+'.'+str(self.year)
        elif(dateformat == 'mdy'):
            s = str(self.month)+'.'+str(self.day)+'.'+str(self.year)
        return s
#db.create_all()

class Data:
	def __init__(self, year, month, day):
		self.year = year
		self.day = day
		self.month = month
	def print(self):
		global dateformat
		if(dateformat == 'ymd'):
			s = self.year+'.'+self.month+'.'+self.day
		elif(dateformat == 'dmy'):
			s = self.day+'.'+self.month+'.'+self.year
		elif(dateformat == 'mdy'):
		    s = self.month+'.'+self.day+'.'+self.year
		elif(dateformat == 'mdy'):
		    s = self.month+'.'+self.day+'.'+self.year

		return s

class Legion:
	def __init__(self, date, number):
		g = date.strip()
		print(g)
		x = g.split('.')
		assert(len(x)==3)
		global dateformat
		if(dateformat == 'dmy'):
			self.date=Data(x[2],x[1],x[0])
		elif(dateformat == 'ymd'):
			self.date=Data(x[0],x[1],x[2])
		elif(dateformat == 'mdy'):
			self.date=Data(x[1],x[2],x[0])
		elif(dateformat == 'det'):
			if(len(x[0])==4):
				dateformat = 'ymd'
				self.date=Data(x[0],x[1],x[2])
			elif(len(x[2])==4):
				dateformat = 'dmy'
				self.date=Data(x[2],x[1],x[0])
			elif(len(x[1])==4):
				dateformat = 'mdy'
				self.date=Data(x[1],x[2],x[0])
		self.number = number

class Legions:
  def __init__(self, legions, path):
    self.legions = legions
    self.path = path

def datedifference(x, y):
    if int(x.year)>int(y.year): return bool(1);
    elif int(y.year)>int(x.year): return bool(0);
    if int(x.month)>int(y.month): return bool(1);
    elif int(y.month)>int(x.month): return bool(0);
    if int(x.day)>int(y.day): return bool(1);
    elif int(y.day)>int(x.day): return bool(0);
    return bool(0);

    #return int(x.day)+30*int(x.month)+365*int(x.year)-(int(y.day)+30*int(y.month)+365*int(y.year))

def datascrepancy(x, y):
	x=int(x)
	y=int(y)
	if(abs(x-y)/x < 0.2): return bool(0)
	else: return bool(1)

#h = dict()
dateformat='ymd'
appending=bool(0)
updating=bool(0)
separator=''

def splitline(line):
    if separator == '':
        h = [',',';',':','_','/','\\','|','||',' ','  ']
        g = list()
        for c in h:
            g = line.split(c)
            if(len(g)==3):
                for i in range(3):
                    g[i] = g[i].strip()
                if len(g[0])*len(g[1])*len(g[2]) > 0: return g
        return g
    else:
        g = line.split(separator)
        if(len(g)==3):
                for i in range(3):
                    g[i] = g[i].strip()
                if len(g[0])*len(g[1])*len(g[2]) > 0: return g
        return list()

def readfromfolder(path):
	onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
	for i in onlyfiles:
		if i!="log.txt" and i[-4:]==".txt":
			f = open(join(path,i), "rt")
			myline = f.readline()
			b = []
			bdb = []
			l = ''
			while(myline):
				g = myline.strip()
				x = splitline(g)
				if(len(x)==3):
					l = x[0]
					#b.append(Legion(x[1],x[2]))
					legion = Legion(x[1],x[2])
					series = LegionsDB(year=legion.date.year,month=legion.date.month,day=legion.date.day,value=x[2])
					bdb.append(series)
				myline = f.readline()
			if len(l)>0:
				#h[l] = Legions(b,join(path,i))
				seria = LegionDB(series=l,URLpath=join(path,i))
				seria.legions = bdb
				db.session.add(seria)
				db.session.commit()

	onlyfolders = [f for f in listdir(path) if isdir(join(path, f))]
	for j in onlyfolders:
		readfromfolder(join(path,j))

@app.route("/log")
def log():
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
        assert dateformat=='dmy' or dateformat=='ymd' or dateformat=='mdy' or dateformat=='det'
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
                    new_vc = LegionsDB(day=vc.date.day,month=vc.date.month,year=vc.date.year,value=x[2])
                    hg = LegionDB.query.filter_by(series=x[0]).first()
                    if hg is not None:
				   # if x[0] in h.keys():
                        if datedifference(hg.legions[-1].getdate(),vc.date):
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
                    new_jj = LegionsDB(day=jj.date.day,month=jj.date.month,year=jj.date.year,value=x[2])
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