# AutoGen Magentic-One 多代理协作天气查询系统

基于 Microsoft AutoGen Magentic-One 框架的多代理协作天气查询系统，支持智能 IP 定位和自动化团队协作机制。现已支持三种不同的协作模式：**SelectorGroupChat**、**Swarm**、**Magentic-One**。

## 🌟 项目特色

- 🧠 **意图解析代理** - 分析用户查询意图，提取城市和时间信息
- 🌤️ **天气查询代理** - 调用天气 API 获取数据，支持自动 IP 定位
- ✨ **响应格式化代理** - 格式化输出并提供生活建议
- 🧲 **Magentic-One 协作** - 智能自动化团队协作，无需手动配置协作流程
- 📍 **智能定位** - 用户无需指定城市，自动通过 IP 获取地理位置
- 🎯 **三种协作模式** - 支持 SelectorGroupChat、Swarm、Magentic-One 三种不同的协作机制

## 📁 项目结构

```plain
weather_autogen/
├── src/                        # 核心源代码
│   ├── weather_cli.py          # 通用命令行界面（包含演示功能）
│   ├── selector_groupchat/     # 集中式选择器协作模式
│   │   ├── weather_team.py     # 协作管理器
│   │   └── weather_agents.py   # 代理定义
│   ├── swarm/                  # 去中心化handoff协作模式
│   │   ├── weather_team.py     # 协作管理器
│   │   └── weather_agents.py   # 代理定义
│   └── magentic_one/           # 智能自动化团队协作模式
│       ├── weather_team.py     # 协作管理器
│       └── weather_agents.py   # 代理定义
├── mcp_server/                 # MCP 服务器
│   └── weather_mcp_server.py   # 彩云天气MCP服务器(支持IP定位)
├── tests/                      # 测试套件
│   └── reports/YYYYMMDD/       # 按日期分组的测试报告
├── requirements.txt            # 依赖包
└── README.md                  # 项目文档
```

## 🚀 快速开始

### 1. 进入项目目录

```bash
cd mcp/weather_autogen
```

### 2. 激活虚拟环境（如果还没有）

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
source .venv/bin/activate  # macOS/Linux
# 或 .venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 设置 API 密钥

```bash
# 复制配置模板
cp .env.example .env.local

# 编辑 .env.local 文件，填入API密钥：
# OPENAI_API_KEY=your-openai-api-key
# CAIYUN_API_KEY=your-caiyun-api-key
```

### 5. 运行天气查询系统

```bash
# 推荐：通用CLI（交互式选择协作模式）
python src/weather_cli.py "今天天气怎么样"

# 指定协作模式
python src/weather_cli.py --mode magentic_one "今天天气"
python src/weather_cli.py --mode swarm "今天天气"

# 演示模式
python src/weather_cli.py --demo

# 注意：源代码模块专注业务逻辑，演示功能统一通过 CLI 提供
```

## 🧲 Magentic-One 协作流程

```mermaid
graph LR
    A[用户查询] --> B[MagenticOneOrchestrator]
    B --> C[智能代理选择]
    C --> D[意图解析代理]
    D --> E[天气查询代理] 
    E --> F[响应格式化代理]
    F --> G[用户 - 完成]
```

### 🧲 Magentic-One 协作机制

- **智能自动化** - MagenticOneOrchestrator 自动管理代理协作流程
- **零配置协作** - 无需手动配置 handoffs 或选择器函数
- **智能任务分配** - 根据代理描述和任务需求自动选择合适的代理

### 协作示例

**用户输入**：`"上海明天天气"`

1. 🧲 **MagenticOneOrchestrator**：

   ```plain
   分析任务：需要天气查询
   → 自动选择 intent_parser 开始协作
   ```

2. 🧠 **意图解析代理**：

   ```plain
   解析: 城市=上海, 时间=tomorrow, 查询=明天天气
   → 自动交接给 weather_agent
   ```

3. 🌤️ **天气查询代理**：

   ```plain
   调用 query_weather_tomorrow("上海")
   获取天气数据
   → 自动交接给 formatter
   ```

4. ✨ **响应格式化代理**：

   ```plain
   美化输出 + 添加生活建议
   → 输出"查询完成"，协作结束
   ```

## 🎯 支持的查询类型

| 查询类型 | 示例           | 特殊功能   | Magentic-One 自动协作流程                   |
| -------- | -------------- | ---------- | ------------------------------------------- |
| 今日天气 | "今天天气"     | IP 自动定位 | 自动：intent_parser→weather_agent→formatter |
| 明日天气 | "明天会下雨吗" | IP 自动定位 | 自动：intent_parser→weather_agent→formatter |
| 未来天气 | "未来三天天气" | IP 自动定位 | 自动：intent_parser→weather_agent→formatter |
| 城市指定 | "北京明天天气" | 直接查询   | 自动：intent_parser→weather_agent→formatter |
| 城市指定 | "上海今天天气" | 直接查询   | 自动：intent_parser→weather_agent→formatter |

### 🆕 智能 IP 定位功能

当用户查询**没有明确指定城市**时，系统会：

