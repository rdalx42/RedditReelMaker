from moviepy.editor import AudioFileClip, VideoFileClip, CompositeVideoClip, ImageClip
from PIL import Image, ImageDraw, ImageFont
import random
import whisper
import numpy as np
from math import sin, pi

class Video:
    def __init__(self, mp3, video_path="res/parkour.mp4",cool_subtitles=False,export_name="output",background_video_change_frame_rate = 8):
        self.mp3 = mp3
        self.background_video_frame_change_rate = background_video_change_frame_rate
        self.export_name = export_name
        self.video_path = video_path
        self.model = whisper.load_model("small")  
        if cool_subtitles==True:
            self.fontcolors = ["white","blue","yellow","red","green","purple","orange"]
        else:
            self.fontcolors=["white"]
    def generate_subtitles(self):
        result = self.model.transcribe(self.mp3, word_timestamps=True)
        subtitles = []

        delay_map = {
            ".": 0.0,
            "?": 0.0,
            "!": 0.0,
            ",": 0.0,
            ";": 0.0,
            ":": 0.0,
            "...": 0.0
        }

        for seg in result.get("segments", []):
            if "words" in seg:
                for w in seg["words"]:
                    word = w["word"].strip()
                    start = w["start"]
                    end = w["end"]

                    extra_delay = 0.0
                    for mark, delay in delay_map.items():
                        if word.endswith(mark):
                            extra_delay = delay
                            break

                    
                    subtitles.append({
                        "start": start,
                        "end": end + extra_delay,
                        "text": word
                    })
            else:
                text = seg["text"].strip()
                start = seg["start"]
                end = seg["end"]

                extra_delay = 0.0
                for mark, delay in delay_map.items():
                    if text.endswith(mark):
                        extra_delay = delay
                        break

                subtitles.append({
                    "start": start,
                    "end": end + extra_delay,
                    "text": text
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
        amplitude = 20  # max pixels to move
        frequency = 2   # number of bounces per second
        clip = clip.set_position(lambda t: ("center", 900 - amplitude * abs(sin(pi * frequency * t))))

        return clip

    def do(self, output_file=None):
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
        num_switches = int(np.ceil(audio_duration / self.background_video_frame_change_rate))
        subclips = []

        for i in range(num_switches):
            start_time = random.uniform(0, video_duration - self.background_video_frame_change_rate)
            end_time = start_time + self.background_video_frame_change_rate
            subclip = video_full.subclip(start_time, end_time).crop(
                width=video_full.h * 9 / 16,
                height=video_full.h,
                x_center=video_full.w / 2,
                y_center=video_full.h / 2
            ).resize((1080, 1920))
            subclip = subclip.set_start(i * self.background_video_frame_change_rate)
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
            output_file = f"{self.export_name}.mp4"
        
        final_clip.write_videofile(output_file, codec="libx264", audio_codec="aac", fps=24)
        
        final_clip.close()
        clip.close()
        video_full.close()
        audio.close()
        print(f"Saved video to {output_file}")
        return output_file
