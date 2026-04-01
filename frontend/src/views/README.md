# Views 视图层

本目录包含 AgiComm 前端应用的所有页面视图。每个视图对应一个主要功能模块。

## 视图列表

### 1. **InquiryView.vue** - 媒体提问仿真

- **路由**: `/` (默认主页)
- **功能描述**:
  - 输入科技事件描述
  - 选择目标媒体（多选，最多 10 个）
  - 触发媒体提问仿真
  - 展示各媒体的提问内容
  - 流式响应处理

- **核心功能模块**:
  1. **事件输入区**:
     - 大文本框输入事件描述
     - 字符数限制
     - 实时验证

  2. **媒体选择面板**:
     - 搜索框快速查找媒体
     - 多选复选框
     - 选择数量限制提示
     - 清空按钮

  3. **提问生成区**:
     - 提交按钮
     - 加载状态显示
     - 错误提示

  4. **结果展示区**:
     - 媒体卡片列表（使用 AgentCard 组件）
     - 响应式网格布局
     - 支持展开/折叠卡片
     - 错误处理显示

- **API 调用**:
  - 端点: `POST /simulate/inquiry`
  - 请求体:
    ```json
    {
      "event_text": "事件描述",
      "media_ids": ["id1", "id2"] // 可选
    }
    ```
  - 响应格式: NDJSON (newline-delimited JSON)
  - 每行包含一个媒体的提问数据

- **数据加载**:
  - 启动时加载媒体列表（CSV 文件）
  - 渐进式媒体信息加载

- **错误处理**:
  - 无效事件描述提示
  - 媒体选择提示
  - 网络错误处理
  - 后端错误响应处理

- **样式特点**:
  - 两栏布局（左边输入，右边结果）
  - 响应式设计（移动端单栏）
  - 渐变背景
  - 调整的阴影效果

### 2. **NewsView.vue** - 多维报道生成

- **路由**: `/news`
- **功能描述**:
  - 输入科技事件
  - 选择事件日期（可选）
  - 选择媒体（最多 10 个）
  - 生成多维度新闻报道
  - 流式响应处理

- **核心功能模块**:
  1. **事件信息录入**:
     - 事件文本输入
     - 事件日期选择（datetime picker）
     - 媒体选择面板

  2. **报道生成控制**:
     - 生成按钮
     - 进度显示
     - 取消操作（流式响应中）

  3. **报道展示区**:
     - 媒体报道卡片
     - 标题、摘要、完整内容
     - 错误报告特殊处理
     - 响应式网格

  4. **导出功能** (预留):
     - 复制到剪贴板
     - 保存为文本/JSON

- **API 调用**:
  - 端点: `POST /simulate/news`
  - 请求体:
    ```json
    {
      "event_text": "事件描述",
      "event_date": "2026-03-30", // 可选
      "media_ids": ["id1", "id2"] // 可选
    }
    ```
  - 响应格式: NDJSON，每行为一个媒体的报道

- **特殊处理**:
  - 日期格式转换 (YYYY-MM-DD)
  - 报道长内容的折叠展示
  - 错误报告的专门展示样式

- **样式特点**:
  - 与 InquiryView 类似的整体风格
  - 日期选择器集成
  - 响应式报道卡片

### 3. **SocialView.vue** - 受众传播仿真

- **路由**: `/social`
- **功能描述**:
  - 受众媒介接触行为仿真
  - 社交网络传播模拟
  - 多维传播路径分析

- **状态**: 预留接口，功能开发中

- **实现计划**:
  - 事件输入
  - 受众分群配置
  - 传播渠道选择
  - 传播动力参数设置
  - 实时仿真展示

### 4. **ModelStatusView.vue** - 模型服务监控 (新增)

- **路由**: `/model-status`
- **功能描述**:
  - 实时检查 LLM 模型服务状态
  - 显示在线模型列表
  - 错误日志展示
  - 手动检查和自动检查

