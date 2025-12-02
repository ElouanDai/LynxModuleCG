#!/usr/bin/env python3
import os
import sys
import subprocess
import json
from pathlib import Path
import argparse


def main():
    parser = argparse.ArgumentParser(description='Generate module call graph')
    parser.add_argument('target_dir', help='Target directory to scan')
    parser.add_argument('jelly_path', help='Jelly executable path')
    args = parser.parse_args()
    
    target_dir = args.target_dir

    # 获取当前脚本目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 从输入路径中提取项目名
    project_name = os.path.basename(os.path.normpath(target_dir))
    
    # 创建输出目录
    output_dir = os.path.join(script_dir, f'cg_{project_name}')
    os.makedirs(output_dir, exist_ok=True)

    # TTMLResolver可执行文件路径从命令行参数获取
    jelly_path = args.jelly_path

    # 递归扫描目标目录
    print(f'Scanning directory: {target_dir}')

    for root, dirs, files in os.walk(target_dir):
        # 检查当前目录是否包含package.json
        if 'package.json' in files:
            # 构建相对路径作为输出文件名
            relative_path = os.path.relpath(root, target_dir)
            
            # 特殊处理根目录
            if relative_path == '.':
                output_filename = 'root.json'
            else:
                # 替换路径中的-为_，然后用-连接路径组件
                safe_relative_path = relative_path.replace('-', '_').replace(os.sep, '-')
                output_filename = f"{safe_relative_path}.json"
            
            output_path = os.path.join(output_dir, output_filename)

            # 构建命令
            cmd = [
                jelly_path,
                '-j', output_path,
                '--api-usage',
                '-b', root,
                root
            ]

            print(f'Executing command for {relative_path}:')
            print(' '.join(cmd))

            # 执行命令
            try:
                result = subprocess.run(cmd, check=True, capture_output=True, text=True)
                print(f'Successfully generated {output_filename}')
            except subprocess.CalledProcessError as e:
                print(f'Error generating {output_filename}: {e}')
                print(f'Stderr: {e.stderr}')

if __name__ == '__main__':
    main()