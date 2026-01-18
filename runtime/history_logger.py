from flask import Flask, request
import os

app = Flask(__name__)

print("Starting History Logger Service...")
print("Listening on http://localhost:5000/history")

@app.route("/history", methods=["POST"])
def history():
    data = request.json
    print(f"Received {len(data) if data else 0} history items.")
    
    list_of_titles = []
    if isinstance(data, list):
        for item in data:
            title = item.get("title", "No title found")
            list_of_titles.append(title+"\n")

    # Save to history file
    history_path = "./history.txt"
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(history_path), exist_ok=True)
        with open(history_path, "w", encoding="utf-8", errors="ignore") as f:
            f.writelines(list_of_titles)
        print("Updated history.txt")
    except Exception as e:
        print(f"Error writing file: {e}")
        
    return {"status": "received"}

if __name__ == "__main__":
    # Runs on port 5000 (default) as expected by the extension
    app.run(port=5000)
