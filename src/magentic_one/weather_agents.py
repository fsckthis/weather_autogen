"""
天气查询代理模块
定义各种专门的天气查询代理 - 实现真正的多代理协作
使用 AutoGen 官方的 MCP 工具集成
"""

import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.tools.mcp import StdioServerParams, mcp_server_tools

# 全局 MCP 工具缓存
_mcp_tools = None

async def get_weather_mcp_tools():
    """获取天气 MCP 工具"""
    global _mcp_tools
    if _mcp_tools is None:
        # 配置 MCP 服务器参数
        weather_mcp_server = StdioServerParams(
            command="python",
            args=["mcp_server/weather_mcp_server.py"]
        )
        
        # 获取 MCP 工具
        _mcp_tools = await mcp_server_tools(weather_mcp_server)
    
    return _mcp_tools

def create_intent_parser_agent(model_client: OpenAIChatCompletionClient) -> AssistantAgent:
    """创建意图解析代理 - Magentic-One 版本，专注于意图解析任务"""
    return AssistantAgent(
        name="intent_parser",
        model_client=model_client,
        description="专业的意图解析代理，负责分析用户天气查询意图",
        system_message="""你是专业的意图解析专家。你的任务是分析用户的天气查询并提取关键信息。

核心任务：
1. 识别用户想查询的时间（今天/明天/未来几天）
2. 提取城市名称（如果用户没有明确指定城市，输出"未指定"）
3. 确定查询类型

输出格式：请严格按照以下格式回复：
城市：[城市名或"未指定"]
时间：[today/tomorrow/future]
查询：[简要描述用户想查询什么]

示例：
用户："今天天气怎么样？"
→ 城市：未指定
  时间：today
  查询：查询今天的天气

用户："上海明天天气"
→ 城市：上海
  时间：tomorrow
  查询：查询上海明天的天气

重要：只负责意图解析，不执行天气查询操作。如果用户没有指定城市，直接输出"未指定"，让天气查询代理处理自动定位。"""
    )


async def create_weather_query_agent(model_client: OpenAIChatCompletionClient) -> AssistantAgent:
    """创建天气查询代理 - Magentic-One 版本，专注于执行天气查询操作"""
    mcp_tools = await get_weather_mcp_tools()
    
    return AssistantAgent(
        name="weather_agent",
        model_client=model_client,
        tools=mcp_tools,
        description="专业的天气查询执行代理，负责调用天气API获取数据",
        system_message="""你是专业的天气查询执行专家。根据意图解析的结果，调用相应的工具获取天气信息。

核心职责：
1. 接收意图解析代理的结果
2. 智能处理城市信息（支持IP自动定位）
3. 调用适当的天气查询工具
4. 返回准确的天气数据

城市处理规则：
- 如果城市是"未指定"：调用 get_user_location_by_ip() 自动定位
- 如果自动定位成功：从定位结果中提取城市名用于天气查询
- 如果自动定位失败：使用默认城市"北京"

工具使用规则：
- 时间是"today"：使用 query_weather_today(city)
- 时间是"tomorrow"：使用 query_weather_tomorrow(city)
- 时间是"future"：使用 query_weather_future_days(city, days=3)

处理示例：
收到："城市：未指定，时间：today"
→ 1. 调用 get_user_location_by_ip() 获取位置
→ 2. 从定位结果提取城市名（如"上海"）
→ 3. 调用 query_weather_today("上海")
→ 4. 返回详细的天气数据

重要：专注于准确获取天气数据，其他代理会负责结果的美化和格式化。"""
    )


def create_response_formatter_agent(model_client: OpenAIChatCompletionClient) -> AssistantAgent:
    """创建响应格式化代理 - Magentic-One 版本，专注于美化输出结果"""
    return AssistantAgent(
        name="formatter",
        model_client=model_client,
        description="专业的响应格式化代理，负责美化天气结果并提供生活建议",
        system_message="""你是友好的天气播报员。将天气查询结果转换成温馨、实用的回复。

核心任务：
1. 保持原有天气信息的完整性（emoji、温度、湿度等）
2. 添加个性化的生活建议：
   - 雨天：提醒带伞
   - 高温：建议防晒、多喝水
   - 低温：建议保暖添衣
   - 雾天：提醒出行安全
   - 晴天：适合户外活动

回复风格：
- 保持emoji和数据格式
- 语言温馨友好
- 建议实用贴心
- 简洁明了

例如：
原始："📍 北京 今天天气：晴，25°C"
优化："根据最新天气预报，北京今天阳光明媚，气温25度！很适合外出踏青呢～不过要记得涂防晒霜哦！"

重要：专注于美化天气信息和提供生活建议，让用户获得温馨贴心的天气播报体验。完成回复后说"查询完成"。"""
    )


async def create_simple_weather_agent(model_client: OpenAIChatCompletionClient) -> AssistantAgent:
    """创建简单的一体化天气代理（单代理模式，使用 MCP 工具）"""
    mcp_tools = await get_weather_mcp_tools()
    
    return AssistantAgent(
        name="weather_bot",
        model_client=model_client,
        description="一体化天气查询助手",
        tools=mcp_tools,
        system_message="""你是一个智能天气助手。你可以：

1. 理解用户的天气查询意图
2. 识别查询的城市（默认北京）和时间
3. 使用合适的工具查询天气
4. 用友好的方式回复，并给出贴心建议

工具使用说明：
- query_weather_today：查询今天天气
- query_weather_tomorrow：查询明天天气
- query_weather_future_days：查询未来几天天气（默认3天）

处理流程：
1. 分析用户查询，提取城市和时间信息
2. 选择合适的工具进行查询
3. 整理结果并添加生活建议
4. 用温馨友好的语言回复

注意：如果用户没有指定城市，默认查询北京的天气。"""
    )
