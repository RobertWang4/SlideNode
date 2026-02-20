import requests
import json

# 不走系统代理，避免 ProxyError
session = requests.Session()
session.trust_env = False

MINIMAX_BASE_URL = "https://api.minimaxi.com/v1"
MINIMAX_API_KEY = "sk-cp-lpWumc2Nk2-qnvlJwF6ZH_ReHtESDN5EqzdrDTwWFE41vXtkyPLdkl9U6eMLGuLQC6oeUWO-QD64kH4PMhJRS25WUbd_1EiGfgnlwC_XukzUVUIqmE2LIpE"
MINIMAX_MODEL = "MiniMax-M2.5"

headers = {
    "Authorization": f"Bearer {MINIMAX_API_KEY}",
    "Content-Type": "application/json",
}

# First API call
response = session.post(
    url=f"{MINIMAX_BASE_URL}/chat/completions",
    headers=headers,
    data=json.dumps({
        "model": MINIMAX_MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "How many r's are in the word 'strawberry'?"},
        ],
    }),
)

resp1 = response.json()
print("--- 第 1 轮回复 ---")
if "error" in resp1:
    print("错误:", resp1["error"])
else:
    msg1 = resp1["choices"][0]["message"]
    print(msg1.get("content", ""))
    print()

    # Second API call - multi-turn conversation
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "How many r's are in the word 'strawberry'?"},
        {"role": "assistant", "content": msg1.get("content", "")},
        {"role": "user", "content": "Are you sure? Think carefully."},
    ]

    response2 = session.post(
        url=f"{MINIMAX_BASE_URL}/chat/completions",
        headers=headers,
        data=json.dumps({
            "model": MINIMAX_MODEL,
            "messages": messages,
        }),
    )

    if response2.ok:
        resp2 = response2.json()
        msg2 = resp2["choices"][0]["message"]
        print("--- 第 2 轮回复 ---")
        print(msg2.get("content", ""))
    else:
        print("--- 第 2 轮请求失败 ---", response2.status_code, response2.text)
