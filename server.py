#!/usr/bin/env python3
"""
静态文件服务器 - 公网访问店铺网站
提供 index.html 和 uploads/ 目录的静态文件服务
"""

import http.server
import socketserver
import os
import sys
import signal

# 配置
PORT = 80  # 默认端口，可通过命令行参数修改
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    """自定义HTTP处理器"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def log_message(self, format, *args):
        """简化日志输出"""
        print(f"[{self.address_string()}] {args[0]}")
    
    def do_GET(self):
        """处理GET请求"""
        # 根路径重定向到index.html
        if self.path == '/':
            self.path = '/index.html'
        return super().do_GET()

    def end_headers(self):
        """添加HTTP头以禁用缓存并尝试清除Service Worker"""
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        # 尝试清除Service Worker和其他站点数据
        self.send_header("Clear-Site-Data", '"cache", "storage", "executionContexts"')
        super().end_headers()

def signal_handler(sig, frame):
    """优雅退出"""
    print("\n🛑 服务器已停止")
    sys.exit(0)

def main():
    global PORT
    
    # 命令行参数解析
    if len(sys.argv) > 1:
        try:
            PORT = int(sys.argv[1])
        except ValueError:
            print(f"⚠️ 无效端口号: {sys.argv[1]}, 使用默认端口 80")
            PORT = 80
    
    # 检查是否需要root权限 (端口 < 1024)
    if PORT < 1024 and os.geteuid() != 0:
        print(f"⚠️ 端口 {PORT} 需要管理员权限")
        print(f"请使用: sudo python server.py {PORT}")
        print(f"或使用高端口: python server.py 8080")
        sys.exit(1)
    
    # 检查index.html是否存在
    index_path = os.path.join(DIRECTORY, 'index.html')
    if not os.path.exists(index_path):
        print("⚠️ 警告: index.html 不存在")
        print("请先在管理后台发布网站!")
    
    # 设置信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 启动服务器
    with socketserver.TCPServer(("0.0.0.0", PORT), QuietHandler) as httpd:
        print("=" * 50)
        print("🌐 店铺网站服务器已启动")
        print("=" * 50)
        print(f"📍 本地访问: http://localhost:{PORT}")
        print(f"🌍 公网访问: http://[您的公网IP]:{PORT}")
        print("=" * 50)
        print("📂 服务目录:", DIRECTORY)
        print("📄 首页文件: index.html")
        print("🖼️ 图片目录: uploads/")
        print("=" * 50)
        print("按 Ctrl+C 停止服务器...")
        print()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    main()
