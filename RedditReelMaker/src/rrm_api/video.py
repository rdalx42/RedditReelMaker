from moviepy.editor import AudioFileClip, VideoFileClip

import random

class Video:

    def __init__(self, mp3, video_path="res/parkour_minecraft.mp4"):

        self.mp3 = mp3
        self.video_path = video_path

    def do(self, output_file=None):
        # load audio and vid

        print("Making video...")

        audio = AudioFileClip(self.mp3)
        video_full = VideoFileClip(self.video_path,target_resolution=(1080,1920))

        video_duration = video_full.duration
        audio_duration = audio.duration

        if audio_duration > video_duration:
            print("Video duration is shorter than audio duration. Cannot create clip.")
            audio.close()
            video_full.close()
            return None

        print("Getting intervals...")

        interval1 = random.uniform(0, video_duration - audio_duration)
        interval2 = interval1 + audio_duration

        print("Clipping...")

        # subclip 9:16 (reel aspect ratio)
        print("Setting Intervals to [",interval1,",",interval2,"]")
        clip_from_video = video_full.subclip(interval1, interval2)
        print("Setting Ratio")
        clip_from_video = clip_from_video.crop(
            width=video_full.h * 9/16,  # center crop width
            height=video_full.h,
            x_center=video_full.w / 2,
            y_center=video_full.h / 2
        )
        clip_from_video = clip_from_video.resize((1080, 1920))

        print("Setting Audio")
        clip_from_video = clip_from_video.set_audio(audio)

        print("Setting output...")

        # set output file
        if not output_file:
            output_file = f"RedditReelMaker_output_{random.randint(1000, 9999)}.mp4"

        # write output

        print("Saving video...")

        clip_from_video.write_videofile(
            output_file,
            codec="libx264",
            audio_codec="aac",
            fps=24
        )

        # Clean
        clip_from_video.close()
        video_full.close()
        audio.close()

        print(f"Saved video to {output_file}")
        return output_file
