import asyncio
import websockets

connected_clients = {}  # Dictionary to store WebSocket connections and their associated usernames

async def handle_connection(websocket, path):
    # Prompt user for a username
    username = await websocket.recv()
    
    # Add the connection and username to the dictionary
    connected_clients[websocket] = username
    join_message = f"{username} joined the chat"
    print(join_message)

    # Broadcast the join message to all connected clients
    tasks = [client.send(join_message) for client in connected_clients]
    if tasks:  # Check if there are tasks to be awaited
        await asyncio.gather(*tasks)

    try:
        async for message in websocket:
            # Format the message with the username
            formatted_message = f"{username}: {message}"

            # Prepare a list of tasks to send the formatted message to all connected clients except the sender
            tasks = [client.send(formatted_message) for client in connected_clients if client != websocket]
            if tasks:  # Check if there are tasks to be awaited
                await asyncio.gather(*tasks)
    except websockets.ConnectionClosed:
        pass
    finally:
        # Remove the connection and username from the dictionary
        del connected_clients[websocket]
        leave_message = f"{username} left the chat"
        print(leave_message)

        # Broadcast the leave message to all connected clients
        tasks = [client.send(leave_message) for client in connected_clients]
        if tasks:  # Check if there are tasks to be awaited
            await asyncio.gather(*tasks)

async def main():
    # Start the WebSocket server
    async with websockets.serve(handle_connection, "localhost", 8765):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())