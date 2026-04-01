# Components 组件库

本目录包含 AgiComm 前端应用的所有可复用 Vue 组件。

## 组件列表

### 1. **Navbar.vue** - 顶部导航栏

- **功能**:
  - 显示后端连接状态（绿色/红色指示器）
  - 后端连接故障时提供重试按钮
  - 深色/浅色主题切换
  - 模型服务监控快速入口
  - GitHub 仓库链接
- **属性**:
  - 无属性（全局可用）

- **事件**:
  - 自动检测后端连接（每 3 分钟检查一次）

- **样式特点**:
  - 粘性顶部定位（`sticky top-0`）
  - 响应式设计（mobile/tablet/desktop）
  - 玻璃态效果（`backdrop-blur`）
  - 深色模式支持

### 2. **Sidebar.vue** - 左侧边栏导航

- **功能**:
  - 主要导航菜单
  - 路由链接到各个仿真模块
  - 移动端折叠菜单
  - 当前事件指示器

- **属性**:
  - 无属性（通过 `inject` 获取 sidebar 状态）

- **路由链接**:
  - `/` - 媒体提问仿真
  - `/news` - 多维报道生成
  - `/social` - 受众传播仿真 (预留)
  - `/model-status` - 模型服务监控

- **样式特点**:
  - 移动端固定侧边栏（可折叠）
  - 桌面端静态侧边栏
  - 分组导航结构

### 3. **AgentCard.vue** - 代理卡片

- **功能**:
  - 显示媒体代理的信息卡片
  - 用于媒体提问结果展示

- **属性**:
  - `agent` (Object) - 代理对象，包含媒体信息和提问内容
  - `isLast` (Boolean) - 是否为最后一个卡片

- **事件**:
  - 无自定义事件

- **样式特点**:
  - 响应式卡片设计
  - 支持展开/折叠效果
  - 深色模式支持

## 使用示例

### 基础导航

所有导航组件均在 `App.vue` 中全局使用，无需单独导入。

### router-link 集成

组件通过 Vue Router 的 `router-link` 实现路由导航：

```vue
<router-link to="/model-status" class="...">
  🔧 模型监控
</router-link>
```

## 设计原则

1. **响应式设计**: 所有组件支持 mobile/tablet/desktop 三层响应
2. **深色模式**: 使用 Tailwind CSS 的 `dark:` 前缀支持深色主题
3. **可访问性**: 包含 `aria-label` 等无障碍属性
4. **性能**: 使用 Vue 3 `Composition API` 优化性能
5. **一致性**: 统一使用 Tailwind CSS + Slate 色系

## 修改指南

### 修改导航链接

编辑 `Sidebar.vue` 中的 `router-link` 组件：

```vue
<router-link to="/new-path" class="..." @click="onNav">
  <span>🎯</span>
  <span>新导航项</span>
</router-link>
```

### 修改后端连接检查

编辑 `Navbar.vue` 中的 `checkBackendConnection` 方法：

```javascript
const API_HEALTH = `${API_BASE}/health`; // 修改检查端点
```

### 修改主题颜色

编辑 `Tailwind.config.js` 中的颜色配置，所有组件会自动使用新主题。

## 内部状态管理

### provide/inject 系统

- `Sidebar` 通过 `provide` 向下提供 `sidebar` 对象
- 包含 `toggle()`, `open()`, `close()` 方法
- 实现移动端菜单的打开/关闭

### 响应式状态

组件使用 Vue 3 `ref()` 管理本地状态：

- `backendConnected` - 后端连接状态
- `isDark` - 深色模式开关
- `sidebarOpen` - 侧边栏打开状态

## 常见问题

### Q: 如何添加新的导航菜单项?

A: 在 `Sidebar.vue` 中添加 `router-link`，并在 `router.js` 中注册对应的路由。

### Q: 如何修改导航栏样式?

A: 编辑 `Navbar.vue` 或 `Sidebar.vue` 中的 `class` 属性（使用 Tailwind CSS 类名）。

### Q: 为什么侧边栏在移动端显示/隐藏?

A: 使用 CSS 的 `md:` 断点（768px）进行响应式控制。

## 文件大小统计

| 组件          | 行数 | 大小    |
| ------------- | ---- | ------- |
| Navbar.vue    | ~100 | ~3 KB   |
| Sidebar.vue   | ~80  | ~2.5 KB |
| AgentCard.vue | ~60  | ~1.5 KB |

## 更新历史

- **v1.0** (2026-04-01): 初始版本，添加 ModelStatusView 导航入口

---

**最后更新**: 2026年4月1日
