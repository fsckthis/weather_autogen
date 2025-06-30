"""
多代理协作天气查询系统
真正的智能体群组！三个代理协作完成天气查询任务
"""

import os
from typing import Sequence
from dotenv import load_dotenv
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.ui import Console
from autogen_agentchat.messages import BaseAgentEvent, BaseChatMessage
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
    """天气查询智能体群组 - 多代理协作系统"""
    
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
        self.team = None
        self.verbose = verbose
        
    async def initialize(self):
        """初始化所有代理和团队"""
        
        # 创建三个专门的代理（支持 MCP 工具和IP定位）
        self.intent_parser = await create_intent_parser_agent(self.model_client)
        self.weather_agent = await create_weather_query_agent(self.model_client)
        self.formatter = create_response_formatter_agent(self.model_client)
        
        # 创建协作团队
        self.team = SelectorGroupChat(
            participants=[self.intent_parser, self.weather_agent, self.formatter],
            model_client=self.model_client,
            selector_func=self._agent_selector,
            termination_condition=self._create_termination_condition()
        )
        
    def _agent_selector(self, messages: Sequence[BaseAgentEvent | BaseChatMessage]) -> str | None:
        """智能体选择器 - 控制代理协作流程"""
        if len(messages) <= 1:
            # 第一步：意图解析
            return "intent_parser"
        
        last_speaker = messages[-1].source
        
        if last_speaker == "intent_parser":
            # 第二步：天气查询
            return "weather_agent"
        elif last_speaker == "weather_agent":
            # 第三步：响应格式化
            return "formatter"
        else:
            # 完成协作
            return None
    
    def _create_termination_condition(self):
        """创建终止条件"""
        text_termination = TextMentionTermination("查询完成")
        max_messages_termination = MaxMessageTermination(max_messages=8)
        return text_termination | max_messages_termination
    
    async def query(self, user_input: str, show_process: bool = None) -> str:
        """执行天气查询"""
        if not self.team:
            await self.initialize()
        
        # 如果没有明确指定，检查环境变量，否则默认为 False
        if show_process is None:
            show_process = False
            
        if show_process:
            print(f"\n{'='*60}")
            print(f"🗣️ 用户查询：{user_input}")
            print(f"{'='*60}")
            
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
    
    
    async def close(self):
        """关闭资源"""
        if self.model_client:
            await self.model_client.close()
            print("🔒 智能体群组资源已释放")