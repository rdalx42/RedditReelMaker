
from rrm_api.rrm import Api
from rrm_api.sound import Sound
from rrm_api.video import  Video

api = Api(100,200,"AskReddit")
selected = api.get_post(20,40)
api.sanitize_comment(selected)

audio_path = Sound(selected).do()

video = Video(audio_path)
output_file = video.do()

print("Saved video at:", output_file)
