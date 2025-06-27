# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

这是一个基于 Microsoft AutoGen 框架的多代理协作天气查询系统。项目展示了智能体群组协作，通过三个专门的代理协作完成天气查询任务：

1. **意图解析代理** - 分析用户查询意图，提取城市和时间信息
2. **天气查询代理** - 执行具体的天气数据获取（集成工具调用）
3. **响应格式化代理** - 美化输出结果并提供生活建议

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

```bash
# 测试天气 API 功能
cd mcp_server && python test_weather_api.py

# 测试 MCP 工具（通过 CLI）
python weather_cli.py "上海今天天气"

# 演示模式
python weather_cli.py --demo

# 直接查询模式
python weather_cli.py "今天天气怎么样"

# 原始多代理协作演示（详细日志）
python weather_team.py

# 检查依赖
pip check
```

### Testing and Development

```bash
python run_tests.py
```

## Architecture Overview

### Core Files Structure

- `weather_team.py` - 多代理协作管理器 (WeatherAgentTeam)
- `weather_agents.py` - 代理定义和 MCP 工具集成：意图解析、天气查询、响应格式化、简单代理
- `weather_cli.py` - 简洁的命令行界面，隐藏复杂日志
- `mcp_server/` - MCP 服务器文件夹
  - `weather_mcp_server.py` - 彩云天气 MCP 服务器（真实 API 数据）
  - `test_weather_api.py` - 天气 API 功能测试脚本
  - `README.md` - MCP 服务器详细文档
- `doc/` - 文档文件夹
  - `cy_weather.md` - 彩云天气 API 详细文档

### Multi-Agent Collaboration Flow

1. **SelectorGroupChat** 管理代理选择和流程控制
2. **Agent Selector Function** 控制协作顺序：intent_parser → weather_agent → formatter
3. **Termination Conditions** 限制最大消息数和检查完成状态

### Tool Integration

代理通过 AutoGen 官方的 MCP 工具集成：

**MCP 工具**（通过 `autogen_ext.tools.mcp` 集成）：

- `query_weather_today(city)` - 查询今日天气
- `query_weather_tomorrow(city)` - 查询明日天气
- `query_weather_future_days(city, days)` - 查询未来几天天气
- `get_supported_cities()` - 获取支持的城市列表

**MCP 集成方式**：

1. 使用 `StdioServerParams` 配置 MCP 服务器连接
2. 通过 `mcp_server_tools()` 获取 MCP 工具
3. 工具通过 MCP JSON-RPC 协议通信
4. 支持工具自动发现和动态调用

## Development Guidelines

### Adding New Agents

在 `weather_agents.py` 中创建新代理：

```python
def create_new_agent(model_client: OpenAIChatCompletionClient) -> AssistantAgent:
    return AssistantAgent(
        name="agent_name",
        model_client=model_client,
        description="代理描述",
        tools=[tool_functions] if needed,
        system_message="详细的系统消息定义代理行为"
    )
```

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

### Modifying Collaboration Flow

在 `WeatherAgentTeam._agent_selector()` 中修改代理选择逻辑，控制协作顺序和终止条件。

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

**可选的环境变量：**

- `OPENAI_MODEL` - OpenAI 模型名称（默认：gpt-4o-mini）
- `CAIYUN_BASE_URL` - 彩云天气 API 基础 URL（默认：<https://api.caiyunapp.com/v2.6）>

**安全提醒：**

- 推荐使用 `.env.local` 存储 API 密钥，该文件不会被提交到 Git
- 项目支持按优先级加载：`.env.local` > `.env`
- 请勿在代码中硬编码任何 API 密钥
- 从 `.env.example` 复制并填入你的真实密钥

### AutoGen 多代理系统

- **MCP 协议集成**：使用 `autogen_ext.tools.mcp` 模块
- **多代理协作**：意图解析 → 天气查询 → 响应格式化
- 系统消息采用中文，适合中文天气查询场景
- 默认城市为"北京"
- 代理协作有最大消息数限制（8 条消息）
- 通过环境变量自动加载 API 密钥

### MCP 协议实现

- **MCP 通信**：通过 JSON-RPC 消息与 MCP 服务器通信
- **工具自动发现**：AutoGen 从 MCP 服务器获取可用工具
- **协议支持**：支持 `ListToolsRequest` 和 `CallToolRequest`
- **进程隔离**：每次工具调用启动独立的 MCP 服务器进程
- 日志显示 MCP 协议消息：`Processing request of type ListToolsRequest`

### MCP 天气服务器（FastMCP 版本）

- `weather_mcp_server.py` 使用 FastMCP 框架
- 支持 37 个中国主要城市，集成彩云天气真实 API
- **注意：彩云天气 API 有频率限制，测试时请控制调用频率**
- API 失败时会返回明确的错误信息而非降级数据
- 使用标准 MCP 协议，可与 Claude Desktop 等客户端集成
- FastMCP 提供装饰器模式，自动类型推断和 Schema 生成
