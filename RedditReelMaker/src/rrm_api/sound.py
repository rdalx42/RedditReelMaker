import edge_tts
import asyncio

class sound:
    def __init__(self, content, voice="en-US-GuyNeural", output_file="output.mp3"):
        self.content = content
        self.voice = voice
        self.output_file = output_file

    def set_voice(self,name):
        if name == "male" :
            self.voice="en-US-GuyNeural"
        elif name == "female":
            self.voice = "en-US-AriaNeural"
        else:
            self.voice="en-US-GuyNeural" # default voice

    def do(self):    
        asyncio.run(self._speak())
        return self.output_file

    async def _speak(self):
        communicate = edge_tts.Communicate(self.content, self.voice)
        await communicate.save(self.output_file)
        print(f"Saved audio to {self.output_file}")
