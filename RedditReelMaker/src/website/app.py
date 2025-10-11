from flask import Flask, render_template, request, url_for, redirect
from rrm_api import Api, Sound, Video
import re
import time
import threading
import traceback

app = Flask(__name__)

@app.route("/")
def home():
    return redirect(url_for("create"))

def call_api(params):

    try:
        nsfw = False
        coolsubs = False
        export_filename = "ONLINE_REEL_MAKER_OUTPUT"
        gameplay_path = ""
        change = 0
        l1 = 0
        l2 = 0

        for key, value in params.items():
            if key == "flag_choice_nsfw" and value:
                nsfw = True
            if key == "flag_choice_subtitles" and value:
                coolsubs = True
            if key == "vid_name":
                export_filename = value
            if key == "gameplay_choice":
                if value == "Option 8":
                    gameplay_path = "res/asmr_cooking.mp4"
                elif value == "Option 6":
                    gameplay_path = "res/parkour.mp4"
                else:
                    gameplay_path = "res/subwaysurfers.mp4"
            if key == "clip_choice":
                if value == "Option 9":
                    change = 3
                if value == "Option 10":
                    change = 5
                if value == "Option 11":
                    change = 8
            if key == "len_choice":
                if value == "Option 2":
                    l1, l2 = 70, 100
                elif value == "Option 1":
                    l1, l2 = 50, 70
                elif value == "Option 3":
                    l1, l2 = 140, 210
            print(f"{key} = {value}")

        print("initializing")
        api = Api(l1, l2, "AskReddit",ans_path="C:/Users/raduh/OneDrive/Documents/RedditReelMaker/src/ans.json") # !!! TEMPORARY !!!
        print(l1,l2)
        print("initizalized")
        selected = api.get_post(l1, l2, nsfw=nsfw)
        
        print(selected)
        print("Got post")
        api.sanitize_comment(selected)
        audio_path = Sound(selected).do()
        print("Made sound")
        video = Video(
            audio_path,
            cool_subtitles=coolsubs,
            video_path=gameplay_path,
            export_name=export_filename,
            background_video_change_frame_rate=change
        )
        print("Made video")
        output_file = video.do()
        print("Saved video at:", output_file)
        return output_file

    except Exception as e:
        print("Error in call_api:", e)
        traceback.print_exc()

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
                    if not re.match(r"^[a-zA-Z0-9]+$", value):
                        err_msg = "Only numbers and letters are allowed in the video name"
                        can_call_api = False
                        break
                post_data[key] = value
            post_data["flag_choice_nsfw"] = request.form.get("flag_choice_nsfw")
            post_data["flag_choice_subtitles"] = request.form.get("flag_choice_subtitles")
            if can_call_api:
                try:
                    threading.Thread(target=call_api, args=(post_data,)).start()
                    return redirect(url_for("loading"))
                except Exception as e:
                    err_msg = f"Error: {e}"
                    traceback.print_exc()
            else:
                if err_msg is None:
                    err_msg = "Expected all content to be filled!"
    return render_template("create.html", timestamp=int(time.time()), error_msg=err_msg)

@app.route("/loading")
def loading():
    return render_template("loading.html")

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
