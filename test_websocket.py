import asyncio
import json
import websockets


async def test_websocket():

    uri = "ws://127.0.0.1:8000/ws/chat"

    print("Connecting...")

    async with websockets.connect(
        uri,
        open_timeout=30,
        ping_interval=None
    ) as websocket:

        print("Connected!")

        question = "What is deep learning?"

        print("\nQuestion:")
        print(question)

        await websocket.send(question)

        print("\nResponse:\n")

        while True:

            response = await websocket.recv()

            data = json.loads(response)

            if data["type"] == "sources":

                print("\nSources:")
                for source in data["sources"]:
                    print(
                        f"[Source {source['source_id']}] "
                        f"{source['document']} - "
                        f"Page {source['page']}"
                    )

                print("\nAnswer:\n", end="")

            elif data["type"] == "token":

                print(
                    data["content"],
                    end="",
                    flush=True
                )

            elif data["type"] == "done":

                print("\n\nGeneration complete.")
                break


asyncio.run(test_websocket())