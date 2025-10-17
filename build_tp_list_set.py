#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统计module_tps目录下所有json文件中的依赖信息，统一收集dependencies、devDependencies、unsavedDependencies
以依赖名为key，收集同一个依赖名的不同版本和路径，去重后输出到指定文件
"""
import os
import glob
import json
import sys

def build_tp_list(module_tps_dir, output_json_file, output_txt_file):
    """
    统计module_tps目录下所有json文件中的依赖信息，生成特定格式的JSON输出和包含去重path的TXT文件
    """
    # 创建依赖字典，用于存储所有依赖信息
    # key: 依赖名
    # value: 包含该依赖不同版本和路径的数组
    dependencies_dict = {}
    
    # 创建集合用于存储去重后的path值
    unique_paths = set()
    
    # 获取module_tps目录下所有json文件
    json_files = glob.glob(os.path.join(module_tps_dir, '*.json'))
    
    print(f'找到 {len(json_files)} 个JSON文件需要处理')
    
    # 遍历所有json文件
    for json_file in json_files:
        try:
            print(f'处理文件: {json_file}')
            with open(json_file, 'r', encoding='utf-8') as f:
                # 读取JSON内容
                content = json.load(f)
                
                # 检查content的类型，处理两种可能的格式：
                # 1. 直接是包含dependencies的对象
                # 2. 是包含对象的数组，每个对象可能包含dependencies
                if isinstance(content, dict):
                    process_dependencies(content, dependencies_dict, unique_paths)
                elif isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict):
                            process_dependencies(item, dependencies_dict, unique_paths)
        except Exception as e:
            print(f"处理文件 {json_file} 时出错: {e}")
    
    # 将结果写入JSON输出文件
    with open(output_json_file, 'w', encoding='utf-8') as f:
        json.dump(dependencies_dict, f, ensure_ascii=False, indent=2)
    
    print(f"已成功将 {len(dependencies_dict)} 个唯一依赖写入到 {output_json_file}")
    
    # 将去重后的path值写入TXT文件
    sorted_paths = sorted(unique_paths)
    with open(output_txt_file, 'w', encoding='utf-8') as f:
        for path in sorted_paths:
            f.write(f"{path}\n")
    
    print(f"已成功将 {len(unique_paths)} 个去重后的路径写入到 {output_txt_file}")


def process_dependencies(data, dependencies_dict, unique_paths):
    """
    处理数据中的依赖信息，将依赖添加到dependencies_dict中，同时收集去重的path值
    """
    # 定义需要处理的依赖类型
    dependency_types = ['dependencies', 'devDependencies', 'unsavedDependencies']
    
    # 遍历所有依赖类型
    for dep_type in dependency_types:
        if dep_type in data:
            dependencies = data[dep_type]
            if isinstance(dependencies, dict):
                # 遍历每个依赖
                for dep_name, dep_info in dependencies.items():
                    # 确保dep_info是字典类型
                    if isinstance(dep_info, dict):
                        # 创建依赖对象
                        dep_obj = dep_info.copy()
                        # 确保包含name字段
                        if 'name' not in dep_obj:
                            dep_obj['name'] = dep_name
                        
                        # 收集path值到集合中（自动去重）
                        if 'path' in dep_obj:
                            unique_paths.add(dep_obj['path'])
                        
                        # 如果依赖名不在字典中，创建新的数组
                        if dep_name not in dependencies_dict:
                            dependencies_dict[dep_name] = []
                        
                        # 检查这个依赖对象是否已经存在于数组中（根据from、path和name去重）
                        is_exist = False
                        for existing_dep in dependencies_dict[dep_name]:
                            # 如果from、path和name都相同，则认为是同一个依赖
                            if (('from' in dep_obj and 'from' in existing_dep and dep_obj['from'] == existing_dep['from']) and
                                ('path' in dep_obj and 'path' in existing_dep and dep_obj['path'] == existing_dep['path']) and
                                ('name' in dep_obj and 'name' in existing_dep and dep_obj['name'] == existing_dep['name'])):
                                is_exist = True
                                break
                        
                        # 如果依赖对象不存在，则添加到数组中
                        if not is_exist:
                            dependencies_dict[dep_name].append(dep_obj)


if __name__ == "__main__":
    # 检查命令行参数
    if len(sys.argv) != 4:
        print("用法: python build_tp_list_set.py <module_tps_dir> <output_json_file> <output_txt_file>")
        sys.exit(1)
    
    module_tps_dir = sys.argv[1]
    output_json_file = sys.argv[2]
    output_txt_file = sys.argv[3]
    
    # 如果module_tps_dir是相对路径，相对于脚本所在目录
    if not os.path.isabs(module_tps_dir):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        module_tps_dir = os.path.join(script_dir, module_tps_dir)
    
    build_tp_list(module_tps_dir, output_json_file, output_txt_file)