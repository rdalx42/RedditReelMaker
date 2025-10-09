
from flask import Flask, render_template, request, url_for, redirect
import time

app = Flask(__name__)

@app.route("/")

def home():
    # temporary.
    return redirect(url_for("create"))

@app.route("/create",methods=["GET","POST"])

def create():
    return render_template("create.html",timestamp=int(time.time()))

if __name__ == "__main__":
    app.run(debug=True)
