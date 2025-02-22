import websockets
import json
import asyncio
import base64
import subprocess
import time

from typing import AsyncGenerator
from concurrent.futures import ThreadPoolExecutor

from .ai import Memory, add_memories
from .commons import generation_uri, VoiceSettings, Settings, LLMSettings, openai_aclient
from .misc import text_chunker


class DelayCalc:
    checkpoint_ts = 0

    @classmethod
    def start(cls):
        cls.checkpoint_ts = time.time()

    @classmethod
    def stop(cls):
        stop_ts = time.time() - cls.checkpoint_ts
        print(f"Total time to get first response: {round(stop_ts, 2)}")


class StreamPipe:

    def __init__(self):

        self.conn_initialized = False
        
        self.mpv_process = None
        self.stream_task = None
        self.generate_response_task = None

        self.aborted = False

        self.user_message = ""

        # The following is 'assistant response' but its being streamed
        self.streamed_text = "" # Keeps track of the streamed text. Not very accurate unless we keep track of the duration of the chars that have been said.

    

    async def init(self):

        self.executor = ThreadPoolExecutor(max_workers=1)

        
        self.stream_task = asyncio.create_task(self.stream(self.listen()))

        asyncio.create_task(self.init_conn())



    async def generate_response(self, messages):

        self.user_message = messages[-1]["content"]

        response = await openai_aclient.chat.completions.create(model=LLMSettings.model, messages=messages, temperature=LLMSettings.temperature, stream=True)

        async def text_iterator():
            async for chunk in response:
                delta = chunk.choices[0].delta
                yield delta.content
        
        chunks = text_chunker(text_iterator())

        self.generate_response_task = asyncio.create_task(self._stream_response(chunks))


    async def wait(self):
        while self.mpv_process is not None:
            "This is the only one we check because its waiting on the audio to be fully received, which waits for the audio to be fully sent."
            await asyncio.sleep(0.1)

    async def kill(self):
        self.aborted = True
        try:
            if self.mpv_process is not None:
                self.mpv_process.terminate()
            
            if self.stream_task is not None:
                self.stream_task.cancel()
                try:
                    await self.stream_task
                except asyncio.CancelledError:
                    pass

            if self.generate_response_task is not None:
                self.generate_response_task.cancel()
                try:
                    await self.generate_response_task
                except asyncio.CancelledError:
                    pass
        except Exception as e:
            print(f"Error during kill: {e}")


    async def init_conn(self):
        "This is ran in a thread, to let chatgpt start generating"

        self.conn = await websockets.connect(generation_uri)

        init_message = {
            "text": " ",
            "voice_settings": {
                "stability": VoiceSettings.stability,
                "similarity_boost": VoiceSettings.similarity_boost,
                "style": VoiceSettings.style,
                "use_speaker_boost": VoiceSettings.use_speaker_boost
            },
            "xi_api_key": Settings.ELEVENLABS_API_KEY
        }
        await self.conn.send(json.dumps(init_message))

        self.conn_initialized = True


    async def send(self, text: str):
        while not self.conn_initialized:
            await asyncio.sleep(0.05)

        input_message = {
            "text": text
        }
        await self.conn.send(json.dumps(input_message))
    
    async def send_final(self):
        await self.send(text="")

    
    async def listen(self):

        while not self.conn_initialized:
            await asyncio.sleep(0.05)

        t = time.time()
        first_chunk = True

        while True:
            if self.aborted:
                break

            try:
                response = await self.conn.recv()
                data = json.loads(response)

                if data.get("audio") is not None:
                    if data.get("alignment") is not None:
                        chars = ''.join(data["alignment"]["chars"])
                        self.streamed_text += chars + " "
                    if first_chunk:
                        first_chunk = False
                        print(f"Time to get first response from elabs: {time.time() - t}")

                        DelayCalc.stop()

                    chunk = base64.b64decode(data["audio"])
                    yield chunk
                elif data.get("isFinal"):
                    break
            except websockets.exceptions.ConnectionClosed:
                print("Connection closed")
                break


    async def stream(self, audio_stream):
        """Stream audio data using mpv player."""
        loop = asyncio.get_running_loop()
        
        self.mpv_process = subprocess.Popen(
            ["mpv", "--no-cache", "--no-terminal", "--", "fd://0"],
            stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        print("Started streaming audio")

        async def write_chunk(chunk):
            await loop.run_in_executor(self.executor, 
                                     lambda: (self.mpv_process.stdin.write(chunk),
                                            self.mpv_process.stdin.flush()))

        try:
            async for chunk in audio_stream:
                if self.mpv_process is None:  # Check if process was killed
                    break
                await write_chunk(chunk)
                await asyncio.sleep(0)  # Let other tasks run
        except Exception as e:
            print(f"Error in streaming: {e}")
        finally:
            if self.mpv_process and self.mpv_process.stdin:
                await loop.run_in_executor(self.executor, 
                                         self.mpv_process.stdin.close)

            while self.mpv_process and self.mpv_process.poll() is None:
                await asyncio.sleep(0.1)

            self.mpv_process = None
            self.stream_task = None

    async def _stream_response(self, response_generator: AsyncGenerator[str, None]):
        async for text in response_generator:
            if self.aborted:
                break
            await self.send(text)

        await self.send_final()

        print(self.streamed_text)

        user_message = self.user_message
        assistant_response = self.streamed_text
        asyncio.create_task(add_memories(user_message, assistant_response))

        self.generate_response_task = None
