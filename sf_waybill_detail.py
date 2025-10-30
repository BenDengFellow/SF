"""SF Express Waybill Detail Fetcher

功能:
1. 传入顺丰运单号, 打开官网详情页.
2. 等待页面出现图形验证码, 手动输入后提交.
3. 向下滚动到底部, 从下往上查找文字 "展开详情" 并点击.

使用:
    python sf_waybill_detail.py SF1234567890123

依赖: selenium, webdriver-manager

注意:
- 该页面可能使用反爬策略, 请控制访问频率.
- 验证码需要人工输入.
"""
from __future__ import annotations
import sys
import time
from dataclasses import dataclass
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

BASE_URL = "https://www.sf-express.com/chn/sc/waybill/waybill-detail/{waybill}"

@dataclass
class WaybillResult:
    waybill: str
    detail_expanded: bool
    page_title: str


def _detect_browser_binary(browser: str) -> Optional[str]:
    """在常见默认目录中尝试查找浏览器可执行文件路径."""
    import os
    candidates: list[str] = []
    if browser == "chrome":
        candidates = [
            r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            r"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
        ]
    elif browser == "edge":
        candidates = [
            r"C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
            r"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
        ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None


def create_driver(browser: str = "chrome", *, headless: bool = False, binary_path: Optional[str] = None) -> WebDriver:
    """创建浏览器驱动, 支持 chrome / edge.

    :param browser: 浏览器类型 (chrome|edge)
    :param headless: 是否无头模式
    :param binary_path: 浏览器可执行文件路径; 为空时尝试自动探测
    """
    browser = browser.lower()
    if browser not in {"chrome", "edge"}:
        raise ValueError("browser 必须是 'chrome' 或 'edge'")

    if not binary_path:
        binary_path = _detect_browser_binary(browser)
    if not binary_path:
        print(f"警告: 未在默认路径找到 {browser} 可执行文件, 将依赖系统 PATH. 若启动失败请安装或指定 --binary-path")

    if browser == "chrome":
        from selenium.webdriver.chrome.options import Options as ChromeOptions
        options = ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1280,900")
        if binary_path:
            options.binary_location = binary_path
        driver: WebDriver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    else:  # edge
        from selenium.webdriver.edge.options import Options as EdgeOptions
        options = EdgeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1280,900")
        if binary_path:
            options.binary_location = binary_path
        driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()), options=options)

    driver.set_page_load_timeout(60)
    return driver


def wait_for_captcha_and_input(driver: webdriver.Chrome, timeout: int = 120) -> None:
    """等待验证码图片出现, 提示用户输入, 然后提交.

    页面结构可能会变化, 这里通过寻找包含 'captcha' 的 img 或 input 以及提交按钮来做一个较宽松的匹配.
    """
    wait = WebDriverWait(driver, timeout)
    # 尝试等待输入框出现
    try:
        captcha_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name*='captcha'], input[id*='captcha'], input[class*='captcha']"))
        )
    except Exception:
        print("未检测到验证码输入框, 可能无需验证码或页面结构已变化.")
        return

    # 尝试找到验证码图片, 纯提示用
    try:
        captcha_img = driver.find_element(By.CSS_SELECTOR, "img[src*='captcha'], img[class*='captcha']")
        print("已检测到验证码图片, 请查看浏览器窗口.")
    except Exception:
        print("未找到验证码图片, 仅发现输入框.")

    code = input("请输入图片验证码并按回车确认: ").strip()
    captcha_input.clear()
    captcha_input.send_keys(code)
    # 尝试提交: 找按钮或回车
    try:
        submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit'], button[class*='captcha'], button[class*='submit']")
        submit_btn.click()
    except Exception:
        captcha_input.send_keys(Keys.ENTER)

    time.sleep(2)


def scroll_to_bottom(driver: webdriver.Chrome) -> None:
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def find_and_click_expand(driver: webdriver.Chrome) -> bool:
    """从页面底部开始向上寻找 '展开详情' 文字并点击."""
    # 先滚动到底部
    scroll_to_bottom(driver)

    # 获取所有元素文本, 从后往前搜索
    elements = driver.find_elements(By.XPATH, "//*[contains(text(),'展开详情')]")
    if not elements:
        print("未找到 '展开详情' 元素.")
        return False

    # 选择最靠后的一个 (通常最后加载的在列表末尾)
    target = elements[-1]
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", target)
    time.sleep(0.6)
    try:
        target.click()
        print("已点击 '展开详情'.")
        return True
    except Exception as e:
        print(f"点击失败: {e}")
        return False


def fetch_waybill_detail(waybill: str, *, browser: str = "chrome", headless: bool = False, binary_path: Optional[str] = None) -> WaybillResult:
    driver = create_driver(browser=browser, headless=headless, binary_path=binary_path)
    url = BASE_URL.format(waybill=waybill)
    print(f"打开: {url}")
    driver.get(url)

    # 等待可能的验证码并手动输入
    wait_for_captcha_and_input(driver)

    expanded = find_and_click_expand(driver)
    title = driver.title
    print(f"页面标题: {title}")

    result = WaybillResult(waybill=waybill, detail_expanded=expanded, page_title=title)
    # 保留窗口供进一步手动查看, 如需自动关闭可解除注释.
    # driver.quit()
    return result


def main(argv: list[str]) -> int:
    import argparse
    parser = argparse.ArgumentParser(description="顺丰运单详情自动化操作")
    parser.add_argument("waybill", help="顺丰运单号")
    parser.add_argument("--browser", choices=["chrome", "edge"], default="chrome", help="浏览器类型, 默认为 chrome")
    parser.add_argument("--headless", action="store_true", help="无头模式运行")
    parser.add_argument("--binary-path", dest="binary_path", help="浏览器可执行文件路径(可选)")
    args = parser.parse_args(argv[1:])

    result = fetch_waybill_detail(
        args.waybill,
        browser=args.browser,
        headless=args.headless,
        binary_path=args.binary_path,
    )
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
