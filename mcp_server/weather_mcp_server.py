#!/usr/bin/env python3
"""
彩云天气 MCP 服务器
基于 FastMCP 框架实现真实天气查询
"""

import os
import sys
import httpx
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# 必须在导入 FastMCP 之前设置环境变量和日志配置
os.environ["FASTMCP_LOG_LEVEL"] = "CRITICAL"
os.environ["NO_COLOR"] = "1"
os.environ["TERM"] = "dumb"

# 自定义日志过滤器，过滤掉特定消息
class MessageFilter(logging.Filter):
    """过滤掉 FastMCP 的启动消息"""
    def filter(self, record):
        # 过滤掉包含 "Starting MCP server" 的消息
        if "Starting MCP server" in record.getMessage():
            return False
        return True

# 设置基本日志配置
logging.basicConfig(level=logging.INFO, format='%(message)s')

# 为根日志器添加过滤器
root_logger = logging.getLogger()
root_logger.addFilter(MessageFilter())

# 预先设置所有可能的日志器级别
for logger_name in [
    "FastMCP", "FastMCP.server", "FastMCP.server.server",
    "fastmcp", "fastmcp.server", "fastmcp.server.server",
    "mcp", "mcp.server", "rich", "httpx"
]:
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.WARNING)  # 允许警告和错误，但过滤掉 INFO 级别的启动消息
    logger.addFilter(MessageFilter())

# 现在才导入 FastMCP
from fastmcp import FastMCP

# 加载环境变量
parent_dir = os.path.dirname(os.path.dirname(__file__))
load_dotenv(os.path.join(parent_dir, ".env.local"))
load_dotenv(os.path.join(parent_dir, ".env"))

# 允许天气服务器的关键日志
logger = logging.getLogger("weather-mcp-server")
logger.setLevel(logging.INFO)

# API 配置
CAIYUN_API_KEY = os.getenv("CAIYUN_API_KEY")
if not CAIYUN_API_KEY:
    logger.error("❌ 未设置 CAIYUN_API_KEY 环境变量，请在 .env 文件中配置")
    raise ValueError("CAIYUN_API_KEY 环境变量未设置")

CAIYUN_BASE_URL = os.getenv("CAIYUN_BASE_URL", "https://api.caiyunapp.com/v2.6")

AMAP_API_KEY = os.getenv("AMAP_API_KEY")
# 如果没有高德 API，仅使用内置城市坐标
if not AMAP_API_KEY:
    logger.warning("⚠️ 未设置 AMAP_API_KEY 环境变量，将仅支持内置城市列表")

AMAP_BASE_URL = os.getenv("AMAP_BASE_URL", "https://restapi.amap.com/v3/geocode/geo")

