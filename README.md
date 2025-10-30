# 顺丰运单详情自动操作脚本

## 功能概述
根据输入的顺丰运单号自动打开官网详情页, 在出现图形验证码后由人工输入验证码, 然后自动在页面底部查找并点击“展开详情”。

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

## 运行脚本
```powershell
# 示例运单号替换为真实单号
python sf_waybill_detail.py SF3286069356111

# 可选无头模式(不显示浏览器窗口)
python sf_waybill_detail.py SF3286069356111 --headless
```
运行后浏览器会打开页面, 当出现验证码输入框时, 终端将提示你输入验证码。输入完成后脚本会尝试提交, 然后滚动到底部寻找“展开详情”并点击。

## 注意事项
1. 页面结构可能变化, 若脚本无法找到元素, 需根据最新的 DOM 选择器调整代码。
2. 该脚本不会绕过验证码, 仅辅助操作, 验证码需人工识别输入。
3. 若需要 Edge 浏览器, 可修改代码中 `create_driver` 函数为 Edge 对应实现。
4. 若官网有反爬限制, 建议降低访问频率。

## 可能的改进方向
- 自动识别验证码 (OCR + 人机验证策略, 有风险且可能违反网站使用条款, 谨慎进行)
- 增加日志与异常处理, 保存页面HTML供后续分析
- 使用 `argparse` 支持批量运单号处理与重试逻辑
- 加入等待“展开详情”按钮动态加载的显式等待

## 免责声明
请遵守顺丰官网的使用条款, 合理合法使用本脚本。