# TextConvert - 本地文本/电子书格式转换工具

一款**本地离线、轻量化、垂直专注文本/电子书领域**的格式批量转换工具。纯本地运行、不上传文件、无网络依赖、无广告、无付费限制。

## 特性

- **统一调度架构**：`convert_file(input, target_format)` 一行代码完成转换
- **智能格式识别**：读取文件头魔数，不依赖后缀名
- **HTML 通用中间层**：最大程度保留段落、结构与排版
- **多引擎适配**：内置 PyMuPDF / python-docx / ebooklib / Markdown，并支持 Calibre、LibreOffice、WeasyPrint 外部引擎
- **批量转换**：支持单文件、文件夹、递归遍历
- **完整日志与异常处理**：失败不中断，记录详细日志
- **完全离线**：100% 本地处理，保护隐私

## 支持格式

| 类型 | 格式 |
|------|------|
| 纯文本 | `.txt` `.md` |
| 网页 | `.html` |
| 办公文档 | `.docx` |
| 电子书 | `.epub` `.mobi` |
| 固定排版 | `.pdf` |

## 安装

```bash
pip install -r requirements.txt
```

可选外部引擎（提升特定格式质量）：
- [Calibre](https://calibre-ebook.com/)：EPUB / MOBI / AZW3 互转
- [LibreOffice](https://www.libreoffice.org/)：DOCX / PDF 办公文档互转

## 使用

### 命令行

```bash
# 单文件转换
python cli.py input.pdf -f html
python cli.py input.md -f docx -o output.docx

# 批量转换（目录）
python cli.py ./books -f epub -r

# 自定义工作区
python cli.py input.pdf -f html -w D:/MyWorkspace
```

### Python API

```python
from core.scheduler import convert_file, batch_convert

# 单文件
result = convert_file("input.pdf", "html")

# 批量
results = batch_convert("./books", "epub", recursive=True)
```

## Web 应用

提供与 [draw.io](https://www.drawio.com/) 风格类似的网页版界面：蓝色顶部工具栏、白色主工作区、左右侧边栏、拖放上传、实时日志、结果下载。

### 启动

```bash
python run_web.py
```

打开浏览器访问：http://127.0.0.1:8080

### 功能

- 拖放或点击上传文件
- 选择目标格式（HTML / TXT / MD / DOCX / EPUB / PDF）
- 单文件或批量转换
- 转换结果一键下载
- 右侧实时查看最近结果与系统日志

## 项目架构

```
.
├── cli.py                  # 命令行入口
├── main.py                 # 项目主入口
├── run_web.py              # Web 应用启动入口
├── config.py               # 全局配置
├── requirements.txt        # Python 依赖
├── README.md               # 项目说明
├── 需求.md                 # 需求文档
├── core/                   # 调度核心
│   ├── scheduler.py
│   ├── format_detector.py
│   └── router.py
├── engines/                # 转换引擎
│   ├── base.py
│   ├── text_engine.py
│   ├── markdown_engine.py
│   ├── pymupdf_engine.py
│   ├── docx_engine.py
│   ├── epub_engine.py
│   ├── weasyprint_engine.py
│   ├── calibre_engine.py
│   └── libreoffice_engine.py
├── utils/                  # 工具
│   ├── logger.py
│   └── file_utils.py
├── webapp/                 # Web 应用
│   ├── app.py              # FastAPI 后端
│   ├── templates/
│   │   └── index.html      # 主页面
│   └── static/
│       ├── style.css       # draw.io 风格样式
│       └── app.js          # 前端交互
└── tests/                  # 测试
    ├── test_conversion.py  # 集成测试
    └── fixtures/           # 测试样例文件
```

## 转换策略

1. 优先使用外部引擎直接转换（如 Calibre EPUB->MOBI、LibreOffice DOCX->PDF）
2. 否则通过 **源格式 -> HTML -> 目标格式** 的中间层完成
3. 自动选择当前环境可用的最佳引擎

## 日志

日志默认输出到工作区 `log/` 目录，同时打印到控制台。

## 免责声明

本项目为纯个人学习开源项目，仅供技术研究与个人自用。用户需自行保证文件版权合法性。
