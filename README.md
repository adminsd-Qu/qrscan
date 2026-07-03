# qrscan

从图片文件中解码二维码和条形码。提供 GUI 和命令行两种使用方式。

---

## 依赖

```
pyzbar>=0.1.9
Pillow>=10.0
```

pyzbar 调用 libzbar C 库，需要 `libzbar-64.dll` 和 `libiconv.dll`（打包时已包含）。Pillow 用于打开图片并转为 RGB。

GUI 使用 Python 内置 tkinter，无额外依赖。

---

## 文件说明

```
qrscan.py          CLI 工具，解析命令行参数 → 调用 pyzbar → 格式化输出
qrscan_gui.py      GUI 界面，tkinter 对话框，import qrscan 的解码函数
requirements.txt   pip 依赖清单
dist/
  QRScanner.exe    PyInstaller 打包的单文件 exe（31MB，包含 Python 解释器及所有依赖）
```

### qrscan.py

- `decode_image(path)` — 核心解码，用 Pillow 打开图片转 RGB 后交给 pyzbar，返回 Decoded 对象列表。失败返回 None。
- `format_text(file_results)` — 纯文本格式化，支持 quiet（只输出数据）和 show_types（标注条码类型）。
- `format_json(file_results)` — JSON 输出。
- `main()` — argparse 解析，遍历文件调用 decode_image，确定退出码后输出。

### qrscan_gui.py

- `QRScannerApp(tk.Tk)` — 主窗口（520×380，固定大小，居中）。
- `_on_path_change()` — 监听输入框变化，自动去掉首尾引号（适配 Ctrl+Shift+C 复制的路径）。
- `_browse()` — filedialog 选择图片，过滤常见图片后缀。
- `_decode()` — 取输入框路径，调 `decode_image()`，结果写入只读 Text 控件。
- `_open_help()` — 通过 `os.startfile()` 打开随 exe 一起打包的 README.md。

---

## 用法

### GUI

双击 `dist/QRScanner.exe`。

1. 在输入框粘贴图片路径（或点「浏览」选择文件）
2. 点「解码」
3. 结果区出现解码文本，选中后 Ctrl+C 复制
4. 点「帮助」打开本说明

在资源管理器中对图片文件按 Ctrl+Shift+C 复制路径，粘贴到输入框会自动去掉首尾双引号。

### CLI

```bash
pip install -r requirements.txt

python qrscan.py image.png              # 单张解码
python qrscan.py -j image.png           # JSON 输出
python qrscan.py -q *.png               # 静默模式，只输出解码数据
python qrscan.py -t image.jpg           # 标注条码类型
```

退出码：

| 值 | 含义 |
|----|------|
| 0  | 至少识别到一个条码 |
| 1  | 所有文件均未识别到条码 |
| 2  | 文件错误（不存在/无权限） |

---

## 支持的输入格式

图片格式由 Pillow 决定：PNG、JPG、BMP、GIF、TIFF、WebP。

条码类型由 libzbar 决定：QRCODE、EAN-13、EAN-8、UPC-A、UPC-E、CODE-128、CODE-39、Data Matrix、PDF417 等。

---

## 构建 exe

```bash
pip install pyinstaller
cd qrscan
pyinstaller --onefile --noconsole --name "QRScanner" \
    --add-data "README.md;." \
    --add-binary "<pyzbar路径>/libiconv.dll;pyzbar" \
    --add-binary "<pyzbar路径>/libzbar-64.dll;pyzbar" \
    qrscan_gui.py
```

pyzbar 路径可通过 `python -c "import pyzbar,os; print(os.path.dirname(pyzbar.__file__))"` 获取。

`--add-binary` 手动添加 libzbar 及其依赖 libiconv 是因为 PyInstaller 的 pyzbar hook 不会自动收集 libiconv.dll。
