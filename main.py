# main_async.py

import asyncio
from selenium_model_async import AsyncModel

async def main():
    model = AsyncModel("test.html")
    await model.start()

    try:
        while True:  # 필요에 따라 반복 횟수 조절
            await asyncio.sleep(1)
            await model.update_predictions()
            predictions = model.get_current_predictions()
            print("현재 예측값:", predictions)
    finally:
        await model.stop()

asyncio.run(main())
