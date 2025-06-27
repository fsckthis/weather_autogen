#!/usr/bin/env python3
"""
API层测试 - 测试高德地图API和彩云天气API的基础功能
"""

import pytest
import pytest_asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from mcp_server.weather_mcp_server import AmapGeocoder, WeatherAPI

class TestAmapAPI:
    """高德地图API测试"""
    
    @pytest_asyncio.fixture
    async def geocoder(self):
        """地理编码器实例"""
        geocoder = AmapGeocoder()
        yield geocoder
    
    @pytest.mark.asyncio
    async def test_amap_api_connection(self, geocoder):
        """测试高德API连接"""
        # 测试基础连接和API密钥
        coords = await geocoder.get_coordinates("北京")
        assert coords is not None, "高德API连接失败或API密钥无效"
    
    @pytest.mark.asyncio
    async def test_amap_predefined_cities(self, geocoder):
        """测试预定义城市（应该走缓存，不调用API）"""
        test_cities = ["北京", "上海", "广州"]
        
        for city in test_cities:
            coords = await geocoder.get_coordinates(city)
            assert coords is not None, f"预定义城市{city}获取坐标失败"
            lat, lon = coords
            assert isinstance(lat, float) and isinstance(lon, float)
            assert -90 <= lat <= 90 and -180 <= lon <= 180
    
    @pytest.mark.asyncio
    async def test_amap_dynamic_cities(self, geocoder):
        """测试动态城市（调用高德API）"""
        dynamic_cities = ["三亚", "桂林", "丽江"]
        
        for city in dynamic_cities:
            coords = await geocoder.get_coordinates(city)
            assert coords is not None, f"动态城市{city}获取坐标失败"
            lat, lon = coords
            # 检查坐标在中国范围内
            assert 15 <= lat <= 60, f"{city}纬度超出中国范围"
            assert 70 <= lon <= 140, f"{city}经度超出中国范围"
    
    
    @pytest.mark.asyncio
    async def test_amap_invalid_input(self, geocoder):
        """测试无效输入（高德API可能进行模糊匹配）"""
        # 使用更不可能匹配到的输入
        very_invalid_inputs = ["火星市abc123xyz", ""]
        none_count = 0
        
        for invalid in very_invalid_inputs:
            coords = await geocoder.get_coordinates(invalid)
            if coords is None:
                none_count += 1
        
        # 至少要有一个返回None（空字符串通常会返回None）
        assert none_count >= 1, f"应该有至少一个无效输入返回None"

class TestCaiyunAPI:
    """彩云天气API测试"""
    
    @pytest_asyncio.fixture 
    async def weather_api(self):
        """天气API实例"""
        from mcp_server.weather_mcp_server import geocoder
        api = WeatherAPI(geocoder)
        yield api
    
    @pytest.mark.asyncio
    async def test_caiyun_api_connection(self, weather_api):
        """测试彩云天气API连接"""
        # 使用北京测试API连接
        data = await weather_api.get_daily_weather("北京", days=1)
        assert data.get("status") == "ok", "彩云天气API连接失败或API密钥无效"
    
    @pytest.mark.asyncio
    async def test_caiyun_data_structure(self, weather_api):
        """测试彩云天气API返回数据结构"""
        data = await weather_api.get_daily_weather("北京", days=1)
        
        # 验证基础结构
        assert "status" in data
        assert "result" in data
        assert "daily" in data["result"]
        
        daily = data["result"]["daily"]
        required_fields = ["temperature", "skycon", "precipitation", "humidity", "wind"]
        
        for field in required_fields:
            assert field in daily, f"缺少必要字段: {field}"
            assert isinstance(daily[field], list), f"{field}应该是列表类型"
            assert len(daily[field]) > 0, f"{field}不应为空"
    
    @pytest.mark.asyncio
    async def test_caiyun_temperature_data(self, weather_api):
        """测试温度数据合理性"""
        data = await weather_api.get_daily_weather("北京", days=1)
        
        temp_data = data["result"]["daily"]["temperature"][0]
        temp_min = temp_data["min"]
        temp_max = temp_data["max"]
        
        # 温度合理性检查
        assert isinstance(temp_min, (int, float)), "最低温度应为数字"
        assert isinstance(temp_max, (int, float)), "最高温度应为数字"
        assert -50 <= temp_min <= 50, f"最低温度{temp_min}超出合理范围"
        assert -50 <= temp_max <= 50, f"最高温度{temp_max}超出合理范围"
        assert temp_min <= temp_max, f"最低温度{temp_min}不应高于最高温度{temp_max}"
    
    @pytest.mark.asyncio
    async def test_caiyun_multi_days(self, weather_api):
        """测试多天天气查询"""
        days_to_test = [1, 3, 5, 7]
        
        for days in days_to_test:
            data = await weather_api.get_daily_weather("北京", days=days)
            assert data.get("status") == "ok", f"查询{days}天天气失败"
            
            temp_list = data["result"]["daily"]["temperature"]
            assert len(temp_list) >= days, f"查询{days}天但只返回{len(temp_list)}天数据"
    
    @pytest.mark.asyncio
    async def test_caiyun_different_cities(self, weather_api):
        """测试不同城市天气查询"""
        cities = ["北京", "上海", "广州", "成都", "三亚"]
        
        for city in cities:
            data = await weather_api.get_daily_weather(city, days=1)
            assert data.get("status") == "ok", f"{city}天气查询失败"
    

class TestAPIIntegration:
    """API集成测试 - 测试高德地图和彩云天气API的配合"""
    
    @pytest.mark.asyncio
    async def test_geocoding_to_weather_flow(self):
        """测试地理编码到天气查询的完整流程"""
        geocoder = AmapGeocoder()
        weather_api = WeatherAPI(geocoder)
        
        # 1. 使用高德API获取坐标
        city = "三亚"  # 动态城市，会调用高德API
        coords = await geocoder.get_coordinates(city)
        assert coords is not None, f"获取{city}坐标失败"
        
        # 2. 使用坐标查询天气
        data = await weather_api.get_daily_weather(city, days=1)
        assert data.get("status") == "ok", f"使用坐标查询{city}天气失败"
    

# 慢速测试标记
@pytest.mark.slow
@pytest.mark.asyncio
async def test_api_performance():
    """API性能测试（慢速测试）"""
    geocoder = AmapGeocoder()
    weather_api = WeatherAPI(geocoder)
    
    import time
    
    # 测试地理编码性能
    start_time = time.time()
    await geocoder.get_coordinates("杭州")
    geocoding_time = time.time() - start_time
    
    # 测试天气查询性能
    start_time = time.time()
    await weather_api.get_daily_weather("北京", days=1)
    weather_time = time.time() - start_time
    
    # 性能断言（可根据实际情况调整）
    assert geocoding_time < 5.0, f"地理编码耗时过长: {geocoding_time:.2f}s"
    assert weather_time < 5.0, f"天气查询耗时过长: {weather_time:.2f}s"