# Juniper
POC of a real-time STS AI Assistant
Current latency is of around ~1-2s


# Requirements
(coded and tested only on windows)
<br>
MPV executable
<br>
whisper
<br>
openai
<br><br>
(not sure if any are missing)

# Usage
ALT + J to talk to it (streaming of STT not implemented yet)
<br>
ALT + N to reset context
<br><br>
Memories are stored in files/memory.json
<br><br>
Feel free to edit any prompt/system inside.
<br>
Add your Open AI and elevenlabs API keys in commons.py
<br>

# Notes
This was coded in a few hours, dont expect it to be very good, feel free to make any pull requests to improve the system with new features, better prompting or to reduce latency.

# Todo
- Add real time streaming of transcription with whisper, with a feature that waits for the user to stop talking without needing to press any keys.
- Real time streaming with the pressing keys feature, would allow a reduced latency.
- Improvment of latency, faster models or better pipeline
- Running local LLM and TTS models
- Adding audio processing, to remove silences from the TTS model or speed it up
- Improve the prompts, and the memory system
- Add other features, that the AI can use to help the user
<br>
- Add logging and error handling
