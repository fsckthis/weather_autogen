#!/usr/bin/env python3
"""
MCP服务器测试 - 测试MCP工具的输出和功能
"""

import pytest
import asyncio
import sys
import os
import json

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from mcp_server.weather_mcp_server import (
    handle_query_weather_today,
    handle_query_weather_tomorrow, 
    handle_query_weather_future_days,
    handle_get_supported_cities,
    handle_get_city_coordinates,
    server
)

class TestMCPWeatherTools:
    """MCP天气工具测试"""
    
    @pytest.mark.asyncio
    async def test_query_weather_today_tool(self):
        """测试今天天气查询工具"""
        # 测试默认城市（北京）
        result = await handle_query_weather_today({})
        assert len(result) == 1
        assert result[0].type == "text"
        content = result[0].text
        
        # 验证输出格式
        assert "📍" in content, "缺少位置标识"
        assert "🌤️" in content, "缺少天气标识"
        assert "🌡️" in content, "缺少温度标识"
        assert "北京" in content, "默认应为北京天气"
    
    @pytest.mark.asyncio
    async def test_query_weather_today_with_city(self):
        """测试指定城市今天天气查询"""
        result = await handle_query_weather_today({"city": "上海"})
        assert len(result) == 1
        content = result[0].text
        
        assert "上海" in content, "应显示指定城市上海"
        assert "📍" in content
        assert "🌤️" in content
    
    @pytest.mark.asyncio
    async def test_query_weather_tomorrow_tool(self):
        """测试明天天气查询工具"""
        result = await handle_query_weather_tomorrow({"city": "北京"})
        assert len(result) == 1
        content = result[0].text
        
        # 检查是否是明天的日期（相对今天+1）
        from datetime import datetime, timedelta
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        assert "北京" in content
        # 明天的天气数据应该存在
        assert "❌" not in content or "明天天气数据不足" not in content
    
    @pytest.mark.asyncio
    async def test_query_weather_future_days_tool(self):
        """测试未来几天天气查询工具"""
        # 测试默认3天
        result = await handle_query_weather_future_days({"city": "北京"})
        assert len(result) == 1
        content = result[0].text
        
        assert "北京" in content
        assert "未来" in content
        assert "天天气预报" in content
        
        # 应该包含多个日期
        content_lines = content.split("\n")
        date_lines = [line for line in content_lines if "📅" in line and "202" in line]
        assert len(date_lines) >= 3, "应该包含至少3天的天气数据"
    
    @pytest.mark.asyncio
    async def test_query_weather_future_days_custom_days(self):
        """测试自定义天数的未来天气查询"""
        result = await handle_query_weather_future_days({"city": "上海", "days": 5})
        assert len(result) == 1
        content = result[0].text
        
        assert "上海" in content
        assert "未来5天" in content
    
    @pytest.mark.asyncio
    async def test_get_supported_cities_tool(self):
        """测试获取支持城市列表工具"""
        result = await handle_get_supported_cities({})
        assert len(result) == 1
        content = result[0].text
        
        assert "内置城市列表" in content
        assert "北京" in content
        assert "上海" in content
        assert "通过高德地图API动态获取坐标" in content
    
    @pytest.mark.asyncio
    async def test_get_city_coordinates_tool(self):
        """测试获取城市坐标工具"""
        # 测试预定义城市
        result = await handle_get_city_coordinates({"city": "北京"})
        assert len(result) == 1
        content = result[0].text
        
        assert "📍 北京 坐标信息" in content
        assert "纬度" in content
        assert "经度" in content
        assert "39.9042" in content  # 北京的预定义纬度
    
    @pytest.mark.asyncio
    async def test_get_city_coordinates_dynamic(self):
        """测试动态城市坐标获取"""
        result = await handle_get_city_coordinates({"city": "三亚"})
        assert len(result) == 1
        content = result[0].text
        
        if "❌" not in content:  # 如果成功获取坐标
            assert "📍 三亚 坐标信息" in content
            assert "纬度" in content
            assert "经度" in content
        else:  # 如果API调用失败
            assert "未找到城市" in content or "获取" in content and "坐标失败" in content
    
    @pytest.mark.asyncio
    async def test_invalid_city_handling(self):
        """测试无效城市处理"""
        # 测试今天天气查询的错误处理
        result = await handle_query_weather_today({"city": "不存在的城市xxx"})
        assert len(result) == 1
        content = result[0].text
        assert "❌" in content, "应该显示错误信息"
    
    @pytest.mark.asyncio
    async def test_weather_tool_output_format(self):
        """测试天气工具输出格式的一致性"""
        tools_to_test = [
            (handle_query_weather_today, {"city": "北京"}),
            (handle_query_weather_tomorrow, {"city": "北京"}),
            (handle_get_city_coordinates, {"city": "北京"})
        ]
        
        for tool_func, args in tools_to_test:
            result = await tool_func(args)
            
            # 验证基础格式
            assert isinstance(result, list), f"{tool_func.__name__}应返回列表"
            assert len(result) >= 1, f"{tool_func.__name__}应至少返回一个内容项"
            assert result[0].type == "text", f"{tool_func.__name__}应返回文本类型"
            assert isinstance(result[0].text, str), f"{tool_func.__name__}应返回字符串内容"
            assert len(result[0].text) > 0, f"{tool_func.__name__}不应返回空内容"

