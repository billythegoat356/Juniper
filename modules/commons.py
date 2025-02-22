from openai import AsyncOpenAI


class Voices:
    # Default
    jessica = "cgSgspJ2msm6clMCkdW9"
    sarah = "EXAVITQu4vr4xnSDxMaL"

    # Community
    anna = "QJZ3UdMVxxnwyFHF8mTp"
    natasha = "bVyC6AU0DeIMNdcIj0k1"
    scarlett = "aBT5tRan4lIdrm1G4dJU"

class VoiceSettings:
    model = "eleven_flash_v2_5"
    voice_id = Voices.anna

    stability = 0.5
    similarity_boost = 0.8
    style = 1
    use_speaker_boost = True

class LLMSettings:
    # model = "gpt-4-turbo"
    model = "gpt-4o-mini" # fastest i think
    # model = "gpt-4o-realtime-preview" # test
    temperature = 1

class MemorySettings:
    model = "gpt-4o"
    temperature = 1


class Settings:
    ELEVENLABS_API_KEY = ""
    OPENAI_API_KEY = ""


class AudioSettings:
    speed = 1
    min_silences_len = 100
    silence_thresh = -40

openai_aclient = AsyncOpenAI(api_key=Settings.OPENAI_API_KEY)

generation_uri = f"wss://api.elevenlabs.io/v1/text-to-speech/{VoiceSettings.voice_id}/stream-input?model_id={VoiceSettings.model}"
