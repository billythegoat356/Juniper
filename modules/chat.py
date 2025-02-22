import asyncio

from modules.stream import StreamPipe, DelayCalc
from modules.rec import AudioRecorder
from modules.transcribe import transcribe
from modules.keys_listener import kwait, KEvents

from modules.ai import get_system_prompt

import time


class ChatPipe:

    messages: dict = []
    stream: StreamPipe = None

    @classmethod
    async def stop_stream(cls):
        if cls.stream is not None:
            await cls.stream.kill()
            cls.messages.append({"role": "assistant", "content": cls.stream.streamed_text})

    @classmethod
    async def new(cls):
        print("NEW CONTEXT")

        await cls.stop_stream()

        cls.messages = [{"role": "system", "content": get_system_prompt()}]
        cls.stream = None

    @classmethod
    async def open(cls):
        print("OPENED")
        
        AudioRecorder.start_recording()
        await cls.stop_stream()
    
    @classmethod
    async def close(cls):
        print("CLOSED")
        AudioRecorder.stop_recording()

        DelayCalc.start()

        t2 = time.time()
        text = transcribe()
        print(f"Time taken: to transcribe {time.time() - t2}")
        print(text)

        cls.messages.append({"role": "user", "content": text})

        cls.stream = StreamPipe()
        await cls.stream.init()
        await cls.stream.generate_response(cls.messages)



KEvents.new = ChatPipe.new
KEvents.open = ChatPipe.open
KEvents.close = ChatPipe.close

async def run():
    print("Talking with Juniper")

    await ChatPipe.new()
    await kwait()

asyncio.run(run())