class TestMCPServerConfiguration:
    """MCP服务器配置测试"""
    
    @pytest.mark.asyncio
    async def test_server_tools_list(self):
        """测试MCP服务器工具列表"""
        from mcp_server.weather_mcp_server import list_tools
        
        tools = await list_tools()
        assert isinstance(tools, list), "工具列表应为列表类型"
        assert len(tools) >= 5, "应该至少有5个工具"
        
        # 验证必要工具存在
        tool_names = [tool.name for tool in tools]
        expected_tools = [
            "query_weather_today",
            "query_weather_tomorrow", 
            "query_weather_future_days",
            "get_supported_cities",
            "get_city_coordinates"
        ]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names, f"缺少必要工具: {expected_tool}"
    
    @pytest.mark.asyncio
    async def test_tool_schemas(self):
        """测试工具模式定义"""
        from mcp_server.weather_mcp_server import list_tools
        
        tools = await list_tools()
        
        for tool in tools:
            # 验证基础字段
            assert hasattr(tool, 'name'), f"工具{tool}缺少名称"
            assert hasattr(tool, 'description'), f"工具{tool.name}缺少描述"
            assert hasattr(tool, 'inputSchema'), f"工具{tool.name}缺少输入模式"
            
            # 验证输入模式结构
            schema = tool.inputSchema
            assert isinstance(schema, dict), f"工具{tool.name}输入模式应为字典"
            assert "type" in schema, f"工具{tool.name}输入模式缺少类型"
            assert schema["type"] == "object", f"工具{tool.name}输入模式类型应为object"
    
    @pytest.mark.asyncio
    async def test_tool_handler_mapping(self):
        """测试工具处理函数映射"""
        from mcp_server.weather_mcp_server import TOOL_HANDLERS, call_tool
        
        # 验证所有工具都有对应的处理函数
        expected_handlers = [
            "query_weather_today",
            "query_weather_tomorrow",
            "query_weather_future_days", 
            "get_supported_cities",
            "get_city_coordinates"
        ]
        
        for handler_name in expected_handlers:
            assert handler_name in TOOL_HANDLERS, f"缺少处理函数: {handler_name}"
            assert callable(TOOL_HANDLERS[handler_name]), f"处理函数{handler_name}不可调用"
    
    @pytest.mark.asyncio
    async def test_tool_call_interface(self):
        """测试工具调用接口"""
        from mcp_server.weather_mcp_server import call_tool
        
        # 测试有效工具调用
        result = await call_tool("query_weather_today", {"city": "北京"})
        assert isinstance(result, list)
        assert len(result) >= 1
        
        # 测试无效工具调用
        result = await call_tool("invalid_tool", {})
        assert isinstance(result, list)
        assert len(result) == 1
        assert "未知工具" in result[0].text

class TestMCPWeatherDataFormat:
    """MCP天气数据格式测试"""
    
    @pytest.mark.asyncio
    async def test_weather_format_completeness(self):
        """测试天气格式化输出的完整性"""
        result = await handle_query_weather_today({"city": "北京"})
        content = result[0].text
        
        # 检查必要的信息字段
        required_elements = [
            "📍",  # 地点
            "🌤️",  # 天气
            "🌡️",  # 温度  
            "💧",  # 湿度
            "💨",  # 风力
            "🌧️",  # 降水概率
            "💡"   # 生活建议
        ]
        
        for element in required_elements:
            assert element in content, f"天气格式化输出缺少{element}"
    
    @pytest.mark.asyncio
    async def test_weather_format_consistency(self):
        """测试天气格式化输出的一致性"""
        cities = ["北京", "上海", "广州"]
        
        for city in cities:
            result = await handle_query_weather_today({"city": city})
            content = result[0].text
            
            # 每个城市的输出都应该包含相同的格式元素
            lines = content.strip().split('\n')
            assert len(lines) >= 6, f"{city}天气输出行数不足"
            
            # 第一行应该是地点和日期
            assert city in lines[0], f"{city}第一行应包含城市名"
            assert "📍" in lines[0], f"{city}第一行应包含位置标识"

# 集成测试
@pytest.mark.integration
@pytest.mark.asyncio
async def test_mcp_tools_integration():
    """MCP工具集成测试"""
    # 测试工具之间的协作
    
    # 1. 获取支持的城市
    cities_result = await handle_get_supported_cities({})
    cities_content = cities_result[0].text
    assert "北京" in cities_content
    
    # 2. 获取城市坐标
    coords_result = await handle_get_city_coordinates({"city": "北京"})
    coords_content = coords_result[0].text
    assert "坐标信息" in coords_content
    
    # 3. 查询天气
    weather_result = await handle_query_weather_today({"city": "北京"})
    weather_content = weather_result[0].text
    assert "📍 北京" in weather_content
    
    # 所有工具都应该能正常工作
    assert "❌" not in cities_content
    # 坐标和天气查询可能因为网络问题失败，所以不强制要求无错误