# 城市坐标映射 - 支持全球主要城市
CITY_COORDINATES = {
    # === 中国城市 ===
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
    "拉萨": (29.6625, 91.1110),
    
    # === 日本城市 ===
    "Tokyo": (35.6762, 139.6503),
    "东京": (35.6762, 139.6503),
    "Osaka": (34.6937, 135.5023),
    "大阪": (34.6937, 135.5023),
    "Kyoto": (35.0116, 135.7681),
    "京都": (35.0116, 135.7681),
    "Yokohama": (35.4437, 139.6380),
    "横滨": (35.4437, 139.6380),
    "Nagoya": (35.1815, 136.9066),
    "名古屋": (35.1815, 136.9066),
    "Sapporo": (43.0642, 141.3469),
    "札幌": (43.0642, 141.3469),
    "Fukuoka": (33.5904, 130.4017),
    "福冈": (33.5904, 130.4017),
    "Kobe": (34.6901, 135.1956),
    "神户": (34.6901, 135.1956),
    "Hiroshima": (34.3853, 132.4553),
    "广岛": (34.3853, 132.4553),
    "Sendai": (38.2682, 140.8694),
    "仙台": (38.2682, 140.8694),
    "Inzai": (35.832, 140.145),
    "印西": (35.832, 140.145),
    
    # === 韩国城市 ===
    "Seoul": (37.5665, 126.9780),
    "首尔": (37.5665, 126.9780),
    "Busan": (35.1796, 129.0756),
    "釜山": (35.1796, 129.0756),
    "Incheon": (37.4563, 126.7052),
    "仁川": (37.4563, 126.7052),
    "Daegu": (35.8714, 128.6014),
    "大邱": (35.8714, 128.6014),
    "Daejeon": (36.3504, 127.3845),
    "大田": (36.3504, 127.3845),
    "Gwangju": (35.1595, 126.8526),
    "光州": (35.1595, 126.8526),
    
    # === 美国城市 ===
    "New York": (40.7128, -74.0060),
    "纽约": (40.7128, -74.0060),
    "Los Angeles": (34.0522, -118.2437),
    "洛杉矶": (34.0522, -118.2437),
    "Chicago": (41.8781, -87.6298),
    "芝加哥": (41.8781, -87.6298),
    "Houston": (29.7604, -95.3698),
    "休斯顿": (29.7604, -95.3698),
    "Phoenix": (33.4484, -112.0740),
    "凤凰城": (33.4484, -112.0740),
    "Philadelphia": (39.9526, -75.1652),
    "费城": (39.9526, -75.1652),
    "San Antonio": (29.4241, -98.4936),
    "圣安东尼奥": (29.4241, -98.4936),
    "San Diego": (32.7157, -117.1611),
    "圣地亚哥": (32.7157, -117.1611),
    "Dallas": (32.7767, -96.7970),
    "达拉斯": (32.7767, -96.7970),
    "San Jose": (37.3382, -121.8863),
    "圣何塞": (37.3382, -121.8863),
    "Austin": (30.2672, -97.7431),
    "奥斯汀": (30.2672, -97.7431),
    "Miami": (25.7617, -80.1918),
    "迈阿密": (25.7617, -80.1918),
    "Seattle": (47.6062, -122.3321),
    "西雅图": (47.6062, -122.3321),
    "San Francisco": (37.7749, -122.4194),
    "旧金山": (37.7749, -122.4194),
    "Las Vegas": (36.1699, -115.1398),
    "拉斯维加斯": (36.1699, -115.1398),
    "Washington": (38.9072, -77.0369),
    "华盛顿": (38.9072, -77.0369),
    "Boston": (42.3601, -71.0589),
    "波士顿": (42.3601, -71.0589),
    
    # === 德国城市 ===
    "Berlin": (52.5200, 13.4050),
    "柏林": (52.5200, 13.4050),
    "Munich": (48.1351, 11.5820),
    "慕尼黑": (48.1351, 11.5820),
    "Hamburg": (53.5511, 9.9937),
    "汉堡": (53.5511, 9.9937),
    "Cologne": (50.9375, 6.9603),
    "科隆": (50.9375, 6.9603),
    "Frankfurt": (50.1109, 8.6821),
    "法兰克福": (50.1109, 8.6821),
    "Stuttgart": (48.7758, 9.1829),
    "斯图加特": (48.7758, 9.1829),
    "Dusseldorf": (51.2277, 6.7735),
    "杜塞尔多夫": (51.2277, 6.7735),
    "Dortmund": (51.5136, 7.4653),
    "多特蒙德": (51.5136, 7.4653),
    
    # === 英国城市 ===
    "London": (51.5074, -0.1278),
    "伦敦": (51.5074, -0.1278),
    "Manchester": (53.4808, -2.2426),
    "曼彻斯特": (53.4808, -2.2426),
    "Birmingham": (52.4862, -1.8904),
    "伯明翰": (52.4862, -1.8904),
    "Liverpool": (53.4084, -2.9916),
    "利物浦": (53.4084, -2.9916),
    "Edinburgh": (55.9533, -3.1883),
    "爱丁堡": (55.9533, -3.1883),
    "Glasgow": (55.8642, -4.2518),
    "格拉斯哥": (55.8642, -4.2518),
    
    # === 法国城市 ===
    "Paris": (48.8566, 2.3522),
    "巴黎": (48.8566, 2.3522),
    "Marseille": (43.2965, 5.3698),
    "马赛": (43.2965, 5.3698),
    "Lyon": (45.7640, 4.8357),
    "里昂": (45.7640, 4.8357),
    "Toulouse": (43.6047, 1.4442),
    "图卢兹": (43.6047, 1.4442),
    "Nice": (43.7102, 7.2620),
    "尼斯": (43.7102, 7.2620),
    
    # === 其他主要城市 ===
    "Sydney": (-33.8688, 151.2093),
    "悉尼": (-33.8688, 151.2093),
    "Melbourne": (-37.8136, 144.9631),
    "墨尔本": (-37.8136, 144.9631),
    "Toronto": (43.6532, -79.3832),
    "多伦多": (43.6532, -79.3832),
    "Vancouver": (49.2827, -123.1207),
    "温哥华": (49.2827, -123.1207),
    "Singapore": (1.3521, 103.8198),
    "新加坡": (1.3521, 103.8198),
    "Bangkok": (13.7563, 100.5018),
    "曼谷": (13.7563, 100.5018),
    "Dubai": (25.2048, 55.2708),
    "迪拜": (25.2048, 55.2708),
    "Moscow": (55.7558, 37.6176),
    "莫斯科": (55.7558, 37.6176),
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
            coordinates = CITY_COORDINATES[city_name]
            logger.info(f"📍 使用内置坐标：{city_name} -> {coordinates}")
            return coordinates
        
        if city_name in self.coord_cache:
            return self.coord_cache[city_name]
        
        # 如果没有高德 API，直接返回 None
        if not self.api_key:
            return None
        
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
            logger.info(f"🌤️ 调用彩云天气API：{lat},{lon} 获取{days}天天气数据")
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                logger.info(f"✅ 天气API调用成功：状态 {data.get('status', 'unknown')}")
                return data
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

@mcp.tool()
async def get_user_location_by_ip() -> str:
    """通过IP地址获取用户当前地理位置
    
    当用户没有指定城市时，可以使用此工具自动获取用户所在城市
    """
    try:
        # 使用 ipapi.co 免费服务获取IP定位
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("https://ipapi.co/json/")
            response.raise_for_status()
            
            data = response.json()
            
            # 提取地理位置信息
            country = data.get("country_name", "")
            region = data.get("region", "")
            city = data.get("city", "")
            ip = data.get("ip", "")
            
            # 处理定位结果（支持全球城市）
            if city:
                # 如果是中国城市，尝试匹配已知城市
                if country == "China":
                    matched_city = None
                    city_clean = city.replace("市", "").replace("区", "").replace("县", "")
                    
                    # 先检查是否在支持列表中
                    for supported_city in CITY_COORDINATES.keys():
                        if city_clean in supported_city or supported_city in city_clean:
                            matched_city = supported_city
                            break
                    
                    if matched_city:
                        logger.info(f"🌍 IP定位成功：{country} {city} -> 匹配到 {matched_city}")
                        return f"📍 已自动定位到：{matched_city}\n🌐 您的IP：{ip}\n✅ 将为您查询 {matched_city} 的天气信息"
                    else:
                        logger.info(f"🌍 IP定位成功：{country} {city}（使用原始城市名）")
                        return f"📍 已定位到：{city}\n🌐 您的IP：{ip}\n💡 将尝试查询 {city} 的天气信息"
                else:
                    # 非中国城市，直接使用定位结果
                    logger.info(f"🌍 IP定位成功：{country} {city}（国外城市）")
                    return f"📍 已定位到：{country} {city}\n🌐 您的IP：{ip}\n✅ 将尝试为您查询 {city} 的天气信息"
            else:
                logger.warning(f"🌍 IP定位失败：无法获取城市信息，IP：{ip}")
                return f"📍 无法精确定位城市\n🌐 您的IP：{ip}\n💡 建议手动指定城市名称"
                
    except httpx.HTTPError as e:
        logger.error(f"IP定位服务请求失败: {e}")
        return "❌ IP定位服务暂时不可用，请手动指定城市名称"
    except Exception as e:
        logger.error(f"IP定位失败: {e}")
        return f"❌ 自动定位失败: {str(e)}，请手动指定城市名称"

# 运行服务器
if __name__ == "__main__":
    mcp.run()