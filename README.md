# 顺丰运单详情自动操作脚本

## 功能概述
根据输入的顺丰运单号自动打开官网详情页 (仅使用 Windows Edge 浏览器)。脚本不再处理图形验证码与“展开详情”点击，若页面出现相关内容请在浏览器中手动操作。脚本使用 Selenium Manager 自动解析/下载 EdgeDriver, 无需额外安装。若自动获取失败，可手动下载 msedgedriver.exe 并使用 --driver-path 指定。

## 文件
- `sf_waybill_detail.py` 主脚本
- `requirements.txt` 依赖列表

## 环境准备 (Windows PowerShell)
```powershell
# 进入工作目录
cd c:\Ai\2025\SF

# 创建虚拟环境(如尚未创建)
python -m venv .venv

# 激活 (PowerShell)
. .venv\Scripts\Activate.ps1

# 安装依赖
pip install -r requirements.txt
```

## 运行脚本 (仅 Edge，默认弹出 UI)
```powershell
# 示例运单号替换为真实单号
python sf_waybill_detail.py SF3286069356111

# 无头模式(不显示浏览器窗口) - 不建议, UI 仍需桌面环境
python sf_waybill_detail.py SF3286069356111 --headless

# 若自动无法获取 EdgeDriver, 手动指定下载好的驱动路径
python sf_waybill_detail.py SF3286069356111 --driver-path "C:\Path\To\msedgedriver.exe"
```
运行后浏览器会打开页面，验证码输入与“展开详情”由你手动完成。脚本会自动在屏幕右上角置顶弹出一个窗口：
1. 点击“确认” -> 生成 `output/<运单号>.pdf`
2. 点击“下一单” -> 关闭浏览器与窗口并退出程序

## 注意事项
1. 页面结构可能变化, 若脚本无法找到元素, 需根据最新的 DOM 选择器调整代码。
2. 当前脚本仅支持 Edge 浏览器, 自动探测 Edge 可执行文件路径; 失败时可使用 `--binary-path` 指定浏览器, 使用 `--driver-path` 指定驱动。
3. 若官网有反爬限制, 建议降低访问频率。

## 可能的改进方向
- 增加日志与异常处理, 保存页面HTML供后续分析
- 使用 `argparse` 支持批量运单号处理与重试逻辑
  (已移除验证码与自动点击“展开详情”逻辑, 若再次需要可在脚本中恢复相关函数)
- UI 置顶显示在右上角，包含“确认”和“下一单”两个按钮，后续可扩展批量运单循环

## 免责声明
请遵守顺丰官网的使用条款, 合理合法使用本脚本。