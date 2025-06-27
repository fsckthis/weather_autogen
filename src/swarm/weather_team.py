"""
多代理协作天气查询系统
真正的智能体群组！三个代理协作完成天气查询任务
"""

import asyncio
import os
from typing import Sequence
from dotenv import load_dotenv
from autogen_agentchat.teams import Swarm
from autogen_agentchat.conditions import HandoffTermination, TextMentionTermination
from autogen_agentchat.ui import Console
from autogen_agentchat.messages import HandoffMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from .weather_agents import (
    create_intent_parser_agent,
    create_weather_query_agent,
    create_response_formatter_agent
)

# 加载环境变量 - 按优先级加载
load_dotenv(".env.local")  # 优先加载本地配置
load_dotenv()  # 兜底加载默认配置


class WeatherAgentTeam:
    """天气查询智能体群组 - Swarm 协作系统"""
    
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
        self.swarm_team = None
        self.verbose = verbose
        
    async def initialize(self, show_init_message=True):
        """初始化所有代理和 Swarm 团队"""
        if self.verbose and show_init_message:
            print("🐝 正在初始化 Swarm 智能体群组...")
        
        # 创建三个专门的代理（每个代理都配置了 handoffs）
        self.intent_parser = create_intent_parser_agent(self.model_client)
        self.weather_agent = await create_weather_query_agent(self.model_client)
        self.formatter = create_response_formatter_agent(self.model_client)
        
        if self.verbose and show_init_message:
            print("✅ Swarm 代理创建完成：")
            print("   📋 intent_parser → [weather_agent]")
            print("   🌤️ weather_agent → [formatter]") 
            print("   ✨ formatter → [user] (完成)")
        
        # 创建 Swarm 协作团队
        # HandoffTermination: 当有代理交接给 'user' 时停止
        # TextMentionTermination: 当提到 'TERMINATE' 时停止
        termination = HandoffTermination(target="user") | TextMentionTermination("TERMINATE")
        
        self.swarm_team = Swarm(
            participants=[self.intent_parser, self.weather_agent, self.formatter],
            termination_condition=termination
        )
        
        if self.verbose and show_init_message:
            print("🐝 Swarm 智能体群组协作系统已就绪！")
            print("💡 协作模式：去中心化 handoff 机制")
    
    async def query_with_collaboration(self, user_input: str, show_process: bool = True) -> str:
        """执行 Swarm 协作查询"""
        if not self.swarm_team:
            await self.initialize()
            
        if show_process:
            print(f"\n{'='*60}")
            print(f"🗣️ 用户查询：{user_input}")
            print(f"{'='*60}")
            print("🐝 启动 Swarm 协作流程...\n")
            print("📋 协作路径：intent_parser → weather_agent → formatter → 完成")
            print("-" * 60)
            
            # 流式显示 Swarm 协作过程
            stream = self.swarm_team.run_stream(task=user_input)
            result = await Console(stream)
            
            print(f"\n{'='*60}")
            print("🎉 Swarm 协作完成！")
            print(f"{'='*60}")
            
            # 返回最终结果
            final_message = result.messages[-1].content if result.messages else "Swarm 协作查询失败"
            return final_message
        else:
            # 静默模式
            result = await self.swarm_team.run(task=user_input)
            return result.messages[-1].content if result.messages else "Swarm 协作查询失败"
    
    async def demo_collaboration(self):
        """演示 Swarm 协作"""
        print("🐝 Swarm 协作演示")
        print("=" * 40)
        
        demo_queries = [
            "今天天气怎么样？",
            "上海明天天气"
        ]
        
        for i, query in enumerate(demo_queries, 1):
            print(f"\n📋 演示 {i}/{len(demo_queries)}")
            
            # 为每个查询重新初始化 Swarm，确保状态干净
            self.swarm_team = None
            await self.initialize(show_init_message=(i == 1))  # 只在第一次显示初始化信息
            
            await self.query_with_collaboration(query, show_process=True)
            
            if i < len(demo_queries):
                print("\n⏳ 准备下一个 Swarm 演示...\n")
                await asyncio.sleep(2)
        
        print("\n🎉 Swarm 协作演示完成！")
        print("💡 每个查询都通过 handoff 机制自动完成：")
        print("   📋 intent_parser（解析意图）→ handoff")
        print("   🌤️ weather_agent（查询天气）→ handoff") 
        print("   ✨ formatter（美化输出）→ 完成")
    
    async def close(self):
        """关闭资源"""
        if self.model_client:
            await self.model_client.close()
            print("🔒 Swarm 智能体群组资源已释放")


async def main():
    team = WeatherAgentTeam()
    try:
        print("=" * 50)
        print("🐝 AutoGen Swarm 天气查询系统")
        print("=" * 50)
        # 演示 Swarm 协作流程
        await team.demo_collaboration()
        
    finally:
        await team.close()


if __name__ == "__main__":
    asyncio.run(main())