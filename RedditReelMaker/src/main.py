
from rrm_api.rrm import rrm_api
from rrm_api.sound import sound

api = rrm_api(100,200,"AskReddit")

selected = api.get_post(20,40)