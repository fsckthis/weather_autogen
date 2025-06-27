#!/usr/bin/env python3
"""
通用天气查询CLI
支持三种协作模式：selector_groupchat, swarm, magentic_one
隐藏复杂的多代理协作日志，只显示关键步骤和结果
"""

import asyncio
import sys
import logging
import os

# 隐藏复杂的AutoGen日志
logging.getLogger("autogen_core").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.basicConfig(level=logging.ERROR, format='')

def choose_mode():
    """选择协作模式"""
    print("\n🤖 选择天气系统协作模式:")
    print("1. selector_groupchat - 集中式选择器协作模式")
    print("2. swarm - 去中心化 handoff 协作模式") 
    print("3. magentic_one - 智能自动化团队协作模式")
    
    while True:
        try:
            choice = input("\n请选择模式 (1-3): ").strip()
            if choice == "1":
                return "selector_groupchat"
            elif choice == "2":
                return "swarm"
            elif choice == "3":
                return "magentic_one"
            else:
                print("❌ 无效选择，请输入 1、2 或 3")
        except KeyboardInterrupt:
            print("\n👋 再见！")
            sys.exit(0)

class SimpleWeatherCLI:
    """简洁的天气查询命令行界面"""
    
    def __init__(self, mode: str = None):
        self.mode = mode or choose_mode()
        self.team = None
        
    def _get_team_class(self):
        """动态导入对应模式的WeatherAgentTeam"""
        try:
            # 添加当前目录到Python路径
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            if current_dir not in sys.path:
                sys.path.insert(0, current_dir)
            
            if self.mode == "selector_groupchat":
                from selector_groupchat.weather_team import WeatherAgentTeam
            elif self.mode == "swarm":
                from swarm.weather_team import WeatherAgentTeam
            elif self.mode == "magentic_one":
                from magentic_one.weather_team import WeatherAgentTeam
            else:
                raise ValueError(f"未知的协作模式: {self.mode}")
            return WeatherAgentTeam
        except ImportError as e:
            print(f"❌ 无法导入 {self.mode} 模式: {e}")
            sys.exit(1)

    async def initialize(self):
        """初始化天气查询团队"""
        mode_names = {
            "selector_groupchat": "SelectorGroupChat 集中式选择器",
            "swarm": "Swarm 去中心化 handoff", 
            "magentic_one": "Magentic-One 智能自动化"
        }
        
        print("🤖 初始化天气查询系统...")
        print(f"🔧 协作模式: {mode_names.get(self.mode, self.mode)}")
        
        try:
            WeatherAgentTeam = self._get_team_class()
            # 使用静默模式初始化，避免重复的协作流程输出
            self.team = WeatherAgentTeam(verbose=False)
            await self.team.initialize()
            print("✅ 系统准备就绪！")
            print()
        except Exception as e:
            print(f"❌ 初始化失败: {e}")
            sys.exit(1)
    
    async def query_weather(self, user_input: str):
        """查询天气并显示简洁的协作过程"""
        print(f"🗣️  用户查询: {user_input}")
        print("─" * 50)
        
        try:
            # 显示协作步骤
            print("🔄 启动多代理协作...")
            print("   📋 意图解析代理 → 解析查询意图")
            
            # 执行查询但隐藏详细日志
            result = await self.team.query(user_input, show_process=False)
            
            print("   🌤️  天气查询代理 → 获取天气数据")
            print("   ✨ 响应格式化代理 → 美化输出结果")
            print()
            
            # 显示最终结果
            print("📋 查询结果:")
            print("─" * 50)
            print(result)
            print("─" * 50)
            
        except Exception as e:
            print(f"❌ 查询失败: {e}")
        
        print()
    
    async def interactive_mode(self):
        """交互式查询模式"""
        await self.initialize()
        
        print("🌤️  欢迎使用智能天气查询系统")
        print("💡 支持查询：今天/明天/未来几天的天气")
        print("💡 支持城市：北京、上海、广州等37个主要城市")
        print("💡 输入 'exit' 或 'quit' 退出系统")
        print("═" * 60)
        print()
        
        while True:
            try:
                user_input = input("🌟 请输入天气查询: ").strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() in ['exit', 'quit', '退出', 'q']:
                    print("👋 感谢使用，再见！")
                    break
                
                await self.query_weather(user_input)
                
            except KeyboardInterrupt:
                print("\n👋 感谢使用，再见！")
                break
            except Exception as e:
                print(f"❌ 发生错误: {e}")
                print()
    
    async def demo_mode(self):
        """演示模式"""
        await self.initialize()
        
        print("🎭 天气查询演示模式")
        print("═" * 60)
        print()
        
        demo_queries = [
            "今天天气怎么样？",
            "上海明天天气",
            "广州未来3天天气"
        ]
        
        for i, query in enumerate(demo_queries, 1):
            print(f"📋 演示 {i}/{len(demo_queries)}")
            await self.query_weather(query)
            
            if i < len(demo_queries):
                print("⏳ 准备下一个演示...")
                await asyncio.sleep(2)
                print()
        
        print("🎉 演示完成！")
    
    async def close(self):
        """关闭系统"""
        if self.team:
            await self.team.close()

async def main():
    """主函数"""
    # 检查环境变量或命令行参数中的模式
    mode = None
    
    # 检查是否有 --mode 参数
    if "--mode" in sys.argv:
        mode_index = sys.argv.index("--mode")
        if mode_index + 1 < len(sys.argv):
            mode = sys.argv[mode_index + 1]
            # 移除 --mode 参数
            sys.argv.pop(mode_index + 1)
            sys.argv.pop(mode_index)
    
    # 检查环境变量
    if not mode:
        mode = os.getenv("WEATHER_MODE")
    
    cli = SimpleWeatherCLI(mode)
    
    try:
        # 检查命令行参数
        if len(sys.argv) > 1:
            if sys.argv[1] == "--demo":
                await cli.demo_mode()
            else:
                # 直接查询模式
                query = " ".join(sys.argv[1:])
                await cli.initialize()
                await cli.query_weather(query)
        else:
            # 交互式模式
            await cli.interactive_mode()
            
    finally:
        await cli.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 感谢使用，再见！")
    except Exception as e:
        print(f"❌ 系统错误: {e}")