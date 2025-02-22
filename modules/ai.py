"""
The idea is to have a thread started that will process additional information about the message. Keep in mind that it has to be linked to the actual response.
"""

import json
from pydantic import BaseModel

from .commons import openai_aclient, MemorySettings


class Memory:
    file_path = "files/memory.json"

    # Maybe implement update/remove feature but then the AI would need to always get everything
    # This would be nice to not get duplicates though

    def get():
        with open(Memory.file_path, "r") as f:
            return json.load(f)
    
    def add(text):
        memory = Memory.get()
        memory.append(text)
        with open(Memory.file_path, "w") as f:
            json.dump(memory, f, indent=4)


class MemoriesModel(BaseModel):
    memories: list[str]



async def add_memories(user_message, assistant_response):
    
    system_prompt = """
Based on the user message and assistant response, write down one or more memories (if applicable) that the AI should remember for future conversations.
Memories should only be said user side.
Memories should be relevant, provide information that the AI should remember, and dont always have to be explicitely said by the user.
You are allowed to not remember any memories, if none are relevant.
Memories should not be local data that is only relevant for one chat. Memories should be relevant across future chats and should have relevant general information about the user.
Memories can also be about what the user wants the AI to be.
    """.strip()
    user_prompt = f"""
User Message:
{user_message}

Assistant Response:
{assistant_response}
""".strip()
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    chat_completion = await openai_aclient.beta.chat.completions.parse(messages=messages, model=MemorySettings.model, temperature=MemorySettings.temperature, response_format=MemoriesModel)
    memories_event = chat_completion.choices[0].message.parsed

    new_memories = memories_event.memories

    print("Memories: ", str(new_memories))

    if len(new_memories) > 0:
        for memory in new_memories:
            Memory.add(memory)



def get_system_prompt():
    memory = '\n'.join(Memory.get())
    system_prompt = f"""
Your name is Juniper. You are an AI assistant. Keep responses brief. Your responses are made to be spoken. Be nice and warm.

Consider memories about the user during the chat.
--- MEMORY ---
{memory}
""".strip()
    return system_prompt

