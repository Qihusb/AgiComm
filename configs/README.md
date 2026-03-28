## 配置文件说明

### `media_schema.json`
- 定义媒体画像数据的字段结构与映射规则，供数据处理脚本读取。
- 主要用于约束和扩展媒体静态属性/行为属性的字段组织方式。

### `llm_settings.py`
- 定义大语言模型调用配置（如 `api_key`、`base_url`、`model_name`、`temperature`、`max_tokens`）。
- 供需要调用模型的模块统一读取，便于在本地实验时集中调整参数。
