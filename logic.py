from flask import Flask
from datetime import datetime
from os import listdir
from os.path import isfile, join, isdir
from flask_sqlalchemy import SQLAlchemy
import csv
import pandas as pd
from multiprocessing import Pool

app = Flask(__name__)
app.config["DEBUG"] = True

separator=","
dateformat='%Y.%m.%d'

serieslist = dict()
pandaseries = pd.DataFrame()

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

class DataseriesDB(db.Model):
    __tablename__ = "legion"
    id = db.Column(db.Integer, primary_key=True)
    series = db.Column(db.String(4096))
    URLpath = db.Column(db.String(4096))
    legions = db.relationship("DataentryDB",backref="legion",lazy='subquery')

class DataentryDB(db.Model):
    __tablename__ = "legions"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    value = db.Column(db.Integer)
    legion_id = db.Column(db.Integer, db.ForeignKey("legion.id"))
    def getdate(self):
        return self.date
    def print(self):
        global dateformat
        return self.date.strftime(dateformat)

def DateTime(date):
    date_string =date.strip()
    x = date.split('.')
    assert(len(x)==3)
    global dateformat
    z = datetime.strptime(date_string, dateformat)
    return z


def readfromfolder(path):
	onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
	for i in onlyfiles:
		if i.endswith(".csv"):
		    with open(join(path,i)) as csv_file:
		        csv_reader = csv.reader(csv_file, delimiter=separator)
		        bdb = []
		        l = ''
		        for row in csv_reader:
		            if(len(row))==3:
		                l = row[0]
		                series = DataentryDB(date=DateTime(row[1]),value=row[2])
		                bdb.append(series)
		        seria = DataseriesDB(series=l,URLpath=join(path,i))
		        seria.legions = bdb
		        db.session.add(seria)
		        db.session.commit()
	onlyfolders = [f for f in listdir(path) if isdir(join(path, f))]
	for j in onlyfolders:
		readfromfolder(join(path,j))


def readfromfolderpandas(path):
	onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
	pandasframe = pd.DataFrame(columns = ['Series', 'Date', 'Value'])
	#pandasframe.set_index('Date')
	global pandaseries
	for i in onlyfiles:
		if i.endswith(".csv"):
		    df = pd.read_csv(join(path,i),header=None,index_col=False)
		    df.columns = ['Series', 'Date', 'Value']
		    pandasframe = pd.concat([pandasframe,df])
		    nazwa = df['Series'].iloc[0]
		    serieslist[nazwa]=join(path,i)
	onlyfolders = [f for f in listdir(path) if isdir(join(path, f))]
	for j in onlyfolders:
		readfromfolderpandas(join(path,j))
	return pandasframe

def readfromfolderog(path):
	onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
	for i in onlyfiles:
		if i.endswith(".csv"):
		    with open(join(path,i)) as csv_file:
		        csv_reader = csv.reader(csv_file, delimiter=separator)
		        bdb = []
		        l = ''
		        for row in csv_reader:
		            if(len(row))==3:
		                l = row[0]
		                entry = Dataentry(date=DateTime(row[1]),value=row[2])
		                bdb.append(entry)
		        seria = Dataseries(legions=bdb,id=l,URLpath=join(path,i))
		        global serieslist
		        serieslist[l]=seria
	onlyfolders = [f for f in listdir(path) if isdir(join(path, f))]
	for j in onlyfolders:
		readfromfolderog(join(path,j))

def datascrepancy(x, y):
	x=int(x)
	y=int(y)
	if(abs(x-y)/x < 0.2): return bool(0)
	else: return bool(1)

def saveline(i):
    g = open(i.URLpath, "w")
    g.write(i.series+','+i.legions[0].print()+','+str(i.legions[0].value))
    if(len(i.legions)>1):
        for j in i.legions[1:]:
            g.write('\n'+i.series+','+j.print()+','+str(j.value))
    g.close()

def savetofiles(zxh):
    with Pool() as pool:
        pool.map(saveline,zxh)

def savelinepandas(x,url):
        x.to_csv(url,header=False,index=False)

def savetofilespandas(arg1):
    dfs = arg1.groupby('Series')
    for x in dfs:
        url = serieslist[x[0]]
        savelinepandas(x[1],url)

class Dataseries:
  def __init__(self, id, legions, URLpath):
    self.series = id
    self.legions = legions
    self.URLpath = URLpath

class Dataentry:
  def __init__(self, date, value):
    self.date = date
    self.value = value
  def print(self):
    return self.date.strftime("%Y.%m.%d")