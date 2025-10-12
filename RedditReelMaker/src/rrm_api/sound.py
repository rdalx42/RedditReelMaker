import edge_tts
import asyncio
from pydub import AudioSegment
from pydub.effects import speedup

class Sound:
    def __init__(self, content, output_file="output.mp3"):

        self.content = content
        self.output_file = output_file

    def do(self):
        asyncio.run(self._speak())
        return self.output_file

    async def _speak(self):
        # generate male TTS
        male_file = "male_part.mp3"
        male_tts = edge_tts.Communicate(self.content[0], voice="en-US-GuyNeural")
        await male_tts.save(male_file)

        # generate female TTS
        female_file = "female_part.mp3"
        female_tts = edge_tts.Communicate(self.content[1], voice="en-US-AriaNeural")
        await female_tts.save(female_file)

        male_audio = AudioSegment.from_file(male_file)
        female_audio = AudioSegment.from_file(female_file)

        male_audio = speedup(male_audio,1.1)
        female_audio = speedup(female_audio,1.1)

        # Concatenate without gaps
        combined = male_audio + female_audio

        combined.export(self.output_file, format="mp3")

        # Clean up
        import os
        os.remove(male_file)
        os.remove(female_file)

        print(f"Saved merged audio to {self.output_file}")
