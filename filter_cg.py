#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import json
import requests
import time
import sys

# 模型配置信息（保留原有配置）
API_KEY = "b206585b-562f-429e-bded-a3fbdca15282"
MODEL_NAME = "ep-20250220212055-wtns2"
BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"

# 全局知识库内容
def load_knowledge_base(knowledge_base_path):
    try:
        with open(knowledge_base_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"知识库文件未找到: {knowledge_base_path}")
        return ""
    except Exception as e:
        print(f"读取知识库文件出错: {e}")
        return ""

def call_llm(prompt):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    for attempt in range(3):  # Retry up to 3 times
        try:
            response = requests.post(
                f"{BASE_URL}/chat/completions",
                headers=headers,
                data=json.dumps(payload),
                timeout=60  # Add a timeout
            )
            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"]
                else:
                    print("未获取到模型回复")
                    print("完整响应:", result)
                    return None
            else:
                print(f"请求失败，状态码: {response.status_code}")
                print(f"错误信息: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"发生网络异常: {e}")
        
        time.sleep(2 ** attempt)  # Exponential backoff

    return None

def construct_prompt(api_call, import_type, matched_functions, knowledge_base, config_content=None):
    prompt = f"""
    你是一个智能代码分析助手。
    基于以下知识库，对JavaScript模块的函数调用进行精准筛选。

    {knowledge_base}

    **任务：**
    分析以下API调用和候选函数列表，选择最匹配的函数。

    **API调用：**
    `{api_call}`

    **引入方式类型：**
    `{import_type}`

    **平台环境：**
    Lynx

    **候选函数列表：**
    ```json
    {json.dumps(matched_functions, indent=2)}
    ```
    """
    if config_content:
        prompt += f"""
    **被调用的三方库的package.json文件：**
    这是被调用的第三方库的package.json文件内容，用于辅助分析模块解析规则。
    ```json
    {config_content}
    ```
    """
    prompt += """
    **要求：**
    1.  仔细阅读知识库，特别是关于 `exports`, `import`, `require` 和不同构建目标的规则。
    2.  根据API调用的上下文和候选函数的路径，确定最合适的函数。
    3.  你的回答应该只包含最有可能的函数签名（一个或多个），直接输出函数签名字符串，不要包含任何其他解释或标记。
    4.  函数签名本身不应该包含引号（单引号或双引号），请直接输出原始函数签名。
    5.  如果你认为有多个函数符合要求，你只需要输出多个函数签名，每个函数签名占一行，但坚决不允许输出其他解释也不允许输出分析过程。
    """
    return prompt


def main():
    # 检查命令行参数
    if len(sys.argv) != 5:
        print("用法: python filter_cg.py <输入目录> <输出目录> <工作区根目录> <tp_config_dir>")
        sys.exit(1)
    
    # 从命令行参数获取
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    workspace_root = sys.argv[3]
    tp_config_dir = sys.argv[4]
    
    # 获取当前脚本目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 加载知识库
    kb_path = os.path.join(script_dir, 'knowledge_base.md')
    knowledge_base = load_knowledge_base(kb_path)

    # 创建输出目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 获取并排序所有JSON文件
    all_files = [f for f in os.listdir(input_dir) if f.endswith('.json')]
    all_files.sort()  # 按照字典序排序
    total_files = len(all_files)
    processed_files = 0

    print(f"开始处理文件，共 {total_files} 个文件需要处理")

    for filename in all_files:
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)

        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if 'apiUsage' in data:
                for _, usages in data['apiUsage'].items():
                    for usage in usages:
                        if 'matched_module' in usage:
                            for module in usage['matched_module']:
                                config_content = None
                                if 'modulePath' in module:
                                    try:
                                        # 根据modulePath生成tp_config文件路径
                                        module_path = module['modulePath']
                                        # 构建相对于工作区根目录的相对路径
                                        relative_path = os.path.relpath(module_path, workspace_root)
                                          
                                        # 特殊处理根目录
                                        if relative_path == '.':
                                            output_filename = 'root.json'
                                        else:
                                            # 替换路径中的-为_，然后用-连接路径组件
                                            safe_relative_path = relative_path.replace('-', '_').replace(os.sep, '-')
                                            output_filename = f"{safe_relative_path}.json"
                                          
                                        # 构建完整的tp_config文件路径
                                        tp_config_path = os.path.join(tp_config_dir, output_filename)
                                          
                                        # 读取tp_config文件内容
                                        if os.path.exists(tp_config_path):
                                            with open(tp_config_path, 'r', encoding='utf-8') as f:
                                                config_content = f.read()
                                        else:
                                            print(f"警告：tp_config文件不存在: {tp_config_path}")
                                    except Exception as e:
                                        print(f"获取tp_config内容失败: {e}")
                                if 'matched_functions' in module:
                                    if len(module['matched_functions']) > 1:
                                        # 将knowledge_base和config_content传递给construct_prompt函数
                                        prompt = construct_prompt(usage['api'], usage['importType'], module['matched_functions'], knowledge_base, config_content)
                                        llm_response = call_llm(prompt)
                                        if llm_response:
                                            # LLM的响应可能包含多个函数，所以我们将其解析为一个列表
                                            filtered_funcs = []
                                            for func in llm_response.split('\n'):
                                                stripped_func = func.strip()
                                                if stripped_func:
                                                    # 去除首尾的引号（如果存在）
                                                    if (stripped_func.startswith('"') and stripped_func.endswith('"')) or \
                                                       (stripped_func.startswith('\'') and stripped_func.endswith('\'')):
                                                        stripped_func = stripped_func[1:-1]
                                                    filtered_funcs.append(stripped_func)
                                            module['filtered_functions'] = filtered_funcs
                                        else:
                                            # 如果LLM调用失败，则保留原始列表
                                            module['filtered_functions'] = module['matched_functions']
                                    else:
                                        module['filtered_functions'] = module['matched_functions']

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            processed_files += 1
            print(f"已处理文件: {filename} ({processed_files}/{total_files})")

        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            print(f"处理文件 {filename} 时出错: {e} ({processed_files}/{total_files})")
        except Exception as e:
            print(f"处理文件 {filename} 时发生未知错误: {e} ({processed_files}/{total_files})")

    print(f"所有文件处理完成，共处理 {processed_files}/{total_files} 个文件")

if __name__ == '__main__':
    main()