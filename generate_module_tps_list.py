#!/usr/bin/env python3
import os
import sys
import subprocess
import json
from pathlib import Path


def main():
    # 检查命令行参数
    if len(sys.argv) != 3:
        print("用法: python generate_module_tps_list.py <输入文件路径> <基础目录路径>")
        sys.exit(1)
    
    # 从命令行参数获取输入文件路径和基础目录路径
    input_file = sys.argv[1]
    base_dir = sys.argv[2]
    
    # 获取当前脚本目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 创建输出目录
    output_dir = os.path.join(script_dir, 'module_tps')
    os.makedirs(output_dir, exist_ok=True)
    
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
            else:
                # 如果路径不是基于预期的基础目录，则使用完整路径的一部分
                relative_path = module_path.replace('/', '_').replace('\\', '_').replace(':', '_')
            
            # 特殊处理根目录
            if relative_path == '.':
                output_filename = 'root.json'
            else:
                # 替换路径中的-为_，然后用-连接路径组件
                safe_relative_path = relative_path.replace('-', '_').replace(os.sep, '-')
                output_filename = f"{safe_relative_path}.json"
            
            output_path = os.path.join(output_dir, output_filename)
            
            # 保存原始工作目录
            original_dir = os.getcwd()
            
            try:
                # 切换到子模块目录
                os.chdir(module_path)
                
                # 执行 pnpm ls 命令，使用--json参数
                cmd = ['pnpm', 'ls', '--json', '--depth', '0']
                print(f'Executing command in {module_path}:')
                print(' '.join(cmd))
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                # 直接保存原始JSON输出，不做任何处理
                with open(output_path, 'w', encoding='utf-8') as f:
                    # 如果输出不为空，确保是有效的JSON格式
                    if result.stdout.strip():
                        f.write(result.stdout)
                    else:
                        # 如果没有输出，写入空对象
                        f.write('{}')
                
                print(f'Successfully saved raw pnpm output to {output_filename}')
                
                # 如果有错误输出，保存到单独的文件
                if result.stderr:
                    error_file = output_path.replace('.json', '.error.txt')
                    with open(error_file, 'w', encoding='utf-8') as ef:
                        ef.write(result.stderr)
                    print(f'Saved stderr to {error_file}')
                
            except Exception as e:
                print(f'Error processing {module_path}: {e}')
                # 记录错误信息
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(f'Error: {str(e)}')
                continue
            finally:
                # 恢复原始工作目录
                os.chdir(original_dir)
    
    except Exception as e:
        print(f'Error reading input file {input_file}: {e}')
        sys.exit(1)
    
    print('All modules processed!')


if __name__ == '__main__':
    main()