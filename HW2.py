from flask import Flask, jsonify, request, abort
import random
import csv
import os

app = Flask(__name__)


data = []
dates = []

def refreshData():
    with open('daily.csv') as dataFile:
        fileReader = csv.DictReader(dataFile)
        for row in fileReader:
            data.append(dict({'DATE' : row['DATE'], 'TMAX' : row['TMAX'], 'TMIN': row['TMIN']}))
    dataFile.close()


    for entry in data:
        dates.append(dict({'DATE' : entry['DATE']}))

@app.route('/historical/')
def historical():
    dataa = []
    f = open('daily.csv', 'r')
    fileReader = csv.reader(f)
    for row in fileReader:
        tempDate = row[0]
        dataa.append({'DATE' : tempDate})
    f.close()
    return jsonify(dataa)

@app.route('/historical/<date_id>', methods=['GET'])
def get_date(date_id):
    dataa = []
    temp = {}
    found = False
    f =  open('daily.csv', 'r')
    fileReader = csv.reader(f)
    for row in fileReader:
        tempDate = row[0]
        tempTMAX = row[1]
        tempTMIN = row[2]
        if str(row[0]) == str(date_id):
            temp ={"DATE" : tempDate, "TMAX" : float(tempTMAX), "TMIN" : float(tempTMIN)}
            found = True

    if found != True:
        abort(404)

    return jsonify(temp), 200


@app.route('/historical/',methods=['POST'])
def post_date():
    refreshData()
    tempReq = request.get_json(force = True)
    data = []
    f =  open('daily.csv', 'r')
    fileReader = csv.reader(f)
    for row in fileReader:
        data.append(row)
    f.close()
    temp = [tempReq['DATE'],tempReq['TMAX'],tempReq['TMIN']]
    data.append(temp)

    f2 = open('daily.csv', 'w')
    writer = csv.writer(f2)
    writer.writerows(data)
    f2.close()

    tempDate=tempReq['DATE']
    tempTmax=tempReq['TMAX']
    tempTmin=tempReq['TMIN']
    return jsonify({'DATE' : str(tempDate)}), 201

@app.route('/historical/<date_id>',methods=['DELETE'])
def delete_date(date_id):
    refreshData()
    with open('_daily.csv', 'w') as newFile:
        newFile.write('DATE,TMAX,TMIN')
        fieldnames = ['DATE', 'TMAX', 'TMIN']
        writer = csv.DictWriter(newFile, fieldnames=fieldnames)
        newLineWriter = csv.writer(newFile)
        newLineWriter.writerow([])
        for entry in data:
            if entry['DATE'] == str(date_id):
                data.remove(entry)
            else:
                writer.writerow(entry)
    newFile.close()
    os.remove('daily.csv')
    os.rename('_daily.csv', 'daily.csv')
    return jsonify({'Deleted' : str(date_id)}), 204

@app.route('/forecast/<date_id>',methods=['GET'])
def forecast(date_id):
    try:
        prediction = []
        date_int = int(str(date_id))
        for date in range(date_int, (date_int + 7)):
            maxTemp = random.randrange(80, 100, 1);
            minTemp = random.randrange(20,75,1);
            prediction.append(dict({'DATE' : str(date), 'TMAX' : maxTemp, 'TMIN' : minTemp}))

        return jsonify(prediction)

    except Exception as e:
        return jsonify({'ERROR' : 'HTTP 400 Bad Request '+  str(e)})


@app.errorhandler(404)
def error404(e):
    return jsonify({'ERROR' : str(e)}),404

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8000, debug=False)
