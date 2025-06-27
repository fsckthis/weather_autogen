#!/usr/bin/env python3
"""
彩云天气 MCP 服务器
基于 FastMCP 框架实现真实天气查询
"""

import os
import httpx
import logging
from typing import Dict, Any, Optional
from fastmcp import FastMCP
from dotenv import load_dotenv

# 加载环境变量
parent_dir = os.path.dirname(os.path.dirname(__file__))
load_dotenv(os.path.join(parent_dir, ".env.local"))
load_dotenv(os.path.join(parent_dir, ".env"))

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("weather-mcp-server")

# API 配置
CAIYUN_API_KEY = os.getenv("CAIYUN_API_KEY")
if not CAIYUN_API_KEY:
    logger.error("❌ 未设置 CAIYUN_API_KEY 环境变量，请在 .env 文件中配置")
    raise ValueError("CAIYUN_API_KEY 环境变量未设置")

CAIYUN_BASE_URL = os.getenv("CAIYUN_BASE_URL", "https://api.caiyunapp.com/v2.6")

AMAP_API_KEY = os.getenv("AMAP_API_KEY")
if not AMAP_API_KEY:
    logger.error("❌ 未设置 AMAP_API_KEY 环境变量，请在 .env 文件中配置")
    raise ValueError("AMAP_API_KEY 环境变量未设置")

AMAP_BASE_URL = os.getenv("AMAP_BASE_URL", "https://restapi.amap.com/v3/geocode/geo")

# 城市坐标映射
CITY_COORDINATES = {
    "北京": (39.9042, 116.4074),
    "上海": (31.2304, 121.4737),
    "广州": (23.1291, 113.2644),
    "深圳": (22.5431, 114.0579),
    "杭州": (30.2741, 120.1551),
    "南京": (32.0603, 118.7969),
    "武汉": (30.5928, 114.3055),
    "成都": (30.5728, 104.0668),
    "西安": (34.3416, 108.9398),
    "重庆": (29.5630, 106.5516),
    "天津": (39.3434, 117.3616),
    "苏州": (31.2989, 120.5853),
    "青岛": (36.0671, 120.3826),
    "宁波": (29.8683, 121.5440),
    "无锡": (31.5912, 120.3019),
    "济南": (36.6512, 117.1201),
    "大连": (38.9140, 121.6147),
    "沈阳": (41.8057, 123.4315),
    "长春": (43.8171, 125.3235),
    "哈尔滨": (45.8038, 126.5349),
    "福州": (26.0745, 119.2965),
    "厦门": (24.4798, 118.0894),
    "昆明": (25.0389, 102.7183),
    "南昌": (28.6820, 115.8581),
    "合肥": (31.8669, 117.2741),
    "石家庄": (38.0428, 114.5149),
    "太原": (37.8706, 112.5489),
    "郑州": (34.7466, 113.6254),
    "长沙": (28.2282, 112.9388),
    "南宁": (22.8170, 108.3669),
    "海口": (20.0444, 110.1999),
    "贵阳": (26.6470, 106.6302),
    "兰州": (36.0611, 103.8343),
    "银川": (38.4681, 106.2731),
    "西宁": (36.6171, 101.7782),
    "乌鲁木齐": (43.7793, 87.6177),
    "拉萨": (29.6625, 91.1110)
}

# 天气现象映射
SKYCON_MAP = {
    "CLEAR_DAY": "晴天",
    "CLEAR_NIGHT": "晴夜",
    "PARTLY_CLOUDY_DAY": "多云",
    "PARTLY_CLOUDY_NIGHT": "多云",
    "CLOUDY": "阴天",
    "LIGHT_HAZE": "轻度雾霾",
    "MODERATE_HAZE": "中度雾霾",
    "HEAVY_HAZE": "重度雾霾",
    "LIGHT_RAIN": "小雨",
    "MODERATE_RAIN": "中雨",
    "HEAVY_RAIN": "大雨",
    "STORM_RAIN": "暴雨",
    "FOG": "雾",
    "LIGHT_SNOW": "小雪",
    "MODERATE_SNOW": "中雪",
    "HEAVY_SNOW": "大雪",
    "STORM_SNOW": "暴雪",
    "DUST": "浮尘",
    "SAND": "沙尘",
    "WIND": "大风"
}

# 创建 FastMCP 服务器实例
mcp = FastMCP("weather-mcp-server")

