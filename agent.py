from livekit.agents import JobContext, WorkerOptions, cli
from livekit.agents.voice import Agent, AgentSession
from livekit.plugins import silero

PROMPT = "You chat warmly with an elder about their younger years. Comfort first if emotional; ask new details on repeated stories."

async def entrypoint(ctx: JobContext):
    await ctx.connect()
    session = AgentSession(
        vad=silero.VAD.load(),
        stt=None,  # TODO: SenseVoice / FunASR
        llm=None,  # TODO: memory interviewer LLM
        tts=None,  # TODO: CosyVoice 2
    )
    await session.start(agent=Agent(instructions=PROMPT), room=ctx.room)

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
