import asyncio
import os
from google import genai


async def list_models():
    try:
        # Client will automatically pick up GOOGLE_API_KEY from environment if set
        client = genai.Client()
        print("Listing models...")
        # The list method supports pagination
        pager = await client.aio.models.list()
        print("Available models:")
        async for model in pager:
            # Filter to only show generateContent supported models to reduce noise if needed,
            # but let's see everything for now.
            print(f"- {model.name}: {model.supported_generation_methods}")
    except Exception as e:
        print(f"Error listing models: {e}")


if __name__ == "__main__":
    asyncio.run(list_models())
