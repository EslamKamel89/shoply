import asyncio


async def demo_background_service(message: str) -> None:
    await asyncio.sleep(5)
    print(f"[SERVICE] {message}")
