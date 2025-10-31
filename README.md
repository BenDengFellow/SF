# 顺丰运单批量与单票处理工具

本项目包含两个脚本（可打包为单文件 exe）：

1. 单票脚本：`sf_waybill_detail.py`
   - 打开顺丰详情页面，人工输入验证码并手动点击“展开详情”。
   - 点击悬浮确认窗口“确认”后生成当前页面 PDF。

2. 批量脚本：`sf_batch_waybill_ui.py`
   - 从 Excel 读取“序号”与“物流单号”列，表头可在前 20 行任意一行；遇到 `END` 停止。
   - 支持多工作表选择。自动从工作表名提取连续数字块作为潜在“月”前缀：
     * 若首数字块长度 1~2 且值 1-12 视为月份 (如 `1`, `02`, `12`) → 文件名与追踪文字使用 `M月-序号X-运单号`
     * 否则不加月份前缀（保持 `序号X-运单号`）
   - 每页 PDF 右上角显示追踪文字（含月前缀时加在最前）：`[M月-]序号{X}-{运单号}`
   - 每页右下角显示页码：`第 {page} / {total} 页`
   - 右边距增加 `4ch` 内边距避免文本贴边或裁切。

## 环境准备 (Windows PowerShell)
```powershell
cd c:\Ai\2025\SF
python -m venv .venv
. .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 单票脚本示例运行
```powershell
python sf_waybill_detail.py SF3286069356111
python sf_waybill_detail.py SF3286069356111 --headless  # 可选, 不建议初期使用
python sf_waybill_detail.py SF3286069356111 --driver-path "C:\Path\To\msedgedriver.exe"  # 离线驱动
```
确认窗口：
1. “确认” 生成 `output/<运单号>.pdf`
2. “下一单” 退出（单票模式即关闭）

## 批量脚本使用流程
```powershell
python sf_batch_waybill_ui.py
```
操作：
1. 选择 Excel 文件。
2. 选择工作表（按钮自动生成）。
3. 浏览器打开第一条运单（跳过表头），人工输入验证码并展开详情。
4. 点击“确认”生成 PDF；或点“下一单”跳过。
5. 循环直到出现 `END` 或文件结束。

Excel 示例：
| 序号 | 物流单号        |
|------|-----------------|
| 1    | SF3286069356111 |
| 2    | SF1234567890123 |
| 3    | END             |

## PDF 特性
- 使用 DevTools `Page.printToPDF`，非截图，可复制文本。
- header/footer 模板确保每页包含追踪文字与页码。
- 移除 DOM 覆盖层，避免首页重复追踪文字。
- 右侧 `4ch` 额外 padding 防止右上角文本贴边。

## 打包为单文件可执行（PyInstaller）
安装：
```powershell
pip install pyinstaller
```
构建：
```powershell
pyinstaller --clean --onefile --name sf_waybill_detail sf_waybill_detail.spec
pyinstaller --clean --onefile --name sf_batch_waybill_ui sf_batch_waybill_ui.spec
```
生成的 exe 在 `dist/` 目录。

### 离线 EdgeDriver
1. 下载与目标 Edge 版本匹配的 `msedgedriver.exe`
2. 放在项目根目录再执行打包（spec 会自动包含）
3. 运行时查找顺序：可执行目录 → `_MEIPASS` → 当前工作目录 → `C:\msedgedriver.exe`

## 常见问题
| 问题 | 原因 | 解决 |
|------|------|------|
| 无法获取 EdgeDriver | 离线且未放驱动 | 放置 `msedgedriver.exe` 同目录或联网运行 |
| PDF 为空/缺少详情 | 未手动点击“展开详情” | 展开后再点“确认” |
| Excel 未识别列 | 列名拼写或超出首 20 行 | 调整至前 20 行且列名精确匹配 |
| 无月前缀 | 表名首数字不在 1-12 | 属正常逻辑，可改表名 |

## 目录说明
- `sf_waybill_detail.py`：单票脚本
- `sf_batch_waybill_ui.py`：批量脚本与 Tkinter UI
- `sf_waybill_detail.spec` / `sf_batch_waybill_ui.spec`：打包配置
- `requirements.txt`：依赖文件
- `README.md`：项目说明

## 扩展建议
- 支持命令行参数：`--start-seq`、`--headless`
- 自动跳过已存在 PDF，记录日志
- 重试逻辑（验证码失败）
- 生成处理报告 (CSV/Excel)

## 免责声明
请遵守顺丰官网使用条款，合理合法使用本脚本。生成 PDF 含官网内容，不得用于未授权的商业再分发。
