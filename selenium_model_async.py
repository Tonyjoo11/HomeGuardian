# selenium_model_async.py

import asyncio
import os
from playwright.async_api import async_playwright

class AsyncModel:
    def __init__(self, html_file_path):
        self.html_file_path = html_file_path
        self.browser = None
        self.page = None
        self.predictions = {}

    async def start(self):
        playwright = await async_playwright().start()
        # headless=False로 설정하여 브라우저 창이 보이도록 함
        self.browser = await playwright.chromium.launch(headless=False)
        
        # 마이크 권한 허용
        context = await self.browser.new_context(
            permissions=["microphone"]
        )
        self.page = await context.new_page()

        # 로컬 HTML 파일의 절대 경로 가져오기
        html_file_absolute = os.path.abspath(self.html_file_path)
        html_file_url = 'file://' + html_file_absolute

        # 로컬 HTML 파일 열기
        await self.page.goto(html_file_url)

        # "Start" 버튼 클릭
        await self.page.click("button:has-text('Start')")

    async def update_predictions(self):
        # 예측 결과 수집
        elements = await self.page.query_selector_all("#label-container > div")
        current_predictions = {}
        for element in elements:
            text = await element.inner_text()
            try:
                class_name, score = text.split(": ")
                current_predictions[class_name] = float(score)
            except ValueError:
                continue
        self.predictions = current_predictions

    def get_current_predictions(self):
        return self.predictions

    async def stop(self):
        await self.browser.close()
