import edge_tts
import asyncio
import os

class Sound:
    def __init__(self, content, output_file="output.mp3"):

        self.content = content
        self.output_file = output_file

    def do(self):
        asyncio.run(self._speak())
        return self.output_file

    async def _speak(self):

        # save male part
        male_file = "male_part.mp3"
        male_tts = edge_tts.Communicate(self.content[0], voice="en-US-GuyNeural")
        await male_tts.save(male_file)

        # save female part
        female_file = "female_part.mp3"
        female_tts = edge_tts.Communicate(self.content[1], voice="en-US-AriaNeural")
        await female_tts.save(female_file)

        # merge safely
        for filename in [male_file, female_file]:
            if not os.path.exists(filename):
                raise FileNotFoundError(f"{filename} was not created!")

        with open(self.output_file, "wb") as out:
            # write male part
            with open(male_file, "rb") as m:
                out.write(m.read())
            # write female part
            with open(female_file, "rb") as f:
                out.write(f.read())

        # remove temporary files
        os.remove(male_file)
        os.remove(female_file)

        print(f"Saved merged audio to {self.output_file}")