1. 自动通过 IP 地址获取用户地理位置
2. 智能匹配到支持的中国城市
3. 为非中国地区提供友好提示

## 🛠️ 技术架构 (Magentic-One Mode)

### 核心组件

- **WeatherAgentTeam**: Magentic-One 协作管理器，零配置智能协作
- **意图解析代理**: 分析用户查询意图，专注于任务描述
- **天气查询代理**: 通过 MCP 协议调用天气工具，集成智能定位
- **响应格式化代理**: 格式化输出结果，提供生活建议
- **CLI 演示系统**: 统一的命令行接口，支持交互式演示和模式选择

### Magentic-One 协作机制

```python
# 代理配置示例（无需 handoffs 配置）
intent_parser = AssistantAgent(
    name="intent_parser",
    description="专业的意图解析代理，负责分析用户天气查询意图",
    system_message="...专注于意图解析任务"
)
```

**关键特性:**

- **智能自动化**: MagenticOneOrchestrator 自动管理协作流程
- **零配置**: 无需 handoffs 或选择器函数配置
- **智能调度**: 根据代理描述自动选择和协调代理
- **终止条件**: `MaxMessageTermination(max_messages=10)` | `TextMentionTermination("查询完成")`

### MCP 工具函数

- `query_weather_today(city)` - 查询今天天气
- `query_weather_tomorrow(city)` - 查询明天天气
- `query_weather_future_days(city, days)` - 查询未来几天天气
- `get_user_location_by_ip()` - **新增**：通过 IP 自动获取用户地理位置
- `get_supported_cities()` - 获取支持的城市列表
- `get_city_coordinates(city)` - 获取城市坐标信息

## 🔧 自定义扩展 (Magentic-One Mode)

### 添加新的 agent

```python
def create_new_agent(model_client):
    return AssistantAgent(
        name="new_agent",
        model_client=model_client,
        description="新代理的清晰描述，帮助 MagenticOneOrchestrator 理解代理职责",
        system_message="专注于代理核心任务的系统消息，无需协作逻辑"
    )
```

### 三种协作模式对比

| 特性           | SelectorGroupChat      | Swarm               | Magentic-One        |
| -------------- | ---------------------- | ------------------- | ------------------- |
| **配置复杂度** | 复杂选择器函数 (~76 行) | 简单 handoffs 声明  | 零配置，仅需描述    |
| **协作方式**   | 集中式调度             | 去中心化交接        | 智能自动化协作      |
| **代理自主性** | 低（被动选择）         | 中（主动交接）      | 高（智能协调）      |
| **系统管理**   | 手动选择器逻辑         | 声明式 handoffs     | 自动化 Orchestrator |
| **学习成本**   | 高（复杂逻辑）         | 中（理解 handoffs） | 低（直观描述）      |
| **调试友好度** | 中（选择器可见）       | 中（交接明确）      | 高（自动化管理）    |
| **扩展性**     | 低（修改选择器）       | 中（配置 handoffs） | 高（添加描述）      |
| **代码量**     | 最多                   | 中等                | 最少                |

### 添加新的工具

在 MCP 服务器中添加新的工具，然后 AutoGen 会自动发现并使用。

## 🌈 运行示例

```plain
🤖 初始化天气查询系统...
✅ 系统准备就绪！

🗣️  用户查询: 今天北京天气怎么样
──────────────────────────────────────────────────
🔄 启动多代理协作...
   📋 意图解析代理 → 解析查询意图
   🌤️  天气查询代理 → 获取天气数据
   ✨ 响应格式化代理 → 美化输出结果

📋 查询结果:
根据最新天气预报，北京今天的天气是阴天，气温在27°C到35°C之间...
```

## 🔍 故障排除

### 常见问题

1. **API 密钥未设置**

   ```bash
   export OPENAI_API_KEY='your-api-key-here'
   ```

2. **依赖包问题**

   ```bash
   pip install -r requirements.txt --force-reinstall
   ```

3. **Python 环境问题**

   ```bash
   python --version  # 确保 Python 3.8+
   ```

### 🧪 测试和开发

```bash
# 运行测试套件（交互式选择协作模式）
python tests/run_tests.py

# 测试结果：50/50 (100%) 通过
# 报告保存在：tests/reports/20250627/
```

## 📊 项目信息

- **当前协作模式**: AutoGen Magentic-One 智能自动化团队协作
- **代理数量**: 3 个（意图解析、天气查询、响应格式化）
- **MCP 工具**: 6 个（包含 IP 定位功能）
- **支持城市**: 37 个中国主要城市 + 全球 IP 定位
- **技术栈**: AutoGen Magentic-One + MCP + 彩云天气 API + IP 定位服务
- **测试覆盖**: 50 个测试用例，100%通过率
- **配置简洁度**: 零配置协作，仅需代理描述
- **架构设计**: 单分支多模式，源代码专注业务逻辑，CLI 统一处理演示

### 🔀 协作模式选择

```bash
# 通用CLI自动选择模式
python src/weather_cli.py

# 命令行指定模式
python src/weather_cli.py --mode selector_groupchat
python src/weather_cli.py --mode swarm  
python src/weather_cli.py --mode magentic_one
```

---
