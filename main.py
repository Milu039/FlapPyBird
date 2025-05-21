import asyncio

from src.flappy import Flappy

if __name__ == "__main__":
    asyncio.run(Flappy().start())
'''
import asyncio
import sys

from src.flappy_copy import Flappy

if __name__ == "__main__":
    # Check if an argument was passed to run as server
    if len(sys.argv) > 1 and sys.argv[1] == "server":
        from src.server import FlappyServer
        server = FlappyServer()
        server.start()
    else:
        # Run the game client
        asyncio.run(Flappy().start())'''