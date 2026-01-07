import os
from flask import Flask, render_template

print("RUNNING APP FROM:", os.path.abspath(__file__))

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/check")
def check():
    return "check works"

if __name__ == "__main__":
    app.run(debug=True)