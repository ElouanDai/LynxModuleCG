#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强cg目录下文件的apiUsage部分
"""
import os
import sys
import json
import re
from pathlib import Path

# 全局变量设置
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 确保输出目录存在

def load_mono_tp_list(mono_tp_list_path):
    try:
        with open(mono_tp_list_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"错误：加载mono-tp-list.json失败: {e}")
        sys.exit(1)

# 统计结果汇总类
class ResSummary:
    def __init__(self, total_api_calls=0, matched_api_calls_count=0, 
                 matched_apis_with_exactly_one_function=0, api_in_black_list=0, 
                 api_in_hard_list=0, api_of_api_count=0):
        self.total_api_calls = total_api_calls
        self.matched_api_calls_count = matched_api_calls_count
        self.matched_apis_with_exactly_one_function = matched_apis_with_exactly_one_function
        self.api_in_black_list = api_in_black_list
        self.api_in_hard_list = api_in_hard_list
        self.api_of_api_count = api_of_api_count
    
    # 合并两个统计结果
    def merge(self, other):
        self.total_api_calls += other.total_api_calls
        self.matched_api_calls_count += other.matched_api_calls_count
        self.matched_apis_with_exactly_one_function += other.matched_apis_with_exactly_one_function
        self.api_in_black_list += other.api_in_black_list
        self.api_in_hard_list += other.api_in_hard_list
        self.api_of_api_count += other.api_of_api_count
        return self
    
    # 方便打印的字符串表示
    def __str__(self):
        return (
            f"total_api_calls: {self.total_api_calls}, "
            f"matched_api_calls_count: {self.matched_api_calls_count}, "
            f"matched_apis_with_exactly_one_function: {self.matched_apis_with_exactly_one_function}, "
            f"api_in_black_list: {self.api_in_black_list}, "
            f"api_in_hard_list: {self.api_in_hard_list}, "
            f"api_of_api_count: {self.api_of_api_count}"
        )

# 疑似不存在的api - 保持不变
api_black_list = [
    "<@byted-lina/lina-douyin-search-mixins>.linaMixinTrackerNGCard()",
    "<@byted-lina/lina-douyin-search-mixins>.linaMixinTrackerNGComponent()",
    "<@toutiao-infra/bridge>.addEventCenterListener()",
    "<@byted-lynx/testing>.createLynxView()",
    "<fs-extra>.writeFileSync()",
    "<fs-extra>.mkdirSync()",
    "<fs-extra>.writeFileSync()",
]

# 已知难以处理的api - 保持不变
api_hard_list = [
    # 匿名函数
    "<@byted-lina/runtime>.LinaCard()",
    "<@byted-lina/runtime>.LinaComponent()",
    "<@byted-lina/runtime-ng>.LinaCard()",
    "<@byted-lina/runtime-ng>.LinaComponent()",
    "<@byted-lina/runtime-ng>.LinaMixin()",
    "<@byted-lina/utils>.flexibleToFixed()",
    "<@byted-lina/lina-mixin-combine-card>.linaMixinCombineCard()",
    "<fs-extra>.existsSync()",
    "<@byted-lina/utils/dist/douyin/poi-utils>.formatPoiSchema()",
    "<@byted-lina/utils/dist/douyin/poi-utils>.isFromFeed()",
    "<@byted-lina/utils/dist/douyin/poi-utils>.getFeedLogData()",
    "<@byted-lina/utils/dist/douyin/poi-utils>.getMarketingTrackingInfo()",
    "<@byted-lina/utils/dist/douyin/poi-utils>.getNewMarketingTrackingInfo()",
    "<@byted-lina/utils/dist/douyin/poi-utils>.getRankboardList()",
    "<@byted-lina/utils/dist/douyin/poi-utils>.getRankboardList()",
    "<@byted-lina/utils/dist/douyin/poi-utils>.formatSeckillInfo()",
    "<@byted-lina/utils/dist/douyin/poi-utils>.getLifeMarketingTrackingInfo()",
    "<@byted-lina/lina-mixin-entity/dist/esm/utils/index>.setEntityMapCache()",
    "<@byted-lina/utils-ng>.omit()",
    "<@byted-lina/morphling-bridge>.bridge()",
    "<@byted-growth/zlink-sdk-lynx>.activate()",
    "<@byted-growth/zlink-sdk-lynx>.fetchLinkInfo()",
    "<@byted-growth/zlink-sdk-lynx>.clickReport()",
    "<vitest>.vi.fn()",
    "<vitest>.expect()",
    "<vitest>.vi.spyOn()",
    "<vitest>.it()",
    "<vitest>.beforeEach()",
    "<vitest>.afterAll()",
    "<vitest>.describe()",
    "<@byted-lina/lina-mixin-entity>.getEntityMapCache()",
    "<@byted-lina/lina-mixin-entity>.reportError()",
    "<@byted-lina/lina-mixin-entity>.reportInfo()",
    "<@byted-lina/lina-mixin-entity>.getCommonClickParams()",
    "<@byted-lina/lina-mixin-entity>.getBcmInfo()",
    "<@byted-lina/lina-mixin-entity>.getDcmInfo()",
    # 函数别名
    "<@byted-lina/utils/dist/douyin/open-url>.debounceOpenUrl()",
    "<@byted-lina/utils-ng>.rawOpenWithBtm()",
    # 默认导出 所有default方法
]

# 从API调用字符串中提取包名和方法名 - 保持不变
class ApiSignature:
    def __init__(self, package_name, path_name, method_name):
        self.package_name = package_name
        self.path_name = path_name
        self.method_name = method_name
        
    def __repr__(self):
        return f"ApiSignature(package_name='{self.package_name}', path_name='{self.path_name}', method_name='{self.method_name}')"
        
    def __eq__(self, other):
        if not isinstance(other, ApiSignature):
            return False
        return (self.package_name == other.package_name and 
                self.path_name == other.path_name and 
                self.method_name == other.method_name)
        
    def __hash__(self):
        return hash((self.package_name, self.path_name, self.method_name))

# 以下函数保持不变
# extract_package_and_method, find_package_path, generate_tp_func_filename, search_function_signature

def extract_package_and_method(api_call_str):
    # 匹配<包名>.方法链()格式
    pattern = r'<([^>]+)>[.]([^()]+)\(\)'  
    match = re.search(pattern, api_call_str)
    if not match:
        # print(f"警告：API调用格式不正确: {api_call_str}")
        return []
    
    content = match.group(1)
    method_chain = match.group(2)
    
    # 提取最后一个点后面的部分作为方法名
    # 例如：applySDK.init() -> init
    if '.' in method_chain:
        method_name = method_chain.split('.')[-1]
    else:
        method_name = method_chain
    
    signatures = []
    
    # 检查是否包含/字符（表示可能是文件路径）
    if '/' in content:
        # 按照用户要求处理含有多个/的情况
        parts = content.split('/')
        if len(parts) > 1:
            # 情况1：第一段作为包名，其余作为路径名
            package_name_1 = parts[0]
            path_name_1 = '/'.join(parts[1:]) if len(parts) > 1 else ''
            signatures.append(ApiSignature(package_name_1, path_name_1, method_name))
            
            # 情况2：前两段作为包名，其余作为路径名
            if len(parts) > 2:
                package_name_2 = '/'.join(parts[0:2])
                path_name_2 = '/'.join(parts[2:]) if len(parts) > 2 else ''
                signatures.append(ApiSignature(package_name_2, path_name_2, method_name))

    # 普通情况，整个内容作为包名
    signatures.append(ApiSignature(content, "", method_name))
    
    return signatures

# 根据包名查找绝对路径
# 修改为使用传入的workspace_root参数
def find_package_path(package_name, mono_tp_list):
    if package_name not in mono_tp_list:
        # print(f"警告：未找到包{package_name}的路径信息")
        return None
    
    # 返回第一个匹配的路径
    return mono_tp_list[package_name][0]['path']

# 根据绝对路径生成tp_funcs目录下对应的文件名
# 修改为使用传入的workspace_root参数
def generate_tp_func_filename(package_path, workspace_root):
    # 构建相对于工作区根目录的路径
    relative_path = os.path.relpath(package_path, workspace_root)
    
    # 特殊处理根目录
    if relative_path == '.':
        return 'root.json'
    
    # 替换路径中的-为_，然后用-连接路径组件
    safe_relative_path = relative_path.replace('-', '_').replace(os.sep, '-')
    return f"{safe_relative_path}.json"

# 递归搜索函数签名
# 修改为使用传入的workspace_root和tp_funcs_dir参数
def search_function_signature(package_name, path_name, method_name, mono_tp_list, workspace_root, tp_funcs_dir, visited=None):
    if visited is None:
        visited = set()
    
    # 避免循环依赖
    if (package_name, path_name, method_name) in visited:
        return []
    visited.add((package_name, path_name, method_name))
    
    results = []
    
    # 查找包路径
    package_path = find_package_path(package_name, mono_tp_list)
    if not package_path:
        return results
    
    # 生成tp_funcs文件路径
    tp_func_filename = generate_tp_func_filename(package_path, workspace_root)
    tp_func_path = os.path.join(tp_funcs_dir, tp_func_filename)
    
    # 检查文件是否存在
    if not os.path.exists(tp_func_path):
        # print(f"警告：未找到tp_funcs文件: {tp_func_path}")
        return results
    
    try:
        with open(tp_func_path, 'r', encoding='utf-8') as f:
            tp_func_data = json.load(f)
        
        # 搜索functions部分
        if 'functions' in tp_func_data:
            for func in tp_func_data['functions']:
                # 使用正则表达式确保方法名是一个完整的标识符或符合命名规范的部分
                # 匹配条件：方法名前不是字母、数字或下划线 且 方法名结尾
                # 这可以确保我们不会匹配到包含方法名作为子串的其他函数
                pattern = r'(^|[^a-zA-Z0-9_]){method_name}$'.format(method_name=re.escape(method_name))
                if re.search(pattern, func):
                    results.append({
                        'function_signature': func,
                        'module_path': package_path,
                        'module_name': package_name
                    })
        
        # 搜索reexports部分
        if 'reexports' in tp_func_data:
            for export_package, exports in tp_func_data['reexports'].items():
                for export in exports:
                    if export == method_name or export == "*":
                        # 递归搜索导出的包
                        nested_results = search_function_signature(
                            export_package, "", method_name, mono_tp_list, workspace_root, tp_funcs_dir, visited.copy()
                        )
                        results.extend(nested_results)
        
    except Exception as e:
        print(f"错误：处理tp_funcs文件{tp_func_path}失败: {e}")
    
    return results

# 增强单个文件
# 修改为使用传入的参数
def enhance_file(file_path, output_dir, mono_tp_list, workspace_root, tp_funcs_dir):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 创建输出数据的副本
        enhanced_data = data.copy()
        
        # 检查是否有apiUsage部分
        if 'apiUsage' not in data:
            # print(f"警告：文件{file_path}没有apiUsage部分，跳过处理")
            return ResSummary()
        
        enhanced_api_usage = {}
        
        # 使用ResSummary类管理统计变量
        res_summary = ResSummary()
        
        # 处理每个apiUsage条目
        for file_key, api_calls in data['apiUsage'].items():
            enhanced_api_calls = []
            
            for api_call_obj in api_calls:
                res_summary.total_api_calls += 1
                
                # 已经是增强格式，保持不变 (兼容旧逻辑)
                if 'matched_module' in api_call_obj:
                    enhanced_api_calls.append(api_call_obj)
                    if api_call_obj['matched_module']:
                        res_summary.matched_api_calls_count += 1
                    continue

                api_call_str = api_call_obj.get('api')
                import_type = api_call_obj.get('importType')

                if not api_call_str:
                    enhanced_api_calls.append(api_call_obj)
                    continue

                if api_call_str in api_black_list:
                    res_summary.api_in_black_list += 1
                    continue
                
                if api_call_str in api_hard_list or api_call_str.endswith(".default()"):
                    res_summary.api_in_hard_list += 1
                    continue

                if "…" in api_call_str:
                    res_summary.api_of_api_count += 1
                    continue
                
                # 提取包名和方法名
                api_signatures = extract_package_and_method(api_call_str)
                if not api_signatures:
                    # 保持原始格式
                    enhanced_api_calls.append(api_call_obj)
                    continue
                
                all_matched_functions = []
                # 对每个可能的apiSignature尝试匹配
                for signature in api_signatures:
                    # 搜索函数签名，传递workspace_root和tp_funcs_dir参数
                    matched_functions = search_function_signature(
                        signature.package_name, 
                        signature.path_name, 
                        signature.method_name, 
                        mono_tp_list,
                        workspace_root,
                        tp_funcs_dir
                    )
                    all_matched_functions.extend(matched_functions)
                
                # 去重
                unique_matched_functions = []
                seen = set()
                for func in all_matched_functions:
                    func_key = (func['module_name'], func['module_path'], func['function_signature'])
                    if func_key not in seen:
                        seen.add(func_key)
                        unique_matched_functions.append(func)
                
                # 更新匹配统计
                if unique_matched_functions:
                    res_summary.matched_api_calls_count += 1
                    # 如果恰好找到一个匹配函数，则增加计数
                    if len(unique_matched_functions) == 1:
                        res_summary.matched_apis_with_exactly_one_function += 1
                else:
                    print(f"未找到匹配的函数签名: {api_call_str}")
                
                # 构建增强后的API调用信息
                enhanced_api_call = {
                    'api': api_call_str,
                    'importType': import_type,
                    'matched_module': []
                }
                
                # 收集匹配的模块和函数
                module_functions_map = {}
                for match in unique_matched_functions:
                    module_key = (match['module_name'], match['module_path'])
                    if module_key not in module_functions_map:
                        module_functions_map[module_key] = []
                    module_functions_map[module_key].append(match['function_signature'])
                
                # 构建matched_module列表
                for (module_name, module_path), functions in module_functions_map.items():
                    enhanced_api_call['matched_module'].append({
                        'moduleName': module_name,
                        'modulePath': module_path,
                        'matched_functions': functions
                    })
                
                enhanced_api_calls.append(enhanced_api_call)
            
            enhanced_api_usage[file_key] = enhanced_api_calls
        
        enhanced_data['apiUsage'] = enhanced_api_usage
        
        # 生成输出文件名和路径
        filename = os.path.basename(file_path)
        output_path = os.path.join(output_dir, filename)
        
        # 保存增强后的文件
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(enhanced_data, f, ensure_ascii=False, indent=2)
        
        print(f"成功增强文件: {file_path} -> {output_path}")
        
        return res_summary
        
    except Exception as e:
            print(f"错误：处理文件{file_path}失败: {e}")
            return ResSummary()

# 主函数
# 修改为接受命令行参数
def main():
    # 检查命令行参数
    if len(sys.argv) != 6:
        print("用法: python enhance_cg.py <输入目录> <输出目录> <工作区根目录> <mono_tp_list_path> <tp_funcs_dir>")
        sys.exit(1)
    
    # 从命令行参数获取
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    workspace_root = sys.argv[3]
    mono_tp_list_path = sys.argv[4]
    tp_funcs_dir = sys.argv[5]
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 加载mono-tp-list.json
    mono_tp_list = load_mono_tp_list(mono_tp_list_path)
    
    # 获取输入目录下的所有JSON文件
    json_files = [f for f in os.listdir(input_dir) if f.endswith('.json')]
    total_files = len(json_files)
    print(f"找到{total_files}个JSON文件需要处理")
    
    # 使用ResSummary类管理全局统计变量
    overall_summary = ResSummary()
    
    # 处理每个文件
    for index, filename in enumerate(json_files, 1):
        file_path = os.path.join(input_dir, filename)
        print(f"处理文件 {index}/{total_files}: {filename}")
        
        # 获取当前文件的统计信息，传递所有必要的参数
        file_summary = enhance_file(file_path, output_dir, mono_tp_list, workspace_root, tp_funcs_dir)
        
        # 更新全局统计
        overall_summary.merge(file_summary)
    
    # 输出统计结果
    print("\n===== 统计结果 =====")
    print(f"所有apiUsage的总数: {overall_summary.total_api_calls}")
    print(f"找到匹配函数的API调用个数: {overall_summary.matched_api_calls_count}")
    print(f"找到恰好一个匹配函数的API调用个数: {overall_summary.matched_apis_with_exactly_one_function}")
    print(f"在黑名单中的API调用个数: {overall_summary.api_in_black_list}")
    print(f"在难以处理列表中的API调用个数: {overall_summary.api_in_hard_list}")
    print(f"api of api的API调用个数: {overall_summary.api_of_api_count}")
    print("==================")
    
    print("所有文件处理完成")

if __name__ == '__main__':
    main()