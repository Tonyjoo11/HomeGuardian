import asyncio
import bluetooth
from concurrent.futures import ThreadPoolExecutor

def create_server_socket():
    """
    블루투스 서버 소켓을 생성하고 리턴합니다.
    """
    server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    server_socket.bind(("", bluetooth.PORT_ANY))
    server_socket.listen(1)
    port = server_socket.getsockname()[1]
    print(f"Listening for connections on port {port}")
    return server_socket, port

async def accept_client_connection(server_socket):
    """
    클라이언트 연결을 비동기적으로 수락합니다.
    """
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        client_socket, address = await loop.run_in_executor(executor, server_socket.accept)
    print(f"Accepted connection from {address}")
    return client_socket, address

async def handle_client_communication(client_socket, message):
    """
    클라이언트와 비동기적으로 통신하며 매개변수로 받은 메시지를 전송합니다.
    """
    try:
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            # 클라이언트로부터 데이터 수신
            data = await loop.run_in_executor(executor, client_socket.recv, 1024)
            if data:
                print(f"Received: {data.decode('utf-8')}")

            # 메시지 전송
            await loop.run_in_executor(executor, client_socket.send, message.encode('utf-8'))
            print(f"Sent: {message}")
    except Exception as e:
        print(f"Error during communication: {e}")
        
def close_server_socket(server_socket):
    """
    서버 소켓을 닫습니다.
    """
    server_socket.close()
    print("Server socket closed.")

async def main():
    """
    비동기 블루투스 서버 실행을 위한 메인 함수입니다.
    """
    server_socket, port = create_server_socket()
    try:
        client_socket, address = await accept_client_connection(server_socket)
        message = input("Enter a message to send to the client: ")
        await handle_client_communication(client_socket, message)
    except KeyboardInterrupt:
        print("\nServer shutting down.")
    finally:
        close_server_socket(server_socket)

# if __name__ == "__main__":
    # asyncio.run(main())