- **核心功能模块**:
  1. **状态摘要卡片** (左侧):
     - 总体健康状态指示
     - 在线模型数量
     - 最后检查时间
     - 手动检查按钮

  2. **活跃模型列表** (右上):
     - 在线模型名称显示
     - 绿灯指示器
     - 支持多列响应式布局

  3. **错误日志** (右下):
     - 离线/错误的模型
     - 详细错误信息
     - 可滚动列表

  4. **信息提示**:
     - 模型服务说明
     - 自动切换机制说明
     - 实时检查间隔说明

- **API 调用**:
  - 端点: `GET /llm/status`
  - 响应体:
    ```json
    {
      "data": {
        "summary": {
          "title": "AgiComm 模型服务监控",
          "status_icon": "✅ 运行中",
          "health_rate": "2/3",
          "last_check": "刚刚"
        },
        "active_pool": {
          "count": 2,
          "models": ["zhipu", "deepseek"]
        },
        "error_log": [{ "model": "openai", "reason": "API密钥无效" }]
      }
    }
    ```

- **自动刷新**:
  - 页面加载时自动检查
  - 支持手动检查按钮
  - 显示最后检查时间

- **错误处理**:
  - 网络错误捕获
  - 超时处理（8 秒）
  - 友好的错误提示

- **样式特点**:
  - 三列布局（左侧状态摘要，右侧两个卡片）
  - 响应式设计
  - 绿色/红色状态指示
  - 动画加载状态

## 数据流向

```
User Input
    ↓
View Component (ValidationCheck)
    ↓
API Call (fetch)
    ↓
Backend Processing (NDJSON Stream)
    ↓
Stream Parser (line-by-line JSON)
    ↓
Result Display (Component State Update)
    ↓
UI Rendering
```

## 流式响应处理

所有视图使用统一的流式响应解析逻辑：

```javascript
// NDJSON 格式解析
const reader = response.body.getReader();
const decoder = new TextDecoder();
let buffer = "";

while (true) {
  const { done, value } = await reader.read();
  if (done) break;

  buffer += decoder.decode(value, { stream: true });
  const lines = buffer.split("\n");
  buffer = lines.pop(); // 保留不完整的行

  for (const line of lines) {
    if (line.trim()) {
      const data = JSON.parse(line);
      // 处理数据
    }
  }
}
```

## 错误处理策略

1. **验证错误**: 用户输入验证失败时本地提示
2. **网络错误**: 连接失败时显示重试按钮
3. **后端错误**: 流中包含 `has_error` 字段时显示错误信息
4. **超时处理**: 8 秒超时自动中断

## 常见问题

### Q: 如何添加新的视图?

A:

1. 创建 `NewView.vue` 文件
2. 在 `router.js` 中添加路由
3. 在 `Sidebar.vue` 中添加导航链接

### Q: 如何修改 API 端点?

A: 编辑各视图中的 `API_BASE` 或直接修改 `fetch()` 调用的 URL。

### Q: 为什么流式响应显示"无结果"?

A: 检查：

1. 后端是否返回了数据
2. 前端是否正确解析了 NDJSON 格式
3. 媒体是否有效参与

### Q: 如何调试流式响应?

A:

1. 打开浏览器开发者工具 (F12)
2. 在 Network 标签查看响应
3. 在 Console 中查看 JavaScript 日志

## 文件大小统计

| 视图                | 行数 | 大小   | 功能完成度 |
| ------------------- | ---- | ------ | ---------- |
| InquiryView.vue     | 800+ | ~25 KB | 100% ✅    |
| NewsView.vue        | 850+ | ~26 KB | 100% ✅    |
| SocialView.vue      | 150+ | ~4 KB  | 20% 🔶     |
| ModelStatusView.vue | 350+ | ~11 KB | 100% ✅    |

## 更新历史

- **v1.0** (2026-03-30): 初始版本
  - InquiryView 完成
  - NewsView 完成
  - SocialView 占位符

- **v1.1** (2026-03-31): 参与决策逻辑
  - InquiryView 添加 is_participating 字段支持
  - NDJSON 流式响应优化

- **v1.2** (2026-04-01): 模型监控功能
  - 新增 ModelStatusView
  - 支持 LLM 模型实时监控
  - 导航栏/侧边栏集成

---

**最后更新**: 2026年4月1日
