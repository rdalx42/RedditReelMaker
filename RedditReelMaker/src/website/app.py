

from flask import Flask, render_template, request, url_for, redirect
from rrm_api import Api, Sound, Video

import re 
import time

app = Flask(__name__)

@app.route("/")
def home():
    #placeholder
    return redirect(url_for("create"))

def call_api(params):
    
    nsfw = False
    coolsubs=False
    export_filename="ONLINE_REEL_MAKER_OUTPUT"
    gameplay_path = {}

    for key, value in params.items():
        
        # i had no other choice

        if key == "flag_choice_nsfw" and value!=None :
            nsfw=True
        if key == "flag_choice_subtitles" and value!=None: 
            coolsubs=True 

        if key == "vid_name":
            export_filename = value

        if key == "gameplay_choice":
            if value == "option8":
                gameplay_path = "ADD ASMR COOKING PATH"
        
        print(f"{key} = {value}")

@app.route("/create", methods=["GET", "POST"])
def create():
    err_msg = None

    if request.method == "POST":
        if "generate" in request.form:
            can_call_api = True
            post_data = {}

            for key, value in request.form.items():
                if key != "generate" and (value is None or value.strip() == ""):
                    can_call_api = False
                    break

                if key == "vid_name":
                    if not re.match("^[a-zA-Z0-9]+$", value):
                        print("INVALID CHARACTERS")
                        can_call_api=False
                        err_msg = "Only numbers and letters are allowed in the video name"
                        break
                post_data[key] = value

            post_data["flag_choice_nsfw"] = request.form.get("flag_choice_nsfw")
            post_data["flag_choice_subtitles"] = request.form.get("flag_choice_subtitles")

            for key, value in post_data.items():
                print(f"{key} = {value}")


            if can_call_api:
                if post_data["flag_choice_nsfw"]!=None:
                    pass # change algo calling

                if post_data["flag_choice_subtitles"]!=None:
                    pass # change subtite algo calling
                return redirect(url_for("loading"))
            else:
                if err_msg==None: 
                    err_msg = "Expected all content to be filled!"

    return render_template("create.html", timestamp=int(time.time()), error_msg=err_msg)

@app.route("/loading")
def loading():
    return render_template("loading.html")

if __name__ == "__main__":
    app.run(debug=True)
