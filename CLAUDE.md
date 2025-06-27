# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

这是一个基于 Microsoft AutoGen 框架的多代理协作天气查询系统，支持智能 IP 地理定位。项目展示了智能体群组协作，通过三个专门的代理协作完成天气查询任务：

1. **意图解析代理** - 分析用户查询意图，提取城市和时间信息
2. **天气查询代理** - 执行具体的天气数据获取（集成工具调用），支持 IP 自动定位
3. **响应格式化代理** - 美化输出结果并提供生活建议

**🆕 核心功能更新：** 当用户查询没有明确指定城市时，系统会自动通过 IP 地址获取用户地理位置，实现无城市查询。

**🔄 协作模式：** 项目支持三种协作模式，方便学习和对比不同的多代理协作机制。

**📋 架构说明：**

- `src/selector_groupchat/` - SelectorGroupChat 集中式选择器协作模式（原始实现）
- `src/swarm/` - Swarm 去中心化 handoff 协作模式
- `src/magentic_one/` - Magentic-One 智能自动化团队协作模式

**🧪 测试系统：** 统一的测试系统支持动态选择协作模式，可通过环境变量 `WEATHER_MODE` 选择运行哪种实现。

## Quick Start Commands

### Environment Setup

```bash
# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量（推荐使用 .env.local）
cp .env.example .env.local
# 编辑 .env.local 文件，填入你的真实 API 密钥：
# OPENAI_API_KEY=your-openai-api-key
# CAIYUN_API_KEY=your-caiyun-api-key
```

### Running the System

**通用CLI（推荐）**：

```bash
# 交互式选择协作模式
python src/weather_cli.py "今天天气怎么样"

# 通过命令行参数指定模式
python src/weather_cli.py --mode selector_groupchat "今天天气"
python src/weather_cli.py --mode swarm "今天天气"
python src/weather_cli.py --mode magentic_one "今天天气"

# 通过环境变量指定模式
WEATHER_MODE=magentic_one python src/weather_cli.py "今天天气"

# 演示模式
python src/weather_cli.py --demo
python src/weather_cli.py --mode swarm --demo
```

**其他命令**：

```bash
# 检查依赖
pip check

# 注意：源代码模块已移除演示代码，推荐使用 CLI 进行演示
# python src/weather_cli.py --demo  # 推荐的演示方式
```

### Testing and Development

```bash
# 运行测试套件（交互式选择协作模式）
python tests/run_tests.py

# 选择模式后，测试结果示例：50/50 (100%) 通过
# 报告按日期分组：tests/reports/20250627/selector_groupchat_test_summary_20250627_143052.md
```

## Architecture Overview

### Core Files Structure

- `src/` - 核心源代码目录，包含三种协作模式的实现
  - `weather_cli.py` - **通用命令行界面**（支持三种模式动态选择 + 演示功能）
  - `selector_groupchat/` - 集中式选择器协作模式
    - `weather_team.py` - SelectorGroupChat 协作管理器（纯业务逻辑）
    - `weather_agents.py` - 基础代理定义和 MCP 工具集成
  - `swarm/` - 去中心化 handoff 协作模式
    - `weather_team.py` - Swarm 协作管理器（纯业务逻辑）
    - `weather_agents.py` - 带 handoff 配置的代理定义
  - `magentic_one/` - 智能自动化团队协作模式
    - `weather_team.py` - MagenticOneGroupChat 协作管理器（纯业务逻辑）
    - `weather_agents.py` - 专注任务的代理定义
- `mcp_server/` - MCP 服务器文件夹
  - `weather_mcp_server.py` - 彩云天气 MCP 服务器（真实 API 数据 + IP 定位功能）
- `tests/` - 测试套件
  - `run_tests.py` - 测试运行脚本（支持交互式模式选择）
  - `test_weather_agents.py` - 代理测试（支持动态模式导入）
  - `test_api.py` - API测试
  - `test_mcp_server.py` - MCP服务器测试
  - `reports/YYYYMMDD/` - 测试报告目录（按日期分组）
- `doc/` - 文档文件夹
  - `cy_weather.md` - 彩云天气 API 详细文档

### Multi-Agent Collaboration Flow (Magentic-One Mode)

**🧲 Magentic-One 协作机制：**

