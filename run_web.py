#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""启动 Web 应用"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run("webapp.app:app", host="127.0.0.1", port=8080, reload=False)
