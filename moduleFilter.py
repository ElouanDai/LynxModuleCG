#!/usr/bin/env python3
import sys
import os

def filter_module_list(input_file_path, output_file_path):
    """
    过滤文本文件中包含node_modules的行，并将结果按字典序排序后输出到新文件
    
    参数:
        input_file_path: 输入文本文件路径
        output_file_path: 输出文本文件路径
    """
    try:
        # 检查输入文件是否存在
        if not os.path.exists(input_file_path):
            print(f"错误: 输入文件 '{input_file_path}' 不存在")
            return
        
        # 读取输入文件并过滤内容
        filtered_lines = []
        with open(input_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and "node_modules" not in line:
                    filtered_lines.append(line)
        
        # 按字典序排序
        filtered_lines.sort()
        
        # 写入输出文件
        with open(output_file_path, 'w', encoding='utf-8') as f:
            for line in filtered_lines:
                f.write(line + '\n')
        
        print(f"过滤完成！共保留 {len(filtered_lines)} 行，已按字典序排序并输出到 {output_file_path}")
        
    except Exception as e:
        print(f"处理过程中发生错误: {e}")

if __name__ == "__main__":
    # 检查命令行参数
    if len(sys.argv) != 3:
        print("用法: python moduleFilter.py <输入文件路径> <输出文件路径>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    filter_module_list(input_file, output_file)