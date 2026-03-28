# 媒体提问模块 API 使用手册

## 1. 接口概述
- 本接口模拟外交部/科技发布会场景，根据输入的科技事件，自动调度具备特定立场和意图的媒体 Agent 生成针对性提问。

## 2. 基础信息
- **URL**: `http://localhost:8000/simulate/inquiry`
- **Method**: `POST`
- **Content-Type**: `application/json`

## 3. 请求参数
| 参数名 | 类型 | 必选 | 说明 |
| :----- | :--- | :--- | :--- |
| event_text | String | 是 | 科技事件的详细描述 |
| media_count | Integer | 否 | 模拟提问的媒体数量（默认3） |

## 4. 调用示例 (cURL)
```bash
curl -X POST "http://localhost:8000/simulate/inquiry" \
     -H "Content-Type: application/json" \
     -d '{"event_text": "中国宣布在月球南极发现大量水冰矿藏", "media_count": 2}'
```

## 5. 响应示例
```json
{
  "status": "success",
  "data": [
    {
      "media_name": "Reuters",
      "event": "中国宣布在月球南极发现大量水冰矿藏",
      "behavior_tag": "媒体提问",
      "question": "鉴于水冰在太空探索中的战略价值，中方是否计划就资源开采权与国际社会签署新的监管协议？"
    }
  ]
}
```