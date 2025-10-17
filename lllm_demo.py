import requests
import json

# 模型配置信息
API_KEY = "b206585b-562f-429e-bded-a3fbdca15282"
MODEL_NAME = "ep-20250220212055-wtns2"
BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"

# 构建请求头
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

# 构建请求体
payload = {
    "model": MODEL_NAME,
    "messages": [
        {"role": "user", "content": "你好，豆包！请简单介绍一下自己。"}
    ]
}

try:
    # 发送POST请求
    response = requests.post(
        f"{BASE_URL}/chat/completions",
        headers=headers,
        data=json.dumps(payload)
    )
    
    # 检查请求是否成功
    if response.status_code == 200:
        result = response.json()
        # 提取并打印模型回复
        if "choices" in result and len(result["choices"]) > 0:
            print("模型回复:")
            print(result["choices"][0]["message"]["content"])
        else:
            print("未获取到模型回复")
            print("完整响应:", result)
    else:
        print(f"请求失败，状态码: {response.status_code}")
        print("错误信息:", response.text)

except Exception as e:
    print(f"发生异常: {e}")