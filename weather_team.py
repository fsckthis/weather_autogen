"""
多代理协作天气查询系统
真正的智能体群组！三个代理协作完成天气查询任务
"""

import asyncio
import os
from typing import Sequence
from dotenv import load_dotenv
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.ui import Console
from autogen_agentchat.messages import BaseAgentEvent, BaseChatMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from weather_agents import (
    create_intent_parser_agent,
    create_weather_query_agent,
    create_response_formatter_agent
)

# 加载环境变量 - 按优先级加载
load_dotenv(".env.local")  # 优先加载本地配置
load_dotenv()  # 兜底加载默认配置


class WeatherAgentTeam:
    """天气查询智能体群组 - 多代理协作系统"""
    
    def __init__(self, model_name: str = None, verbose: bool = True):
        # 检查 OpenAI API Key
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("❌ 未设置 OPENAI_API_KEY 环境变量，请在 .env 文件中配置")
        
        # 使用环境变量中的模型名称，如果没有则使用默认值
        if model_name is None:
            model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            
        self.model_client = OpenAIChatCompletionClient(
            model=model_name,
            api_key=openai_api_key
        )
        self.intent_parser = None
        self.weather_agent = None
        self.formatter = None
        self.team = None
        self.verbose = verbose
        
    async def initialize(self):
        """初始化所有代理和团队"""
        if self.verbose:
            print("🤖 正在初始化智能体群组...")
        
        # 创建三个专门的代理（weather_agent 使用 MCP 工具）
        self.intent_parser = create_intent_parser_agent(self.model_client)
        self.weather_agent = await create_weather_query_agent(self.model_client)
        self.formatter = create_response_formatter_agent(self.model_client)
        
        if self.verbose:
            print("✅ 代理创建完成：")
            print("   📋 intent_parser - 意图解析专家")
            print("   🌤️ weather_agent - 天气查询专家")
            print("   ✨ formatter - 响应美化专家")
        
        # 创建协作团队
        self.team = SelectorGroupChat(
            participants=[self.intent_parser, self.weather_agent, self.formatter],
            model_client=self.model_client,
            selector_func=self._agent_selector,
            termination_condition=self._create_termination_condition()
        )
        
        if self.verbose:
            print("🎯 智能体群组协作系统已就绪！")
        
    def _agent_selector(self, messages: Sequence[BaseAgentEvent | BaseChatMessage]) -> str | None:
        """智能体选择器 - 控制代理协作流程"""
        if len(messages) <= 1:
            # 第一步：意图解析
            if self.verbose:
                print("🔄 协作流程：用户查询 → 意图解析代理")
            return "intent_parser"
        
        last_speaker = messages[-1].source
        
        if last_speaker == "intent_parser":
            # 第二步：天气查询
            if self.verbose:
                print("🔄 协作流程：意图解析完成 → 天气查询代理")
            return "weather_agent"
        elif last_speaker == "weather_agent":
            # 第三步：响应格式化
            if self.verbose:
                print("🔄 协作流程：天气查询完成 → 响应格式化代理")
            return "formatter"
        else:
            # 完成协作
            if self.verbose:
                print("✅ 协作流程完成！")
            return None
    
    def _create_termination_condition(self):
        """创建终止条件"""
        text_termination = TextMentionTermination("查询完成")
        max_messages_termination = MaxMessageTermination(max_messages=8)
        return text_termination | max_messages_termination
    
    async def query_with_collaboration(self, user_input: str, show_process: bool = True) -> str:
        """执行多代理协作查询"""
        if not self.team:
            await self.initialize()
            
        if show_process:
            print(f"\n{'='*60}")
            print(f"🗣️ 用户查询：{user_input}")
            print(f"{'='*60}")
            print("🚀 启动多代理协作流程...\n")
            
            # 流式显示协作过程
            stream = self.team.run_stream(task=user_input)
            result = await Console(stream)
            
            print(f"\n{'='*60}")
            print("🎉 多代理协作完成！")
            print(f"{'='*60}")
            
            # 返回最终结果
            final_message = result.messages[-1].content if result.messages else "协作查询失败"
            return final_message
        else:
            # 静默模式
            result = await self.team.run(task=user_input)
            return result.messages[-1].content if result.messages else "协作查询失败"
    
    async def demo_collaboration(self):
        """演示多代理协作"""
        print("🎭 多代理协作演示")
        print("=" * 40)
        
        demo_queries = [
            "今天天气怎么样？",
            "上海明天天气"
        ]
        
        for i, query in enumerate(demo_queries, 1):
            print(f"\n📋 演示 {i}/{len(demo_queries)}")
            await self.query_with_collaboration(query, show_process=True)
            
            if i < len(demo_queries):
                print("\n⏳ 准备下一个演示...\n")
                await asyncio.sleep(2)
        
        print("\n🎉 多代理协作演示完成！")
        print("💡 每个查询都经过了：意图解析 → 天气查询 → 响应美化 的完整协作流程")
    
    async def close(self):
        """关闭资源"""
        if self.model_client:
            await self.model_client.close()
            print("🔒 智能体群组资源已释放")


async def main():
    team = WeatherAgentTeam()
    try:
        print("=" * 50)
        # 演示协作流程
        await team.demo_collaboration()
        
    finally:
        await team.close()


if __name__ == "__main__":
    asyncio.run(main())