# 工具类和辅助函数
class AmapGeocoder:
    """高德地图地理编码客户端"""
    
    def __init__(self):
        self.api_key = AMAP_API_KEY
        self.base_url = AMAP_BASE_URL
        self.coord_cache = {}
    
    async def get_coordinates(self, city_name: str) -> Optional[tuple[float, float]]:
        """获取城市坐标"""
        if city_name in CITY_COORDINATES:
            return CITY_COORDINATES[city_name]
        
        if city_name in self.coord_cache:
            return self.coord_cache[city_name]
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                params = {
                    "key": self.api_key,
                    "address": city_name,
                    "output": "json"
                }
                
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                
                data = response.json()
                if data.get("status") == "1" and data.get("count", "0") != "0":
                    geocodes = data.get("geocodes", [])
                    if geocodes:
                        location = geocodes[0].get("location", "")
                        if location:
                            lon, lat = map(float, location.split(","))
                            coordinates = (lat, lon)
                            self.coord_cache[city_name] = coordinates
                            logger.info(f"✅ 获取城市坐标成功：{city_name} -> {coordinates}")
                            return coordinates
            
            logger.warning(f"⚠️ 未找到城市坐标：{city_name}")
            return None
            
        except Exception as e:
            logger.error(f"❌ 地理编码API调用失败：{city_name}, 错误：{e}")
            return None

class WeatherAPI:
    """彩云天气API客户端"""
    
    def __init__(self, geocoder: AmapGeocoder):
        self.api_key = CAIYUN_API_KEY
        self.base_url = CAIYUN_BASE_URL
        self.geocoder = geocoder
    
    async def get_daily_weather(self, city: str, days: int = 1) -> Dict[str, Any]:
        """获取天气预报"""
        coordinates = await self.geocoder.get_coordinates(city)
        if not coordinates:
            raise ValueError(f"不支持的城市：{city}")
        
        lat, lon = coordinates
        url = f"{self.base_url}/{self.api_key}/{lon},{lat}/daily"
        params = {"dailysteps": min(days, 15)}
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            if hasattr(e, 'response') and e.response.status_code == 429:
                raise Exception(f"API调用频率过高，请稍后再试。彩云天气API有频率限制。")
            else:
                raise Exception(f"天气API请求失败: {e}")
        except Exception as e:
            raise Exception(f"天气API调用错误: {e}")
    
    def format_weather_data(self, data: Dict[str, Any], city: str, target_day: int = 0) -> str:
        """格式化天气数据"""
        if data.get("status") != "ok":
            return f"❌ 获取{city}天气失败"
        
        daily = data["result"]["daily"]
        
        if target_day >= len(daily["temperature"]):
            return f"❌ 没有{city}第{target_day+1}天的天气数据"
        
        date_info = daily["temperature"][target_day]
        date = date_info["date"][:10]
        
        temp = daily["temperature"][target_day]
        temp_max = int(temp["max"])
        temp_min = int(temp["min"])
        
        skycon = daily["skycon"][target_day]["value"]
        weather_desc = SKYCON_MAP.get(skycon, skycon)
        
        precipitation = daily["precipitation"][target_day]
        rain_prob = min(int(precipitation["probability"] * 100), 100)
        
        humidity = daily["humidity"][target_day]
        humidity_avg = int(humidity["avg"] * 100)
        
        wind = daily["wind"][target_day]
        wind_speed = wind["avg"]["speed"]
        wind_level = self.wind_speed_to_level(wind_speed)
        
        tips = self._get_weather_tips(weather_desc, temp_max, temp_min, rain_prob)
        
        return f"""📍 {city} {date}
🌤️ 天气：{weather_desc}
🌡️ 温度：{temp_min}°C ~ {temp_max}°C
💧 湿度：{humidity_avg}%
💨 风力：{wind_level}级
🌧️ 降水概率：{rain_prob}%
💡 生活建议：{tips}"""
    
    def wind_speed_to_level(self, speed_ms: float) -> int:
        """风速转风力等级"""
        speed_kmh = speed_ms * 3.6
        if speed_kmh < 1:
            return 0
        elif speed_kmh < 6:
            return 1
        elif speed_kmh < 12:
            return 2
        elif speed_kmh < 20:
            return 3
        elif speed_kmh < 29:
            return 4
        elif speed_kmh < 39:
            return 5
        elif speed_kmh < 50:
            return 6
        elif speed_kmh < 62:
            return 7
        elif speed_kmh < 75:
            return 8
        elif speed_kmh < 89:
            return 9
        elif speed_kmh < 103:
            return 10
        elif speed_kmh < 118:
            return 11
        else:
            return 12
    
    def _get_weather_tips(self, weather: str, temp_max: int, temp_min: int, rain_prob: int) -> str:
        """根据天气生成生活建议"""
        tips = []
        
        if temp_max >= 30:
            tips.append("天气炎热，注意防暑降温")
        elif temp_min <= 5:
            tips.append("天气寒冷，注意保暖添衣")
        elif temp_max - temp_min > 15:
            tips.append("昼夜温差大，适时增减衣物")
        
        if rain_prob > 70:
            tips.append("降雨概率高，建议携带雨具")
        elif rain_prob > 30:
            tips.append("可能有降雨，备好雨伞")
        
        if "雾" in weather or "霾" in weather:
            tips.append("能见度较低，出行注意安全")
        elif "晴" in weather:
            tips.append("天气晴朗，适合户外活动")
        elif "雪" in weather:
            tips.append("有降雪，注意路面湿滑")
        
        return "，".join(tips) if tips else "天气适宜，祝您生活愉快"