1. **智能自动化** - 系统自动管理代理间的协作，无需手动配置交接
2. **中央调度** - MagenticOneOrchestrator 自动分析任务并选择合适的代理
3. **简化配置** - 代理只需专注于自身任务，无需考虑协作逻辑
4. **自适应终止** - 支持 `MaxMessageTermination` 和 `TextMentionTermination` 智能终止

**协作流程：**

- MagenticOneOrchestrator 分析任务
- 自动选择 intent_parser 进行意图解析
- 自动调用 weather_agent 执行查询
- 自动调用 formatter 美化输出

**三种协作模式对比：**

| 特性           | SelectorGroupChat          | Swarm                   | Magentic-One         |
| -------------- | -------------------------- | ----------------------- | -------------------- |
| **协作方式**   | 集中式调度                 | 去中心化交接            | 智能自动化调度       |
| **配置复杂度** | 高（需要 `selector_func`） | 低（声明式 `handoffs`） | 极低（无需配置协作） |
| **代理自主性** | 低（被动接收）             | 高（主动交接）          | 中等（专注任务）     |
| **系统管理**   | 手动选择器                 | 代理自决策              | 自动调度器           |
| **学习成本**   | 中等                       | 高                      | 低                   |
| **调试友好度** | 好（流程清晰）             | 中等（handoff 复杂）     | 好（自动管理）       |
| **扩展性**     | 中等（需修改选择器）       | 高（添加 handoffs）      | 高（自动适配）       |
| **代码量**     | 76 行选择器逻辑             | 0 行选择器逻辑           | 0 行协作逻辑          |

### Tool Integration

代理通过 AutoGen 官方的 MCP 工具集成：

**MCP 工具**（通过 `autogen_ext.tools.mcp` 集成）：

- `query_weather_today(city)` - 查询今日天气
- `query_weather_tomorrow(city)` - 查询明日天气
- `query_weather_future_days(city, days)` - 查询未来几天天气
- `get_user_location_by_ip()` - **新增**：通过 IP 地址获取用户地理位置
- `get_supported_cities()` - 获取支持的城市列表
- `get_city_coordinates(city)` - 获取城市坐标信息

**MCP 集成方式**：

1. 使用 `StdioServerParams` 配置 MCP 服务器连接
2. 通过 `mcp_server_tools()` 获取 MCP 工具
3. 工具通过 MCP JSON-RPC 协议通信
4. 支持工具自动发现和动态调用

## Development Guidelines

### Adding New Agents (Magentic-One Mode)

在 `src/weather_agents.py` 中创建新代理：

```python
def create_new_agent(model_client: OpenAIChatCompletionClient) -> AssistantAgent:
    return AssistantAgent(
        name="agent_name",
        model_client=model_client,
        description="代理描述",
        tools=[tool_functions] if needed,
        system_message="详细的系统消息定义代理行为，专注于特定任务"
    )
```

**Magentic-One 配置要点：**

1. **简化配置**: 无需配置 handoffs 或选择器逻辑
2. **专注任务**: system_message 只需描述代理的核心任务
3. **自动协作**: MagenticOneOrchestrator 自动管理代理间的协作

**三种模式的代理配置对比：**

| 模式                  | 配置需求                          | 复杂度 | 维护成本 |
| --------------------- | --------------------------------- | ------ | -------- |
| **SelectorGroupChat** | 需要实现 `selector_func`          | 高     | 高       |
| **Swarm**             | 需要配置 `handoffs`               | 中     | 中       |
| **Magentic-One**      | 只需 description + system_message | 低     | 低       |

### Adding New Tools

**FastMCP 版本** - 在 MCP 服务器中添加新工具：

1. 在 `mcp_server/weather_mcp_server.py` 中使用 `@mcp.tool()` 装饰器定义新工具
2. 函数签名自动生成工具 Schema，支持类型提示
3. docstring 自动生成工具描述
4. AutoGen 会自动发现并使用新工具

```python
@mcp.tool()
async def new_weather_tool(city: str = "北京", param: int = 5) -> str:
    """新工具描述
    
    Args:
        city: 城市名称
        param: 参数说明
    """
    # 工具实现
    return "结果"
```

### Modifying Collaboration Flow (Swarm Mode)

**Swarm 模式协作配置：**

```python
# 在 src/weather_team.py 中配置 Swarm 团队
from autogen_agentchat.teams import Swarm
from autogen_agentchat.conditions import HandoffTermination, TextMentionTermination

# 创建终止条件
termination = HandoffTermination(target="user") | TextMentionTermination("TERMINATE")

# 创建 Swarm 团队
self.swarm_team = Swarm(
    participants=[self.intent_parser, self.weather_agent, self.formatter],
    termination_condition=termination
)
```

