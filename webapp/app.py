#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Web 应用后端（FastAPI）

参考 draw.io 风格：蓝色顶部工具栏 + 白色主工作区。
"""

import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import config as app_config
from core.scheduler import ConversionError, batch_convert, convert_file
from utils.file_utils import ensure_dir
from utils.logger import setup_logging

# Web 应用专属工作目录
WEB_WORK_DIR = Path("D:/TextConvertWorkspaceWeb")
ensure_dir(WEB_WORK_DIR)
UPLOAD_DIR = ensure_dir(WEB_WORK_DIR / "uploads")
OUTPUT_DIR = ensure_dir(WEB_WORK_DIR / "output")

logger = setup_logging(WEB_WORK_DIR, level=app_config.LOG_LEVEL)

app = FastAPI(title="TextConvert Web", version="1.0.0")

# 静态文件与模板
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")


def _safe_filename(name: str) -> str:
    """清理文件名，保留基本字符"""
    return "".join(c for c in name if c.isalnum() or c in " ._-").strip()


def _work_id() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:6]


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/formats")
async def api_formats():
    """返回支持的目标格式"""
    return {
        "formats": sorted(app_config.SUPPORTED_FORMATS),
        "primary": ["html", "txt", "md", "docx", "epub", "pdf"],
    }


@app.post("/api/convert")
async def api_convert(target_format: str = Form(...), file: UploadFile = File(...)):
    """单文件转换"""
    target_format = target_format.lower().strip()
    if target_format not in app_config.SUPPORTED_FORMATS:
        raise HTTPException(status_code=400, detail=f"不支持的目标格式: {target_format}")

    safe_name = _safe_filename(Path(file.filename).name)
    if not safe_name:
        safe_name = "uploaded"

    wid = _work_id()
    upload_path = UPLOAD_DIR / f"{wid}_{safe_name}"
    try:
        with open(upload_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception as exc:
        logger.exception("上传文件保存失败")
        raise HTTPException(status_code=500, detail=f"保存上传文件失败: {exc}")
    finally:
        file.file.close()

    output_stem = Path(safe_name).stem
    try:
        result_path = convert_file(
            upload_path,
            target_format,
            output_path=OUTPUT_DIR / f"{output_stem}.{target_format}",
            work_dir=WEB_WORK_DIR,
        )
    except ConversionError as exc:
        logger.error("转换失败: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("转换过程异常")
        raise HTTPException(status_code=500, detail=f"转换异常: {exc}") from exc

    return {
        "success": True,
        "filename": result_path.name,
        "original_name": safe_name,
        "target_format": target_format,
        "size": result_path.stat().st_size,
        "download_url": f"/api/download/{result_path.name}",
    }


@app.post("/api/batch")
async def api_batch(target_format: str = Form(...), files: List[UploadFile] = File(...)):
    """批量转换"""
    target_format = target_format.lower().strip()
    if target_format not in app_config.SUPPORTED_FORMATS:
        raise HTTPException(status_code=400, detail=f"不支持的目标格式: {target_format}")

    batch_dir = UPLOAD_DIR / _work_id()
    ensure_dir(batch_dir)

    saved: List[Path] = []
    for uploaded in files:
        safe_name = _safe_filename(Path(uploaded.filename).name)
        if not safe_name:
            safe_name = "uploaded"
        dest = batch_dir / safe_name
        try:
            with open(dest, "wb") as f:
                shutil.copyfileobj(uploaded.file, f)
            saved.append(dest)
        except Exception:
            logger.exception("批量上传保存失败: %s", uploaded.filename)
        finally:
            uploaded.file.close()

    if not saved:
        raise HTTPException(status_code=400, detail="没有可转换的文件")

    try:
        results = batch_convert(batch_dir, target_format, work_dir=WEB_WORK_DIR)
    except ConversionError as exc:
        logger.error("批量转换失败: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("批量转换过程异常")
        raise HTTPException(status_code=500, detail=f"批量转换异常: {exc}") from exc

    return {
        "success": True,
        "count": len(results),
        "results": [
            {
                "filename": p.name,
                "size": p.stat().st_size,
                "download_url": f"/api/download/{p.name}",
            }
            for p in results
        ],
    }


@app.get("/api/files")
async def api_files(limit: int = 50):
    """列出最近的转换结果"""
    files = sorted(OUTPUT_DIR.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)
    return {
        "files": [
            {
                "name": p.name,
                "size": p.stat().st_size,
                "modified": datetime.fromtimestamp(p.stat().st_mtime).isoformat(),
                "download_url": f"/api/download/{p.name}",
            }
            for p in files[:limit] if p.is_file()
        ]
    }


@app.get("/api/download/{filename}")
async def api_download(filename: str):
    """下载转换结果"""
    safe_name = _safe_filename(filename)
    file_path = OUTPUT_DIR / safe_name
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="文件不存在")
    return FileResponse(file_path, filename=safe_name)


@app.get("/api/logs")
async def api_logs(lines: int = 100):
    """读取最近日志"""
    log_dir = WEB_WORK_DIR / app_config.LOG_DIR_NAME
    log_files = sorted(log_dir.glob("convert_*.log"), reverse=True)
    if not log_files:
        return {"logs": []}
    try:
        text = log_files[0].read_text(encoding="utf-8", errors="replace")
        return {"logs": text.strip().splitlines()[-lines:]}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"读取日志失败: {exc}") from exc