# 创建全局实例
geocoder = AmapGeocoder()
weather_api = WeatherAPI(geocoder)

# 定义工具函数
@mcp.tool()
async def query_weather_today(city: str = "北京") -> str:
    """查询今天的天气
    
    Args:
        city: 城市名称，如：北京、上海、广州等
    """
    try:
        data = await weather_api.get_daily_weather(city, days=1)
        return weather_api.format_weather_data(data, city, target_day=0)
    except Exception as e:
        logger.error(f"查询今天天气失败: {e}")
        return f"❌ 查询{city}今天天气失败: {str(e)}"

@mcp.tool()
async def query_weather_tomorrow(city: str = "北京") -> str:
    """查询明天的天气
    
    Args:
        city: 城市名称，如：北京、上海、广州等
    """
    try:
        data = await weather_api.get_daily_weather(city, days=2)
        if len(data["result"]["daily"]["temperature"]) > 1:
            return weather_api.format_weather_data(data, city, target_day=1)
        else:
            return f"❌ 获取{city}明天天气数据不足"
    except Exception as e:
        logger.error(f"查询明天天气失败: {e}")
        return f"❌ 查询{city}明天天气失败: {str(e)}"

@mcp.tool()
async def query_weather_future_days(city: str = "北京", days: int = 3) -> str:
    """查询未来几天的天气预报
    
    Args:
        city: 城市名称，如：北京、上海、广州等
        days: 查询天数，范围1-15天
    """
    try:
        data = await weather_api.get_daily_weather(city, days=days)
        
        if data.get("status") != "ok":
            return f"❌ 获取{city}天气失败"
        
        daily = data["result"]["daily"]
        results = [f"📍 {city} 未来{days}天天气预报："]
        
        for i in range(min(days, len(daily["temperature"]))):
            date_info = daily["temperature"][i]
            date = date_info["date"][:10]
            
            temp_max = int(date_info["max"])
            temp_min = int(date_info["min"])
            
            skycon = daily["skycon"][i]["value"]
            weather_desc = SKYCON_MAP.get(skycon, skycon)
            
            results.append(f"📅 {date}：{weather_desc}，{temp_min}°C ~ {temp_max}°C")
        
        return "\n".join(results)
        
    except Exception as e:
        logger.error(f"查询未来天气失败: {e}")
        return f"❌ 查询{city}未来{days}天天气失败: {str(e)}"

@mcp.tool()
async def get_supported_cities() -> str:
    """获取支持的城市列表"""
    cities = list(CITY_COORDINATES.keys())
    return "内置城市列表：\n" + "、".join(cities) + "\n\n其他城市也支持，通过高德地图API动态获取坐标。"

@mcp.tool()
async def get_city_coordinates(city: str = "北京") -> str:
    """获取城市坐标（支持全国所有城市）
    
    Args:
        city: 城市名称，支持全国所有城市，如：北京、上海、三亚、拉萨等
    """
    try:
        coordinates = await geocoder.get_coordinates(city)
        if coordinates:
            lat, lon = coordinates
            return f"📍 {city} 坐标信息：\n纬度：{lat}\n经度：{lon}\n坐标：{lat},{lon}"
        else:
            return f"❌ 未找到城市：{city}，请检查城市名称是否正确"
    except Exception as e:
        logger.error(f"获取城市坐标失败: {e}")
        return f"❌ 获取{city}坐标失败: {str(e)}"

# 运行服务器
if __name__ == "__main__":
    logger.info("启动彩云天气 MCP 服务器...")
    mcp.run()