**与 SelectorGroupChat 的对比：**

| 特性       | SelectorGroupChat                    | Swarm                                           |
| ---------- | ------------------------------------ | ----------------------------------------------- |
| 协作方式   | 集中式调度                           | 去中心化交接                                    |
| 配置复杂度 | 高（需要 `selector_func`）           | 低（声明式 `handoffs`）                         |
| 终止条件   | `MaxMessageTermination` + 自定义逻辑 | `HandoffTermination` + `TextMentionTermination` |
| 扩展性     | 需修改选择器函数                     | 只需配置 handoffs                               |

## Key Dependencies

- `autogen-agentchat>=0.6.1` - AutoGen 核心框架
- `autogen-ext[openai]>=0.6.1` - OpenAI 集成扩展
- `mcp>=1.0.0` - Anthropic MCP Python SDK
- `fastmcp>=2.8.1` - FastMCP 框架（简化 MCP 开发）
- `httpx>=0.25.0` - HTTP 客户端库

## Important Notes

### Environment Variables Configuration

**必须配置的环境变量：**

- `OPENAI_API_KEY` - OpenAI API 密钥（必需）
- `CAIYUN_API_KEY` - 彩云天气 API 密钥（必需）

**🆕 IP 定位功能说明：**

- IP 定位使用免费的 `ipapi.co` 服务，无需额外 API 密钥
- 支持中国城市智能匹配，非中国地区提供友好提示
- 当用户查询不包含明确城市时自动触发

**可选的环境变量：**

- `OPENAI_MODEL` - OpenAI 模型名称（默认：gpt-4o-mini）
- `CAIYUN_BASE_URL` - 彩云天气 API 基础 URL（默认：<https://api.caiyunapp.com/v2.6）>

**安全提醒：**

- 推荐使用 `.env.local` 存储 API 密钥，该文件不会被提交到 Git
- 项目支持按优先级加载：`.env.local` > `.env`
- 请勿在代码中硬编码任何 API 密钥
- 从 `.env.example` 复制并填入你的真实密钥

### AutoGen Swarm 多代理系统

- **MCP 协议集成**：使用 `autogen_ext.tools.mcp` 模块
- **Swarm 协作模式**：意图解析 → weather_agent → formatter → user (完成)
- **去中心化交接**：每个代理通过 `handoffs` 声明可交接目标，主动调用 `transfer_to_xxx()`
- **智能定位**：支持无城市查询，自动 IP 地理定位
- **灵活终止条件**：`HandoffTermination(target="user")` | `TextMentionTermination("TERMINATE")`
- 系统消息采用中文，适合中文天气查询场景
- 智能城市处理：指定城市直接查询，未指定则 IP 定位
- **状态管理**：每次查询重新初始化 Swarm 实例，确保状态干净
- 通过环境变量自动加载 API 密钥

**Swarm vs SelectorGroupChat：**

- **配置简洁度**：Swarm (0 行选择器) vs SelectorGroupChat (76 行选择器逻辑)
- **协作方式**：去中心化 handoff vs 集中式调度
- **扩展性**：添加代理只需配置 handoffs vs 需修改选择器函数

### MCP 协议实现

- **MCP 通信**：通过 JSON-RPC 消息与 MCP 服务器通信
- **工具自动发现**：AutoGen 从 MCP 服务器获取可用工具
- **协议支持**：支持 `ListToolsRequest` 和 `CallToolRequest`
- **进程隔离**：每次工具调用启动独立的 MCP 服务器进程
- 日志显示 MCP 协议消息：`Processing request of type ListToolsRequest`

### MCP 天气服务器（FastMCP 版本）

- `weather_mcp_server.py` 使用 FastMCP 框架
- 支持 37 个中国主要城市，集成彩云天气真实 API
- **🆕 IP 定位功能**：集成 `ipapi.co` 服务，支持全球 IP 地理定位
- **注意：彩云天气 API 有频率限制，测试时请控制调用频率**
- API 失败时会返回明确的错误信息而非降级数据
- 使用标准 MCP 协议，可与 Claude Desktop 等客户端集成
- FastMCP 提供装饰器模式，自动类型推断和 Schema 生成
- **测试覆盖**：50 个测试用例，100%通过率
