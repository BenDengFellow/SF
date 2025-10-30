"""SF Express Waybill Detail Fetcher

功能:
1. 传入顺丰运单号, 打开官网详情页.
2. 页面后续操作 (验证码、展开详情等) 由用户在浏览器中手动进行。

使用:
    python sf_waybill_detail.py SF1234567890123

依赖: selenium, webdriver-manager

注意:
- 该页面可能使用反爬策略, 请控制访问频率.
- 若出现验证码请手动处理 (脚本已移除验证码输入逻辑).
"""
from __future__ import annotations
import sys
import time
from dataclasses import dataclass
from typing import Optional
import base64
import os
import threading
try:
    import tkinter as tk
    from tkinter import messagebox
except Exception:
    tk = None  # headless/no tk available

from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver

BASE_URL = "https://www.sf-express.com/chn/sc/waybill/waybill-detail/{waybill}"

@dataclass
class WaybillResult:
    waybill: str
    page_title: str
    pdf_path: Optional[str] = None
    driver: Optional[WebDriver] = None  # 返回以便后续 UI 继续使用


def _detect_edge_binary() -> Optional[str]:
    """在常见默认目录中尝试查找 Edge 浏览器可执行文件路径."""
    import os
    candidates = [
        r"C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
        r"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None


def create_driver(*, headless: bool = False, binary_path: Optional[str] = None, driver_path: Optional[str] = None) -> WebDriver:
    """仅创建 Edge 浏览器驱动.

    优先使用 Selenium Manager 自动解析 msedgedriver; 若失败可手动指定 driver_path.
    Selenium 4.6+ 已内置 Selenium Manager, 不需要 webdriver-manager.
    """
    from selenium.webdriver.edge.options import Options as EdgeOptions
    from selenium.webdriver.edge.service import Service as EdgeServiceLocal
    if not binary_path:
        binary_path = _detect_edge_binary()
    if not binary_path:
        print("警告: 未在默认路径找到 Edge 可执行文件, 将依赖系统 PATH. 若启动失败请安装或指定 --binary-path")
    options = EdgeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,900")
    if binary_path:
        options.binary_location = binary_path

    try:
        # 直接调用, 让 Selenium Manager 自动下载/定位驱动
        driver = webdriver.Edge(options=options)
    except Exception as e:
        print(f"Selenium Manager 自动获取 EdgeDriver 失败: {e}")
        if not driver_path:
            # 常见本地缓存/手动放置位置尝试
            import os
            guesses = [
                os.path.join(os.getcwd(), "msedgedriver.exe"),
                r"C:\\msedgedriver.exe",
            ]
            for g in guesses:
                if os.path.exists(g):
                    driver_path = g
                    break
        if not driver_path:
            raise RuntimeError("无法自动获取 EdgeDriver。请手动下载 msedgedriver.exe 并使用 --driver-path 指定其路径。下载地址: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/") from e
        print(f"使用手动指定 EdgeDriver 路径: {driver_path}")
        service = EdgeServiceLocal(executable_path=driver_path)
        driver = webdriver.Edge(service=service, options=options)

    driver.set_page_load_timeout(60)
    return driver


## 已移除验证码自动处理函数 (wait_for_captcha_and_input)


## 自动查找并点击“展开详情”逻辑已移除，保留简洁核心功能。


def _print_page_to_pdf(driver: WebDriver, waybill: str, output_dir: str = "output") -> Optional[str]:
    """使用 Chromium DevTools 协议将当前页面保存为 PDF.

    Edge / Chrome 驱动均支持 `execute_cdp_cmd('Page.printToPDF', params)`。
    返回生成的 PDF 路径, 若失败返回 None.
    """
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        pdf_b64 = driver.execute_cdp_cmd("Page.printToPDF", {
            "landscape": False,
            "printBackground": True,
            "preferCSSPageSize": True,
        })["data"]
        pdf_data = base64.b64decode(pdf_b64)
        pdf_path = os.path.join(output_dir, f"{waybill}.pdf")
        with open(pdf_path, "wb") as f:
            f.write(pdf_data)
        print(f"PDF 已生成: {pdf_path}")
        return pdf_path
    except Exception as e:
        print(f"PDF 生成失败: {e}")
        return None


def fetch_waybill_detail(waybill: str, *, headless: bool = False, binary_path: Optional[str] = None, driver_path: Optional[str] = None, debug: bool = False) -> WaybillResult:
    driver = create_driver(headless=headless, binary_path=binary_path, driver_path=driver_path)
    url = BASE_URL.format(waybill=waybill)
    print(f"打开: {url}")
    driver.get(url)

    # 已移除验证码处理逻辑; 若页面出现验证码请在浏览器手动输入后继续查看。

    # 如果需要调试，保存初始页面源码与截图，用户自行点击展开详情
    if debug:
        try:
            html_path = f"debug_{waybill}.html"
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            screenshot_path = f"debug_{waybill}.png"
            driver.save_screenshot(screenshot_path)
            print(f"调试: 已保存页面源码 -> {html_path}, 截图 -> {screenshot_path}")
        except Exception as e:
            print(f"调试文件保存失败: {e}")
    title = driver.title
    print(f"页面标题: {title}")

    pdf_path = None

    result = WaybillResult(waybill=waybill, page_title=title, pdf_path=pdf_path, driver=driver)
    # 保留窗口供进一步手动查看, 如需自动关闭可解除注释.
    # driver.quit()
    return result


def launch_confirmation_ui(driver: WebDriver, waybill: str) -> Optional[str]:
    """启动 Tkinter UI:
    - 按钮 “确认”: 在你已于浏览器完成验证码+展开详情后，点击生成 PDF。
    - 按钮 “下一单”: 在 PDF 生成完成后可点击，退出程序 (关闭窗口与浏览器)。

    若系统无 Tkinter，则使用命令行交互 (回车生成 PDF, 再次回车退出)。
    """
    pdf_path: Optional[str] = None

    if tk is None:
        input("请在浏览器中完成验证码与展开详情后按回车生成 PDF...")
        pdf_path = _print_page_to_pdf(driver, waybill)
        input("PDF 已生成, 按回车退出程序...")
        try:
            driver.quit()
        except Exception:
            pass
        return pdf_path

    def on_confirm():
        nonlocal pdf_path
        if confirm_btn['state'] == tk.DISABLED:
            return
        confirm_btn.config(state=tk.DISABLED)
        status_var.set("正在生成 PDF...")
        root.update_idletasks()
        pdf_path = _print_page_to_pdf(driver, waybill)
        if pdf_path:
            status_var.set("PDF 已生成: 点击 '下一单' 退出")
            next_btn.config(state=tk.NORMAL)
        else:
            status_var.set("生成失败, 可重试")
            confirm_btn.config(state=tk.NORMAL)

    def on_next():
        status_var.set("正在退出...")
        try:
            driver.quit()
        except Exception:
            pass
        root.after(300, root.destroy)

    root = tk.Tk()
    root.title("顺丰运单 PDF 生成")
    # 先创建后定位到屏幕右上角 (带一点边距)
    window_w, window_h = 420, 200
    try:
        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()
    except Exception:
        screen_w, screen_h = 1920, 1080
    margin = 12
    pos_x = screen_w - window_w - margin
    pos_y = margin
    root.geometry(f"{window_w}x{window_h}+{pos_x}+{pos_y}")
    # 置顶防止被浏览器遮挡
    root.attributes('-topmost', True)
    msg = tk.Label(root, text=(
        f"运单: {waybill}\n请先在浏览器中: 1) 输入验证码并确认 2) 点击展开详情\n"
        "完成后点击 '确认' 生成 PDF; 生成后点 '下一单' 退出"), wraplength=400, justify="left")
    msg.pack(pady=10)
    status_var = tk.StringVar(value="等待你的操作...")
    confirm_btn = tk.Button(root, text="确认", width=14, command=on_confirm)
    confirm_btn.pack(pady=4)
    next_btn = tk.Button(root, text="下一单", width=14, state=tk.DISABLED, command=on_next)
    next_btn.pack(pady=4)
    status = tk.Label(root, textvariable=status_var, fg="#333")
    status.pack(pady=6)

    root.mainloop()
    return pdf_path


def main(argv: list[str]) -> int:
    import argparse
    parser = argparse.ArgumentParser(description="顺丰运单详情自动化操作")
    parser.add_argument("waybill", help="顺丰运单号")
    parser.add_argument("--headless", action="store_true", help="Edge 无头模式运行 (不建议与 UI 同用)")
    parser.add_argument("--binary-path", dest="binary_path", help="Edge 浏览器可执行文件路径(可选)")
    parser.add_argument("--driver-path", dest="driver_path", help="手动指定 msedgedriver.exe 路径, Selenium Manager 失败时使用")
    parser.add_argument("--debug", action="store_true", help="失败时保存页面源码与截图")
    args = parser.parse_args(argv[1:])

    result = fetch_waybill_detail(
        args.waybill,
        headless=args.headless,
        binary_path=args.binary_path,
        driver_path=args.driver_path,
        debug=args.debug,
    )

    # 默认启动 UI
    print("已打开运单页面。请在浏览器完成验证码与展开详情后, 使用弹出的窗口生成 PDF。")
    if result.driver:
        pdf_path = launch_confirmation_ui(driver=result.driver, waybill=args.waybill)
        if pdf_path:
            result.pdf_path = pdf_path
        else:
            print("未生成 PDF")
    else:
        print("内部错误: 未找到浏览器驱动实例, 无法生成 PDF")
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
