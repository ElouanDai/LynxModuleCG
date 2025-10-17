#!/usr/bin/env python3
import os
import sys
import subprocess
import json
from pathlib import Path


def main():
    # 检查命令行参数
    if len(sys.argv) != 5:
        print("用法: python generate_cg.py <输入文件路径> <基础目录路径> <输出目录> <jelly_mod_main_path>")
        sys.exit(1)
    
    # 从命令行参数获取
    input_file = sys.argv[1]
    base_dir = sys.argv[2]
    output_dir = sys.argv[3]
    jelly_mod_dir = sys.argv[4]
    
    # 获取当前脚本目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 设置node命令和Jelly-Mod的main.js路径
    node_cmd = 'node'
    jelly_mod_main = os.path.join(script_dir, jelly_mod_dir)
    
    # 获取已存在的输出文件名列表
    existing_files = set()
    if os.path.exists(output_dir):
        for filename in os.listdir(output_dir):
            if filename.endswith('.json'):
                existing_files.add(filename)

    # 读取输入文件中的所有子模块路径
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            module_paths = [line.strip() for line in f if line.strip()]
            
        print(f'Found {len(module_paths)} module paths to process')
        
        # 处理每个子模块路径
        for i, module_path in enumerate(module_paths, 1):
            print(f'Processing module {i}/{len(module_paths)}: {module_path}')
            # 检查路径是否存在
            if not os.path.exists(module_path):
                print(f'Skipping non-existent path: {module_path}')
                continue
            
            # 检查是否为目录
            if not os.path.isdir(module_path):
                print(f'Skipping non-directory path: {module_path}')
                continue
            
            # 构建文件名
            if module_path.startswith(base_dir):
                relative_path = os.path.relpath(module_path, base_dir)
                
                # 从base_dir提取仓库名称（将'-'替换为'_'）
                repo_name = os.path.basename(base_dir).replace('-', '_')
                
                # 特殊处理根目录
                if relative_path == '.':
                    output_filename = f"{repo_name}.json"
                else:
                    # 替换路径中的-为_，然后用-连接路径组件
                    safe_relative_path = relative_path.replace('-', '_').replace(os.sep, '-')
                    output_filename = f"{repo_name}-{safe_relative_path}.json"
            else:
                # 如果路径不是基于预期的基础目录，尝试提取与mono相关的仓库名称
                path_parts = module_path.split(os.sep)
                mono_index = -1
                for i, part in enumerate(path_parts):
                    if 'mono' in part:
                        mono_index = i
                        break
                
                if mono_index != -1:
                    # 提取仓库名称部分
                    repo_part = path_parts[mono_index].replace('-', '_')
                    # 提取从仓库开始的路径部分
                    repo_relative_path = os.sep.join(path_parts[mono_index+1:])
                    if repo_relative_path:
                        safe_relative_path = repo_relative_path.replace('-', '_').replace(os.sep, '-')
                        output_filename = f"{repo_part}-{safe_relative_path}.json"
                    else:
                        output_filename = f"{repo_part}.json"
                else:
                    # 如果无法识别mono相关路径，使用简化的路径处理
                    simplified_path = module_path.replace(os.sep, '-').replace(':', '-')[-100:]  # 截取合理长度
                    output_filename = f"unknown-{simplified_path.replace('-', '_')}.json"
            
            output_path = os.path.join(output_dir, output_filename)
            
            # 确定要显示的相对路径信息
            if module_path.startswith(base_dir):
                display_path = relative_path
            else:
                # 对于非base_dir路径，使用简化的显示信息
                if mono_index != -1:
                    if repo_relative_path:
                        display_path = f"{repo_part}/{repo_relative_path}"
                    else:
                        display_path = repo_part
                else:
                    display_path = os.path.basename(module_path)
            
            # 构建命令 - 使用node执行Jelly-Mod的main.js
            cmd = [
                node_cmd,
                jelly_mod_main,
                '-j', output_path,
                '--api-usage',
                '-b', module_path,
                module_path
            ]

            print(f'Executing command for {display_path}:')
            print(' '.join(cmd))

            # 执行命令
            try:
                result = subprocess.run(cmd, check=True, capture_output=True, text=True)
                print(f'Successfully generated {output_filename}')
            except subprocess.CalledProcessError as e:
                print(f'Error generating {output_filename}: {e}')
                print(f'Stderr: {e.stderr}')
                
    except Exception as e:
        print(f'Error reading input file {input_file}: {e}')
        sys.exit(1)
    
    print('All modules processed!')


if __name__ == '__main__':
    main()