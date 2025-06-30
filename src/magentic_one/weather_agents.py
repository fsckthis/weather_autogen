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
    """创建意图解析代理 - Magentic-One 版本，负责意图解析和IP定位"""
    mcp_tools = await get_weather_mcp_tools()
    
    return AssistantAgent(
        name="intent_parser",
        model_client=model_client,
        description="专业的意图解析代理，负责分析用户天气查询意图并处理IP定位",
        tools=mcp_tools,
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

**第3步：输出标准格式**
严格按照此格式输出：
城市：[确定的城市名]
时间：[today/tomorrow/future]
查询：[描述用户想查询什么]

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

**🔄 解析完成后，weather_agent会根据此信息查询天气，formatter会格式化结果。**

**立即开始分析用户查询。**"""
    )


async def create_weather_query_agent(model_client: OpenAIChatCompletionClient) -> AssistantAgent:
    """创建天气查询代理 - Magentic-One 版本，专注于执行天气查询操作"""
    mcp_tools = await get_weather_mcp_tools()
    
    return AssistantAgent(
        name="weather_agent",
        model_client=model_client,
        tools=mcp_tools,
        description="专业的天气查询执行代理，负责调用天气API获取原始数据",
        system_message="""你是专业天气查询执行代理。收到意图解析结果后，立即查询天气。

📋 **处理流程：**

1. **解析意图结果**：从意图解析代理获取城市名和时间
2. **立即查询天气**：根据时间选择对应工具
   - "today" → query_weather_today(城市名)
   - "tomorrow" → query_weather_tomorrow(城市名)
   - "future" → query_weather_future_days(城市名, days=3)
3. **返回原始数据**：直接返回API获取的天气数据

**📝 执行示例：**
收到："城市：Tokyo，时间：today"
→ 立即调用 query_weather_today("Tokyo")
→ 返回原始天气结果，不做任何格式化

收到："城市：上海，时间：tomorrow"  
→ 立即调用 query_weather_tomorrow("上海")
→ 返回原始天气结果，不做任何格式化

**🚫 严格禁止：**
- 进行任何格式化或美化输出
- 添加生活建议或emoji装饰
- 提供最终用户格式的回复
- 询问用户任何问题

**✅ 正确做法：**
- 只提供简洁的原始天气数据
- 让formatter代理处理美化工作

**🔄 数据必须经过formatter美化后才能给用户**

**立即查询天气并返回原始数据。**"""
    )


def create_response_formatter_agent(model_client: OpenAIChatCompletionClient) -> AssistantAgent:
    """创建响应格式化代理 - Magentic-One 版本，专注于美化输出结果"""
    return AssistantAgent(
        name="formatter",
        model_client=model_client,
        description="🔥CRITICAL🔥 最终必需步骤：将天气原始数据转换为用户友好格式。没有此步骤用户无法看到正确结果！",
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
