"""
app.py — Flask 後端主入口 (v1.5.0)
"""

import os
from flask import Flask

from modules.config import FLASK_HOST, FLASK_PORT
from modules.routes import register_all_routes

# 從根目錄提供靜態檔案
app = Flask(__name__, static_folder="static", static_url_path="/static")
app.config['JSON_AS_ASCII'] = False

# 註冊所有模組路由
register_all_routes(app)

if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=debug_mode, use_reloader=debug_mode)
