

from flask import Flask, render_template, request, url_for, redirect

from rrm_api import Api, Sound, Video

# from rrm_api.rrm import Api
# from rrm_api.sound import Sound
# from rrm_api.video import  Video

import time

app = Flask(__name__)

@app.route("/")
def home():
    #placeholder
    return redirect(url_for("create"))

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
                post_data[key] = value

            post_data["flag_choice_nsfw"] = request.form.get("flag_choice_nsfw")
            post_data["flag_choice_subtitles"] = request.form.get("flag_choice_subtitles")

            if can_call_api:
                if post_data["flag_choice_nsfw"]!=None:
                    pass # change algo calling

                if post_data["flag_choice_subtitles"]!=None:
                    pass # change subtite algo calling
                return redirect(url_for("loading"))
            else:
                err_msg = "Expected all content to be filled!"

    return render_template("create.html", timestamp=int(time.time()), error_msg=err_msg)

@app.route("/loading")
def loading():
    return render_template("loading.html")

if __name__ == "__main__":
    app.run(debug=True)
