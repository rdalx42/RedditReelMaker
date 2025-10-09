from moviepy.editor import AudioFileClip, VideoFileClip, CompositeVideoClip, ImageClip
from PIL import Image, ImageDraw, ImageFont
import random
import whisper
import numpy as np
from math import sin, pi

class Video:
    def __init__(self, mp3, video_path="res/parkour.mp4"):
        self.mp3 = mp3
        self.video_path = video_path
        self.model = whisper.load_model("small")  # Load Whisper once
        self.fontcolors = ["white","blue","yellow","red","green","purple","orange"]
    def generate_subtitles(self):
        
        result = self.model.transcribe(self.mp3, word_timestamps=True)
        subtitles = []
        
        for seg in result.get("segments", []):
            if "words" in seg:
                for w in seg["words"]:
                    subtitles.append({
                        "start":w["start"],
                        "end":w["end"],
                        "text":w["word"].strip()
                    })

            else:
                subtitles.append({
                    "start":seg["start"],
                    "end":seg["end"],
                    "text":seg["text"]
                })

        return subtitles

    def create_subtitle_clip(self, text, start, end, video_width, font_path=None):
        if not font_path:
            font_path = "res/Roboto.ttf"
        font_size = 80
        font = ImageFont.truetype(font_path, font_size)
        padding = 20
        img_width = video_width
        img_height = font_size + 2 * padding
        img = Image.new("RGBA", (img_width, img_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        w, h = draw.textsize(text, font=font)
        x = (img_width - w) / 2
        y = padding
        stroke_width = 3
        stroke_fill = "black"
        for dx in [-stroke_width, 0, stroke_width]:
            for dy in [-stroke_width, 0, stroke_width]:
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), text, font=font, fill=stroke_fill)
        draw.text((x, y), text, font=font, fill=random.choice(self.fontcolors)) 
        img_array = np.array(img) 

        clip = ImageClip(img_array, transparent=True).set_start(start).set_end(end)

        # Bounce effect
        amplitude = 50  # max pixels to move
        frequency = 2   # number of bounces per second
        clip = clip.set_position(lambda t: ("center", 900 - amplitude * abs(sin(pi * frequency * t))))

        return clip

    def do(self, output_file=None, switch_interval=8):
        """
        Creates a video with subtitles and switches video frames every few seconds.
        
        switch_interval: seconds per random video frame
        """
        print("Making video...")
        audio = AudioFileClip(self.mp3)
        video_full = VideoFileClip(self.video_path, target_resolution=(1080, 1920))
        video_duration = video_full.duration
        audio_duration = audio.duration
        
        if audio_duration > video_duration:
            print("Audio is longer than video. Exiting.")
            audio.close()
            video_full.close()
            return None

        # Calculate how many switches we need
        num_switches = int(np.ceil(audio_duration / switch_interval))
        subclips = []

        for i in range(num_switches):
            start_time = random.uniform(0, video_duration - switch_interval)
            end_time = start_time + switch_interval
            subclip = video_full.subclip(start_time, end_time).crop(
                width=video_full.h * 9 / 16,
                height=video_full.h,
                x_center=video_full.w / 2,
                y_center=video_full.h / 2
            ).resize((1080, 1920))
            subclip = subclip.set_start(i * switch_interval)
            subclips.append(subclip)

        # Combine the random subclips into one video
        clip = CompositeVideoClip(subclips).set_duration(audio_duration)
        clip = clip.set_audio(audio)

        # Add subtitles
        subtitles = self.generate_subtitles()
        subtitle_clips = []
        for sub in subtitles:
            subtitle_clips.append(
                self.create_subtitle_clip(
                    text=sub["text"],
                    start=sub["start"],
                    end=sub["end"],
                    video_width=clip.w
                )
            )

        final_clip = CompositeVideoClip([clip, *subtitle_clips])
        
        if not output_file:
            output_file = f"RedditReelMaker_output_{random.randint(1000, 9999)}.mp4"
        
        final_clip.write_videofile(output_file, codec="libx264", audio_codec="aac", fps=24)
        
        final_clip.close()
        clip.close()
        video_full.close()
        audio.close()
        print(f"Saved video to {output_file}")
        return output_file
