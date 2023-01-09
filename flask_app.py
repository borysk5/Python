from flask import request, render_template
from datetime import datetime
from os.path import join
from logic import csv, pd, DataseriesDB, DataentryDB, readfromfolderpandas, savetofilespandas, savetofiles, Dataentry, Dataseries, app, db, datascrepancy, readfromfolder, DateTime, readfromfolderog, serieslist
import time


@app.route("/log")
def log():
    f = open("mysite/dataseries/log.txt", "r")
    page= ""
    myline = f.readline()
    while(myline):
        page +=myline+"\n<br>"
        myline = f.readline()
    return page


@app.route("/initialize")
def initialize():
    db.create_all()
    DataentryDB.query.delete()
    DataseriesDB.query.delete()
    db.session.commit()
    page="DONE"
    mypath = "mysite/dataseries"
    readfromfolder(mypath)
    return page

@app.route("/data/<id>")
def data(id):
    global h
    page= ""
    zh = DataseriesDB.query.filter_by(series=id).first()
    if zh is not None:
        for i in zh.legions:
            page+=id+' '+i.print()+' '+str(i.value)+"<br>\n"
    else: page += "No such series"
    return page

@app.route("/serwer", methods=['GET','POST'])
def main():
    args = request.form
    global separator
    if (not args.get("automat")) and args.get("type"):
        separator = args.get("type")
    appending = bool(0)
    updating = bool(0)
    dateformat = "dmy"
    if "dateformat" in args:
        dateformat = args.get("dateformat")
    if args.get("appending"):
        appending = bool(1)
    if args.get("updating"):
        updating = bool(1)
    mypath = "mysite/dataseries"
    checked = ['','','','']
    if(dateformat=="dmy"):checked[0]='checked'
    elif(dateformat=="ymd"):checked[1]='checked'
    elif(dateformat=="mdy"):checked[2]='checked'
    checked1 = ['','']
    if appending: checked1[0]='checked'
    if updating: checked1[1]='checked'
    checktypes=""
    if "types" in args:
        checktypes = args.get("types")
        assert checktypes=='sql' or checktypes=='man' or checktypes=='pan'
    checkedtypes = ['','','']
    if(checktypes=="sql"): checkedtypes[0]='checked'
    elif(checktypes=="man"): checkedtypes[1]='checked'
    elif(checktypes=="pan"): checkedtypes[2]='checked'
    global pandaseries
    global pandaentries
    if(checktypes=='man'):
        readfromfolderog(mypath)
    elif(checktypes=='pan'):
        xj = readfromfolderpandas(mypath)
        pandaseries = xj[0]
        pandaentries = xj[1]

    files = []
    if(args.get("default")):
        files.append(open("mysite/insert.csv"))
    elif(len(request.files)>0):
        files = request.files.getlist('myfile')

    g = open("mysite/dataseries/log.txt", "a")
    g.write('\n'+str(datetime.now()))
    start = time.time()
    print(start)
    for f in files:
        print("tresc")
        print(f.name)
        if f.name.endswith(".csv"):
            csv_reader = csv.reader(f, delimiter=',')
            for x in csv_reader:
                if(len(x)!=3):
                    g.write('\n'+'Data mismatch. Wrong format of data series in line: "'+x+'"');
                else:
                    x[1] = x[1].strip()
                    x[0] = x[0].strip()
                    x[2] = x[2].strip()
                    if(appending and checktypes=='sql'):
                        new_vc = DataentryDB(date=DateTime(x[1]),value=x[2])
                        hg = DataseriesDB.query.filter_by(series=x[0]).first()
                        if hg is not None:
                            DataseriesDB.query.filter_by(series=x[0]).first().legions.append(new_vc)
                            g.write('\n'+'Added new line: '+x[0]+', '+x[1]+', '+x[2])
                        else:
                            new_h = DataseriesDB(series=x[0],URLpath=join(mypath,x[0]+'.csv'))
                            new_h.legions.append(new_vc)
                            db.session.add(new_h)
                            g.write('\n'+'Added new line: '+x[0]+', '+x[1]+', '+x[2])
                    elif(appending and checktypes=='man'):
                        new_vc = Dataentry(date=DateTime(x[1]),value=x[2])
                        if x[0] in serieslist.keys():
                            serieslist[x[0]].legions.append(new_vc)
                            g.write('\n'+'Added new line: '+x[0]+', '+x[1]+', '+x[2])
                        else:
                            new_h = Dataseries(id=x[0],legions=[],URLpath=join(mypath,x[0]+'.csv'))
                            new_h.legions.append(new_vc)
                            serieslist[x[0]]=new_h
                            g.write('\n'+'Added new line: '+x[0]+', '+x[1]+', '+x[2])
                    elif(appending and checktypes=='pan'):
                        if x[0] in pandaseries['Series'].values:
                            df = pd.DataFrame(data=[x])
                            df.columns = ['Series', 'Date', 'Value']
                            pandaentries = pd.concat([pandaentries,df])
                            g.write('\n'+'Added new line: '+x[0]+', '+x[1]+', '+x[2])
                        else:
                            df = pd.DataFrame(data=[x])
                            df.columns = ['Series', 'Date', 'Value']
                            pandaentries = pd.concat([pandaentries,df])
                            ch = pd.DataFrame(data=[[x[0], join(mypath,x[0]+'.csv')]])
                            ch.columns=['Series','URL']
                            pandaseries = pd.concat([pandaseries,ch])
                            g.write('\n'+'Added new line: '+x[0]+', '+x[1]+', '+x[2])
                    if(updating and checktypes!='pan'):
                        global new_jj
                        global entries
                        if(checktypes=='sql'):
                            new_jj = DataentryDB(date=DateTime(x[1]),value=x[2])
                            entries = DataseriesDB.query.filter_by(series=x[0]).first().legions
                        elif(checktypes=='man'):
                            new_jj = Dataentry(date=DateTime(x[1]),value=x[2])
                            entries = serieslist[x[0]].legions
                        for xx in entries:
                            if(xx.print() == new_jj.print()):
                                if(datascrepancy(xx.value,new_jj.value)):
                                    g.write('\n'+'Data mismatch in: '+x[0]+' '+xx.print()+'. New value ('+str(new_jj.value)+') too different from '+str(xx.value));
                                else:
                                    v = xx.value
                                    xx.value = new_jj.value
                                    g.write('\n'+'In '+x[0]+' '+xx.print()+' replaced '+str(v)+' with new value: '+ str(new_jj.value));
                                break
                    elif(updating and checktypes=='pan'):
                        if x[0] in pandaseries['Series'].values:
                            if x[1] in pandaentries['Date'].values:
                                old_value = str(pandaentries.loc[(pandaentries['Date']==x[1]) & (pandaentries['Series']==x[0]),'Value'].iloc[0])
                                if(datascrepancy(old_value,x[2])):
                                    g.write('\n'+'Data mismatch in: '+x[0]+' '+xx.print()+'. New value ('+str(new_jj.value)+') too different from '+str(xx.value));
                                else:
                                    pandaentries.loc[(pandaentries['Date']==x[1]) & (pandaentries['Series']==x[0]),'Value'] = x[2]
                                    g.write('\n'+'In '+x[0]+' '+x[1]+' replaced '+old_value+' with new value: '+ x[2]);
    if(checktypes=='sql'):
        db.session.commit()
        savetofiles(DataseriesDB.query.all())
    elif(checktypes=='man'):
        savetofiles(serieslist.values())
    elif(checktypes=='pan'):
        savetofilespandas(pandaseries,pandaentries)
    passed = 0
    if(len(checktypes)>0):
        g.close()
        end = time.time()
        passed = float(int(100*(end - start))/100)

    return render_template("index.html", checked=checked, checkedtypes=checkedtypes,passed = passed,  checked1=checked1)
	#return page;