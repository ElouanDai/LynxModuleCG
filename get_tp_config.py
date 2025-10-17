#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
读取指定文件中的所有路径，为每个路径收集对应的package.json文件并保存到指定目录
"""
import os
import sys
import json


def main():
    # 检查命令行参数
    if len(sys.argv) != 4:
        print("用法: python get_tp_config.py <输入文件路径> <工作区根目录> <输出目录>")
        sys.exit(1)
    
    # 从命令行参数获取
    input_file = sys.argv[1]
    workspace_root = sys.argv[2]
    output_dir = sys.argv[3]
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"错误：无法找到输入文件 {input_file}")
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
            # 检查package.json是否存在
            package_json_path = os.path.join(path, 'package.json')
            if not os.path.exists(package_json_path):
                print(f'警告：路径中没有package.json文件，跳过: {path}')
                continue
            
            # 构建相对路径作为输出文件名（相对于工作区根目录）
            relative_path = os.path.relpath(path, workspace_root)
            
            # 特殊处理根目录
            if relative_path == '.':
                output_filename = 'root.json'
            else:
                # 替换路径中的-为_，然后用-连接路径组件
                safe_relative_path = relative_path.replace('-', '_').replace(os.sep, '-')
                output_filename = f"{safe_relative_path}.json"
            
            output_path = os.path.join(output_dir, output_filename)

            print(f'  正在读取package.json: {output_filename}')

            # 读取package.json内容
            try:
                with open(package_json_path, 'r', encoding='utf-8') as pkg_file:
                    package_data = json.load(pkg_file)
                
                # 保存到输出文件
                with open(output_path, 'w', encoding='utf-8') as out_file:
                    json.dump(package_data, out_file, ensure_ascii=False, indent=2)
                
                print(f'  成功保存 {output_filename}')
            except json.JSONDecodeError as e:
                print(f'  解析package.json失败 {output_filename}: {e}')
            except Exception as e:
                print(f'  读取或保存文件失败 {output_filename}: {e}')
        except Exception as e:
            print(f'  处理路径时发生未知错误: {e}')

if __name__ == '__main__':
    main()