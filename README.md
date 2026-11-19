# Memory Companion
A real-time voice companion that chats with elderly family members every day about their younger years, to support cognitive health and preserve their life stories as diaries, old-photo-style images and short videos.

## Architecture (planned)
LiveKit Agents (WebRTC, auto-reconnect) -> Silero VAD -> SenseVoice / FunASR ASR (dialect support) -> LLM interviewer (comforts first when emotional; asks new detail angles on repeated stories) -> CosyVoice 2 TTS (family voice clone). Storage: S3/R2.

## Modules
- `agent.py`: LiveKit voice agent entrypoint (VAD -> ASR -> LLM -> TTS)
- `asr/`: SenseVoice / FunASR, dialect support
- `interviewer/`: LLM memory interviewer (comfort, dedupe, follow-up questions)
- `tts/`: CosyVoice 2 family voice clone
- `diary/`: daily memory diary -> images -> short videos, stored in S3/R2

## Roadmap
- v0.1: voice chat + daily memory diary MVP
- v0.2: diary -> image -> short video with the elder's own voice

## Status
Early planning stage, building with Devin.
