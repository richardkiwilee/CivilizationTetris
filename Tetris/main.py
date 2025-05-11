from Tetris.server import server
from Tetris.client import main
import subprocess
import sys
import argparse
import time
import atexit
import signal
import os


def cleanup_server(process):
    print("主程序退出，准备关闭服务器进程...")
    if process.poll() is None:  # 如果服务器进程还在运行
        process.send_signal(signal.CTRL_BREAK_EVENT)
        try:
            process.wait(timeout=1)  # 等待最多1秒让服务器优雅关闭
        except subprocess.TimeoutExpired:
            print("服务器进程未能正常退出，强制终止")
            process.kill()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', help='action')
    parser.add_argument('-v', '--verbose', action='store_true', default=False)
    parser.add_argument('-s', '--server', type=str, default='localhost')
    parser.add_argument('-p', '--port', type=int, default=50051)
    parser.add_argument('-n', '--name', type=str, default=None)
    parser.add_argument('-d', '--debug', action='store_true', default=False)
    args = parser.parse_args()

    if args.action.lower() == 'service':
        try:
            _ = int(args.port)
        except:
            args.port = 50051
        server(args.port)
    elif args.action.lower() == 'host':
        try:
            _ = int(args.port)
        except:
            args.port = 50051
        
        # 启动服务器进程
        if args.verbose:
            # 调试模式：在新控制台窗口中运行
            server_process = subprocess.Popen(
                [sys.executable, '-mHyperTexas.main', 'service'],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            # 静默模式：隐藏控制台窗口
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            server_process = subprocess.Popen(
                [sys.executable, '-mHyperTexas.main', 'service'],
                startupinfo=startupinfo
            )
        
        # 注册清理函数
        atexit.register(cleanup_server, server_process)
        
        try:
            # 启动客户端
            main('localhost', args.port, args.name)
        except KeyboardInterrupt:
            print("检测到用户中断，正在关闭...")
        finally:
            print("exit...")
            # 确保服务器进程被清理
            if not args.debug:
                cleanup_server(server_process)
                # 取消注册清理函数，因为我们已经手动清理了
            atexit.unregister(cleanup_server)
    
    elif args.action.lower() == 'join':
        if args.debug:
            main('localhost', args.port, args.name)
        else:
            main(args.server, args.port, args.name)
