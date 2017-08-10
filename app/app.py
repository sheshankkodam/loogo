from flask import Flask, json, request

from pymongo import MongoClient

app = Flask(__name__)
client = MongoClient()


@app.route("/")
def hello():
    return "Loogo Started!"


@app.route("/status")
def status():
    data = {"app": "loogo", "version": "1.0.0", "status": "running"}
    response = app.response_class(response=json.dumps(data), status=200, mimetype="application/json")
    return response


@app.route('/washrooms/', methods=['GET'])
def washrooms():
    result = []
    db = client.loogo
    cursor = db.washrooms.find()

    for res in cursor:
        result.append({
            "name": res.get("name"),
            "status": res.get("status")
        })

    response = app.response_class(response=json.dumps(result), status=200, mimetype="application/json")
    return response


@app.route('/washrooms/<washroom_name>', methods=['PUT'])
def update_washroom_status(washroom_name):
    body = request.get_json()

    washroom_status = body.get('status')
    aws_sno = body.get('aws_sno')
    battery_voltage = body.get('battery_voltage')
    db = client.loogo
    db.washrooms.update(
        {"name": washroom_name},
        {
            "$set":
                {
                    "status": washroom_status,
                    "aws_sno": aws_sno,
                    "battery_voltage": battery_voltage
                }
        },
        True
    )
    response = app.response_class(response=json.dumps("successfully updated status for washroom:%s" % washroom_name),
                                  status=200, mimetype="application/json")
    return response


@app.route('/echopath/washrooms/', methods=['GET'])
def echopath_washrooms():
    result = []
    db = client.echopath
    cursor = db.locations.find({}, {"_id": 0})

    for res in cursor:
        result.append(res)

    response = app.response_class(response=json.dumps(result), status=200, mimetype="application/json")
    return response


@app.route('/echopath/washrooms/<washroom_name>', methods=['PUT'])
def update_washroom_status_echopath(washroom_name):
    body = request.get_json()
    washroom_status = True if "active" in body.get('status') else False
    db = client.echopath
    db.locations.update({"name": washroom_name}, {"$set": {"active": washroom_status}})
    response = app.response_class(response=json.dumps("successfully updated status for washroom:%s" % washroom_name),
                                  status=200, mimetype="application/json")
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
