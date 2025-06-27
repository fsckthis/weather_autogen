"""
多代理协作天气查询系统
真正的智能体群组！三个代理协作完成天气查询任务
"""

import os
from dotenv import load_dotenv
from autogen_agentchat.teams import MagenticOneGroupChat
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.ui import Console
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
    """天气查询智能体群组 - Magentic-One 协作系统"""
    
    def __init__(self, model_name: str = None, verbose: bool = True):
        # 检查 OpenAI API Key
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("❌ 未设置 OPENAI_API_KEY 环境变量，请在 .env 文件中配置")
        
        # 使用传入的模型名称，否则从环境变量获取，最后使用默认值
        model_name = model_name or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            
        self.model_client = OpenAIChatCompletionClient(
            model=model_name,
            api_key=openai_api_key
        )
        self.intent_parser = None
        self.weather_agent = None
        self.formatter = None
        self.magentic_team = None
        self.verbose = verbose
        
    async def initialize(self, show_init_message=True):
        """初始化所有代理和 Magentic-One 团队"""
        
        self.intent_parser = create_intent_parser_agent(self.model_client)
        self.weather_agent = await create_weather_query_agent(self.model_client)
        self.formatter = create_response_formatter_agent(self.model_client)
      
        termination = MaxMessageTermination(max_messages=10) | TextMentionTermination("查询完成")
        
        self.magentic_team = MagenticOneGroupChat(
            participants=[self.intent_parser, self.weather_agent, self.formatter],
            model_client=self.model_client,
            termination_condition=termination
        )
    
    async def query(self, user_input: str, show_process: bool = True) -> str:
        """执行天气查询"""
        if not self.magentic_team:
            await self.initialize()
            
        if show_process:
            print(f"\n{'='*60}")
            print(f"🗣️ 用户查询：{user_input}")
            print(f"{'='*60}")
            
            # 流式显示 Magentic-One 协作过程
            stream = self.magentic_team.run_stream(task=user_input)
            result = await Console(stream)
            
            print(f"\n{'='*60}")
            print("🎉 Magentic-One 协作完成！")
            print(f"{'='*60}")
            
            # 返回最终结果
            final_message = result.messages[-1].content if result.messages else "Magentic-One 协作查询失败"
            return final_message
        else:
            # 静默模式
            result = await self.magentic_team.run(task=user_input)
            return result.messages[-1].content if result.messages else "Magentic-One 协作查询失败"
    
    
    async def close(self):
        """关闭资源"""
        if self.model_client:
            await self.model_client.close()
            print("🔒 Magentic-One 智能体群组资源已释放")