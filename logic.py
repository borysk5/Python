from flask import Flask, request, render_template
from datetime import datetime
from os import listdir
from os.path import isfile, join, isdir
from flask_sqlalchemy import SQLAlchemy
import sys
import hashlib
import time
import csv

app = Flask(__name__)
app.config["DEBUG"] = True

separator="."
dateformat='ymd'
appending=bool(0)
updating=bool(0)

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

class LegionDB(db.Model):
    __tablename__ = "legion"
    id = db.Column(db.Integer, primary_key=True)
    series = db.Column(db.String(4096))
    URLpath = db.Column(db.String(4096))
    legions = db.relationship("LegionsDB",backref="legion")

class LegionsDB(db.Model):
    __tablename__ = "legions"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    value = db.Column(db.Integer)
    legion_id = db.Column(db.Integer, db.ForeignKey("legion.id"))
    def getdate(self):
        return self.date
    def print(self):
        return self.date.strftime("%Y.%m.%d")

class Legion:
	def __init__(self, date, number):
		global separator
	    #date_string = date
		g = date.strip()
		date_string = date
		print(g)
		x = g.split('.')
		assert(len(x)==3)
		global dateformat
		if(dateformat == 'dmy'):
			self.date=datetime.strptime(date_string, "%d"+separator+"%m"+separator+"%Y")
		elif(dateformat == 'ymd'):
			self.date=datetime.strptime(date_string, "%Y"+separator+"%m"+separator+"%d")
		elif(dateformat == 'mdy'):
			self.date=datetime.strptime(date_string, "%m"+separator+"%d"+separator+"%Y")

		self.number = number

def splitline(line):
        g = line.split(separator)
        if(len(g)==3):
                for i in range(3):
                    g[i] = g[i].strip()
                if len(g[0])*len(g[1])*len(g[2]) > 0: return g
        return list()

def readfromfolder(path):
	onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
	for i in onlyfiles:
		if i!="log.txt" and i[-4:]==".csv":
		    with open(join(path,i)) as csv_file:
		        csv_reader = csv.reader(csv_file, delimiter=',')
		        bdb = []
		        l = ''
		        for row in csv_reader:
		            l = row[0]
		            legion = Legion(row[1],row[2])
		            series = LegionsDB(date=legion.date,value=row[2])
		            bdb.append(series)
		        seria = LegionDB(series=l,URLpath=join(path,i))
		        seria.legions = bdb
		        db.session.add(seria)
		        db.session.commit()
	onlyfolders = [f for f in listdir(path) if isdir(join(path, f))]
	for j in onlyfolders:
		readfromfolder(join(path,j))

def datascrepancy(x, y):
	x=int(x)
	y=int(y)
	if(abs(x-y)/x < 0.2): return bool(0)
	else: return bool(1)

class Legions:
  def __init__(self, legions, path):
    self.legions = legions
    self.path = path
