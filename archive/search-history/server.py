from flask import Flask, request, jsonify
import json

app = Flask(__name__)
trigger = False

@app.route("/trigger")  
def get_trigger():
    return jsonify({"run": trigger})

@app.route("/fire", methods=["POST"])
def fire():
    global trigger
    trigger = True
    return {"status": "fired"}

@app.route("/reset", methods=["POST"])
def reset():
    global trigger
    trigger = False
    return {"status": "reset"}

@app.route("/history", methods=["POST"])
def history():
    data = request.json
    list_of_titles = []

    for item in data:
        title = item.get("title", "No title found")
        list_of_titles.append(title+"\n")

    with open("history.txt", "w", encoding="utf-8", errors="ignore") as f:
        f.writelines(list_of_titles)
    return {"status": "received"}

app.run(port=5000)