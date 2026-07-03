# QR Scan

从图片文件中解码二维码和条形码。提供 GUI 和 CLI 两种使用方式。

---

## 用法

### GUI（可以直接从`Releases`中下载可执行文件）

双击 `QRScanner.exe`，或执行 `python qrscan_gui.py`。

1. 输入/粘贴图片路径（或点「浏览」选择），也可以将文件从资源管理器拖入文件，等价于填入路径。
2. 点「解码」
3. 结果区出现文本，选中后 Ctrl+C 复制

通过 Ctrl+Shift+C 复制的路径粘贴时会自动去掉首尾引号。

### CLI

```bash
pip install -r requirements.txt

python qrscan.py image.png       # 单张图片
python qrscan.py -j image.png    # JSON 输出
python qrscan.py -q *.png        # 静默模式，只输出解码数据
python qrscan.py -t image.jpg    # 标注条码类型
```
> 将`image.png`改成自己的文件路径。
---

## 文件

| 文件 | 说明 |
|------|------|
| `qrscan.py` | CLI 工具：argparse 解析参数 → pyzbar 解码 → 文本/JSON 输出，3 种退出码 |
| `qrscan_gui.py` | GUI 界面：tkinter 对话框，通过 Win32 WM_DROPFILES 支持文件拖放 |
| `requirements.txt` | pip 依赖清单 |

---


## 依赖

```
pyzbar>=0.1.9
Pillow>=10.0
```

pyzbar 调用 libzbar C 库，打包时已包含 `libzbar-64.dll` 和 `libiconv.dll`。Pillow 用于图片解码及 RGB 转换。GUI 基于 Python 内置 tkinter，无额外依赖。


退出码：`0` 找到条码，`1` 未找到，`2` 文件错误。

---

## 支持的格式

**图片**：PNG, JPG, BMP, GIF, TIFF, WebP（Pillow 支持的全部格式）。

**条码**：QRCODE, EAN-13, EAN-8, UPC-A, UPC-E, CODE-128, CODE-39, Data Matrix, PDF417 等（libzbar 支持的全部类型）。
