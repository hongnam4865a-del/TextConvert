# TextConvert - Local Text & E-book Format Converter

A **lightweight, offline-first, text and e-book focused** batch format conversion tool. Everything runs locally — no file uploads, no network dependency, no ads, and no paid restrictions.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Supported Formats](#supported-formats)
- [Installation](#installation)
- [Usage](#usage)
  - [Command Line Interface](#command-line-interface)
  - [Python API](#python-api)
  - [Web Application](#web-application)
- [Project Architecture](#project-architecture)
- [Conversion Strategy](#conversion-strategy)
- [Logging](#logging)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)
- [Disclaimer](#disclaimer)
- [License](#license)

## Overview

TextConvert is designed for users who need to convert documents between common text, office, and e-book formats without relying on online services. It uses a modular engine architecture with a unified scheduling core that automatically picks the best available conversion path for each task.

## Features

- **Unified scheduling core**: convert any supported file with a single call — `convert_file(input, target_format)`
- **Intelligent format detection**: reads file magic bytes instead of relying solely on file extensions
- **HTML intermediate layer**: preserves paragraph structure and layout when converting between heterogeneous formats
- **Multi-engine support**: built-in engines for PyMuPDF, python-docx, ebooklib, and Markdown, plus optional external engines (Calibre, LibreOffice, WeasyPrint)
- **Batch conversion**: convert single files, whole folders, or recursively scan subdirectories
- **Comprehensive logging and error handling**: failures are logged without stopping the entire batch
- **Fully offline**: 100% local processing to protect your privacy

## Supported Formats

| Category | Formats |
|----------|---------|
| Plain text | `.txt`, `.md` |
| Web | `.html`, `.htm` |
| Office documents | `.docx` |
| E-books | `.epub`, `.mobi`, `.azw3` |
| Fixed-layout | `.pdf` |

> **Note**: Direct conversion between any two supported formats is available via the HTML intermediate layer. External engines may provide higher-quality direct conversion for specific format pairs.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/hongnam4865a-del/TextConvert.git
cd TextConvert
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Optional external engines

For better conversion quality on specific formats, install one or more of the following tools and ensure they are available in your system `PATH`:

| Engine | Recommended for | Download |
|--------|-----------------|----------|
| [Calibre](https://calibre-ebook.com/) | EPUB / MOBI / AZW3 interconversion | `ebook-convert` command |
| [LibreOffice](https://www.libreoffice.org/) | DOCX / PDF office documents | `soffice` command |
| [WeasyPrint](https://weasyprint.org/) | HTML to PDF (requires GTK on Windows) | installed via `pip` |

## Usage

### Command Line Interface

Convert a single file:

```bash
python cli.py input.pdf -f html
python cli.py input.md -f docx -o output.docx
```

Batch convert all files in a directory:

```bash
python cli.py ./books -f epub -r
```

Use a custom workspace:

```bash
python cli.py input.pdf -f html -w D:/MyWorkspace
```

#### CLI Options

| Option | Short | Description |
|--------|-------|-------------|
| `--format` | `-f` | Target format (required) |
| `--output` | `-o` | Custom output path |
| `--recursive` | `-r` | Recursively scan subdirectories |
| `--work-dir` | `-w` | Custom workspace directory |
| `--keep-temp` | `-k` | Keep temporary files after conversion |

### Python API

```python
from core.scheduler import convert_file, batch_convert

# Single file conversion
result = convert_file("input.pdf", "html")
print(result)  # Path to the generated file

# Batch conversion
results = batch_convert("./books", "epub", recursive=True)
for src, dst in results:
    print(f"{src} -> {dst}")
```

### Web Application

TextConvert includes a web interface inspired by [draw.io](https://www.drawio.com/): a blue top toolbar, white main workspace, collapsible sidebars, drag-and-drop upload, live logs, and one-click downloads.

#### Start the web server

```bash
python run_web.py
```

Then open your browser at:

```
http://127.0.0.1:8080
```

#### Web UI Features

- Drag and drop files onto the workspace or click to browse
- Select the target format: HTML, TXT, MD, DOCX, EPUB, or PDF
- Convert single files or entire batches
- Download converted files individually
- View recent results and live system logs in the right sidebar

## Project Architecture

```
.
├── cli.py                  # Command-line entry point
├── main.py                 # Project main entry point
├── run_web.py              # Web application launcher
├── config.py               # Global configuration
├── requirements.txt        # Python dependencies
├── README.md               # Chinese documentation
├── README_EN.md            # English documentation
├── 需求.md                  # Requirements document (Chinese)
├── core/                   # Scheduling core
│   ├── scheduler.py        # Unified conversion dispatcher
│   ├── format_detector.py  # File format detection
│   └── router.py           # Conversion route planner
├── engines/                # Conversion engines
│   ├── base.py             # Abstract base engine
│   ├── text_engine.py      # TXT / HTML engine
│   ├── markdown_engine.py  # Markdown engine
│   ├── pymupdf_engine.py   # PDF to HTML engine
│   ├── docx_engine.py      # DOCX engine
│   ├── epub_engine.py      # EPUB engine
│   ├── weasyprint_engine.py# HTML to PDF engine
│   ├── calibre_engine.py   # Calibre external engine wrapper
│   └── libreoffice_engine.py# LibreOffice external engine wrapper
├── utils/                  # Utilities
│   ├── logger.py           # Logging setup
│   └── file_utils.py       # File helpers
├── webapp/                 # Web application
│   ├── app.py              # FastAPI backend
│   ├── templates/
│   │   └── index.html      # Main page
│   └── static/
│       ├── style.css       # draw.io-inspired styles
│       └── app.js          # Frontend interactions
└── tests/                  # Tests
    ├── test_conversion.py  # Integration tests
    └── fixtures/           # Sample files for testing
```

## Conversion Strategy

TextConvert chooses the conversion path in the following order:

1. **Direct external engine conversion** when available and higher quality (for example, Calibre for EPUB ↔ MOBI, LibreOffice for DOCX ↔ PDF).
2. **HTML intermediate layer** (`source format → HTML → target format`) for all other supported combinations.
3. **Automatic fallback** to the best engine available in the current environment.

This design keeps the code modular and makes it easy to add new formats or engines in the future.

## Logging

Logs are written to both the console and the workspace `log/` directory. The default log file is named `convert_YYYYMMDD.log`.

You can change the log level or format in `config.py`:

```python
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:

- Reporting issues
- Submitting pull requests
- Code style and testing
- Branching strategy

Before submitting a pull request, please run the integration tests:

```bash
python tests/test_conversion.py
```

## Troubleshooting

### Import errors when running tests

Make sure you run tests from the project root:

```bash
python tests/test_conversion.py
```

The test script automatically adds the project root to `sys.path`.

### Calibre or LibreOffice is not detected

Ensure the corresponding executable is in your system `PATH`:

- Calibre: `ebook-convert`
- LibreOffice: `soffice`

On Windows, you may need to add the installation directory to your environment variables.

### WeasyPrint fails on Windows

WeasyPrint requires GTK runtime libraries on Windows. Install [GTK for Windows](https://www.gtk.org/docs/installations/windows/) and ensure `gtk3-runtime` is in your `PATH`. If WeasyPrint is unavailable, TextConvert will automatically fall back to Calibre for HTML → PDF conversion.

### PDF to HTML output does not look right

PDF is a fixed-layout format. The built-in PyMuPDF engine extracts text and basic structure; complex layouts may require manual cleanup or the use of an alternative engine.

### Batch conversion stops on one file

By default, `batch_convert` logs errors and continues with the remaining files. Check the log file in your workspace `log/` directory for details about the failed file.

## Disclaimer

This project is a personal open-source learning project intended for technical research and personal use only. Users are responsible for ensuring they have the legal right to convert any files they process.

## License

This project is licensed under the [MIT License](LICENSE).
