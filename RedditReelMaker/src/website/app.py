from flask import Flask, render_template, request, redirect, url_for, send_file
import threading
import traceback
import time
import re
import uuid
import random
import os
from rrm_api import Api, Sound, Video

app = Flask(__name__)

tasks = {}

def call_api_worker(task_id, params):
    try:
        tasks[task_id]["status"] = "processing"
        tasks[task_id]["message"] = "Initializing API..."

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

        tasks[task_id]["message"] = "Fetching Reddit post..."
        api = Api(l1, l2, "AskReddit", ans_path="C:/Users/raduh/OneDrive/Documents/RedditReelMaker/src/ans.json")
        selected = api.get_post(l1, l2, nsfw=nsfw)
        tasks[task_id]["message"] = "Generating voiceover..."
        api.sanitize_comment(selected)
        audio_path = Sound(selected).do()

        rand_str = f'{random.getrandbits(128):032x}'
        export_filename += rand_str

        tasks[task_id]["message"] = "Initializing video..."
        video = Video(
            audio_path,
            cool_subtitles=coolsubs,
            video_path=gameplay_path,
            export_name=export_filename,
            background_video_change_frame_rate=change
        )
        tasks[task_id]["message"] = "Downloading will begin shortly (1-3 minutes)"
        output_file = video.do()
        tasks[task_id]["status"] = "done"
        tasks[task_id]["file"] = output_file
        tasks[task_id]["message"] = "Video generated successfully ✅"
    except Exception as e:
        traceback.print_exc()
        tasks[task_id]["status"] = "error"
        tasks[task_id]["file"] = None
        tasks[task_id]["message"] = f"Error: {e}"

@app.route("/")
def home():
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
                    task_id = str(uuid.uuid4())
                    tasks[task_id] = {"status": "processing", "file": None, "message": "Queued for generation..."}
                    threading.Thread(target=call_api_worker, args=(task_id, post_data), daemon=True).start()
                    return redirect(url_for("loading", task_id=task_id))
                except Exception as e:
                    err_msg = f"Error: {e}"
                    traceback.print_exc()
            else:
                if not err_msg:
                    err_msg = "Expected all content to be filled!"
    return render_template("create.html", timestamp=int(time.time()), error_msg=err_msg)

@app.route("/loading")
def loading():
    task_id = request.args.get("task_id")
    if not task_id or task_id not in tasks:
        return redirect(url_for("create"))

    task = tasks[task_id]

    if task["status"] == "done":
        return redirect(url_for("download_video", filename=os.path.basename(task["file"])))
    elif task["status"] == "error":
        return f"<h2>Error occurred: {task['message']}</h2>"

    return render_template(
        "loading.html",
        timestamp=int(time.time()),
        status=task["status"],
        message=task["message"],
        task_id=task_id
    )

@app.route("/download/<filename>")
def download_video(filename):
    file_path = os.path.join(os.getcwd(), filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "File not found", 404

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, threaded=True)
