#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
读取指定文件中的所有路径，为每个路径生成对应的JSON文件并保存到tp_funcs目录
"""
import os
import sys
import subprocess
import json
from pathlib import Path


def main():
    # 检查命令行参数
    if len(sys.argv) != 4:
        print("用法: python generate_tp_func_list.py <输入文件路径> <工作区根目录> <jelly_mod_main_path>")
        sys.exit(1)
    
    # 从命令行参数获取
    input_file = sys.argv[1]
    workspace_root = sys.argv[2]
    jelly_mod_main = sys.argv[3]
    
    # 获取当前脚本目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 创建输出目录
    output_dir = os.path.join(script_dir, 'tp_funcs')
    os.makedirs(output_dir, exist_ok=True)

    # 设置node命令
    node_cmd = 'node'

    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"错误：无法找到输入文件 {input_file}")
        sys.exit(1)
    
    # 检查Jelly-Mod main.js是否存在
    if not os.path.exists(jelly_mod_main):
        print(f"错误：无法找到Jelly-Mod main.js文件 {jelly_mod_main}")
        sys.exit(1)
    
    # 读取输入文件中的所有路径
    with open(input_file, 'r', encoding='utf-8') as f:
        paths = [line.strip() for line in f if line.strip()]
    
    print(f'总共读取到 {len(paths)} 个路径')
    
    # 遍历每个路径
    for index, path in enumerate(paths, 1):
        print(f'处理路径 {index}/{len(paths)}: {path}')
        # 检查路径是否存在
        if not os.path.exists(path):
            print(f'警告：路径不存在，跳过: {path}')
            continue
        
        try:
            # 构建相对路径作为输出文件名（相对于工作区根目录）
            # 提取仓库名称（从workspace_root路径中）
            repo_name = os.path.basename(workspace_root).replace('-', '_')
            
            relative_path = os.path.relpath(path, workspace_root)
            
            # 生成从仓库名称开始的路径格式
            if relative_path == '.':
                # 根目录情况
                output_filename = f"{repo_name}.json"
            else:
                # 替换路径中的特殊字符，确保格式一致
                safe_relative_path = relative_path.replace('-', '_').replace(os.sep, '-')
                output_filename = f"{repo_name}-{safe_relative_path}.json"
            
            output_path = os.path.join(output_dir, output_filename)

            # 构建命令 - 使用node执行Jelly-Mod的main.js
            cmd = [
                node_cmd,
                jelly_mod_main,
                '-j', output_path,
                '--api-usage',
                '-b', path,
                path,
                '--gen-func-list'
            ]

            print(f'  执行命令生成: {output_filename}')

            # 执行命令
            try:
                result = subprocess.run(cmd, check=True, capture_output=True, text=True)
                print(f'  成功生成 {output_filename}')
            except subprocess.CalledProcessError as e:
                print(f'  生成失败 {output_filename}: {e}')
                print(f'  错误输出: {e.stderr}')
        except Exception as e:
            print(f'  处理路径时发生未知错误: {e}')

if __name__ == '__main__':
    main()