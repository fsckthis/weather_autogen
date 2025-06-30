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

async def create_intent_parser_agent(model_client: OpenAIChatCompletionClient) -> AssistantAgent:
    """创建意图解析代理 - Swarm 版本，负责意图解析和IP定位"""
    mcp_tools = await get_weather_mcp_tools()
    
    return AssistantAgent(
        name="intent_parser",
        model_client=model_client,
        handoffs=["weather_agent"],  # 可以交接给天气查询代理
        tools=mcp_tools,
        description="专业的意图解析代理，负责分析用户天气查询意图并处理IP定位",
        system_message="""你是智能意图解析专家。分析用户查询并提供明确的城市信息。

📋 **处理流程：**

**第1步：检查城市信息**
- 如果查询包含明确城市名（如"北京"、"Tokyo"、"纽约"） → 使用该城市
- 如果查询没有城市名 → 执行第2步

**第2步：自动获取位置**
- 立即调用 get_user_location_by_ip()
- 从结果中提取任何可用的城市名
- 如果找到城市名 → 使用该城市名
- 如果找不到 → 使用"上海"作为默认

**第3步：输出标准格式并交接**
严格按照此格式输出：
城市：[确定的城市名]
时间：[today/tomorrow/future]
查询：[描述用户想查询什么]

完成解析后调用 transfer_to_weather_agent() 交接

**🚫 绝对禁止输出"未指定"**

**📝 执行示例：**
用户："今天天气怎么样？"
→ 1. 没有城市名
→ 2. 调用 get_user_location_by_ip()
→ 3. 假设IP定位成功获取到具体城市，或使用默认"上海"
→ 4. 输出：
城市：[IP定位的城市或上海]
时间：today
查询：查询今天的天气
→ 5. 调用 transfer_to_weather_agent()

**立即开始分析用户查询。**"""
    )


async def create_weather_query_agent(model_client: OpenAIChatCompletionClient) -> AssistantAgent:
    """创建天气查询代理 - Swarm 版本，执行查询后交接给格式化代理"""
    mcp_tools = await get_weather_mcp_tools()
    
    return AssistantAgent(
        name="weather_agent",
        model_client=model_client,
        handoffs=["formatter"],  # 可以交接给响应格式化代理
        tools=mcp_tools,
        description="执行具体的天气查询操作，支持自动IP定位，完成后交接给格式化代理",
        system_message="""你是天气查询机器人。接收意图解析结果并执行具体的天气查询。

📋 **处理流程：**

**第1步：解析意图信息**
- 从接收到的消息中提取城市名和时间类型
- 城市名格式：城市：[具体城市名]
- 时间格式：时间：[today/tomorrow/future]

**第2步：执行天气查询**
- 根据时间选择合适的工具：
  - "today"/"今天" → query_weather_today(城市名)
  - "tomorrow"/"明天" → query_weather_tomorrow(城市名)  
  - "future"/"未来" → query_weather_future_days(城市名, days=3)

**第3步：交接结果**
- 获得天气数据后，调用 transfer_to_formatter() 交接给格式化代理

**📝 执行示例：**
接收："城市：东京\n时间：today\n查询：查询今天的天气"
→ 1. 解析：城市=东京，时间=today
→ 2. 调用 query_weather_today("东京")
→ 3. 调用 transfer_to_formatter() 交接结果

**立即开始执行。**"""
    )


def create_response_formatter_agent(model_client: OpenAIChatCompletionClient) -> AssistantAgent:
    """创建响应格式化代理 - Swarm 版本，美化输出，完成整个协作流程"""
    return AssistantAgent(
        name="formatter",
        model_client=model_client,
        handoffs=["user"],  # 可以交接回用户（表示完成）
        description="美化天气查询结果并提供贴心建议，完成整个协作流程",
        system_message="""你是专业的天气播报员。将天气查询结果转换成规范的格式化回复。

🎯 **严格按照以下格式输出：**

{城市}的天气情况如下：

🌤️ 天气：{天气状况}
🌡️ 温度：{最低温}°C ~ {最高温}°C
💧 湿度：{湿度}%
💨 风力：{风力}级
🌧️ 降水概率：{降水概率}%

生活建议：{根据天气提供的个性化建议}

📝 **生活建议规则：**
- 雨天/降水概率>60%：提醒带伞
- 高温>28°C：建议防暑降温，穿轻便衣物
- 低温<10°C：建议保暖添衣
- 晴天：适合户外活动
- 多云：适合出行，注意天气变化

🚫 **严格禁止：**
- 使用其他格式
- 省略任何emoji图标
- 改变温度范围格式
- 添加额外的文字说明

📝 **完整示例：**
今天在日本印西的天气情况如下：

🌥️ 天气：多云
🌡️ 温度：23°C ~ 31°C
💧 湿度：55%
💨 风力：6级
🌧️ 降水概率：0%

生活建议：今天气温较高，请注意防暑降温，适合穿着轻便的衣物。希望你有个愉快的一天！

🎯 **立即按此格式美化天气信息，完成后说"查询完成"。**"""
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
