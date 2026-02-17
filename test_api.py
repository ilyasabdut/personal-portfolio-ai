import os
import httpx
import asyncio

async def test_api():
    api_key = os.getenv('LLM_API_KEY')
    api_url = os.getenv('LLM_API_URL')
    model = os.getenv('LLM_MODEL', 'gemma2-9b-it')

    print(f"Testing API with:")
    print(f"  API Key: {api_key[:10]}...")
    print(f"  API URL: {api_url}")
    print(f"  Model: {model}")

    # Handle both API URLs with and without trailing /v1
    if not api_url.endswith('/v1') and not api_url.endswith('/v1/'):
        api_url = f"{api_url}/v1"

    full_url = f"{api_url}/chat/completions"
    print(f"\nFull URL: {full_url}")

    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": "hi"}
        ],
        "stream": False,
        "max_tokens": 100
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                full_url,
                headers=headers,
                json=payload,
                timeout=30.0
            )

            print(f"\nResponse status: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")

            if response.status_code == 200:
                data = response.json()
                print(f"\nResponse data:")
                print(f"  Model: {data.get('model')}")
                print(f"  Choices: {len(data.get('choices', []))}")
                if data.get('choices'):
                    print(f"  Content: {data['choices'][0]['message']['content']}")
            else:
                print(f"\nError response:")
                print(f"  Text: {response.text}")
                try:
                    error_data = response.json()
                    print(f"  Error: {error_data.get('error', {})}")
                except:
                    pass

    except Exception as e:
        print(f"\nException occurred: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    asyncio.run(test_api())
