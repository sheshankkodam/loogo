from flask import Flask, json, request

from pymongo import MongoClient

app = Flask(__name__)
client = MongoClient()
db = client.loogo


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

    db.washrooms.update(
        {"name": washroom_name},
        {"$set": {"status": washroom_status}},
        True
    )
    response = app.response_class(response=json.dumps("successfully updated status for washroom:%s" % washroom_name),
                                  status=200, mimetype="application/json")
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
