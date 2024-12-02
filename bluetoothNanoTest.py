import asyncio
from bleak import BleakClient

# 아두이노 나노 33 BLE의 MAC 주소 (미리 확인 후 입력)
DEVICE_MAC_ADDRESS = "CE:04:78:05:29:87"  # 아두이노의 BLE MAC 주소
SERVICE_UUID = "6f742e01-ec6e-4621-a0db-7511cc6c46ad"  # 아두이노 서비스 UUID
CHARACTERISTIC_UUID = "00000000-0000-0000-0000-000000000000"  # 특성 UUID
RECONNECT_DELAY = 5

async def connect():
    """
    BLE Peripheral과 연결을 유지하는 함수.
    연결이 끊어지면 재시도합니다.
    """
    while True:
        try:
            print(f"Attempting to connect to {DEVICE_MAC_ADDRESS}...")
            async with BleakClient(DEVICE_MAC_ADDRESS) as client:
                print(f"Connected to device at {DEVICE_MAC_ADDRESS}")
                
                # 연결이 유지되는 동안 send_data 함수 호출
                
        except Exception as e:
            print(f"Connection failed: {e}")
            print(f"Reconnecting in {RECONNECT_DELAY} seconds...")
            await asyncio.sleep(RECONNECT_DELAY)


async def write_data_to_peripheral(data_to_write):
    # Peripheral에 연결
    async with BleakClient(DEVICE_MAC_ADDRESS) as client:
        print(f"Connected to device at {DEVICE_MAC_ADDRESS}")

        # 데이터 쓰기
        # data_to_write = input()  # 아두이노에 보낼 데이터
        await client.write_gatt_char(CHARACTERISTIC_UUID, data_to_write.encode("utf-8"))
        print(f"Data sent: {data_to_write}")
