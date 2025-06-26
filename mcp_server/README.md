# 彩云天气 MCP 服务器

基于 Anthropic MCP Python SDK 实现的天气查询服务器，集成彩云天气真实 API。

## 功能特性

- 🌤️ **真实天气数据** - 集成彩云天气 API
- 🏙️ **支持 37 个城市** - 涵盖中国主要城市
- 📅 **多时间段查询** - 今日、明日、未来几天
- 🎯 **标准 MCP 协议** - 可与 Claude Desktop 等客户端集成
- 💡 **智能生活建议** - 根据天气生成贴心提醒

## 快速开始

### 1. 安装依赖

```bash
# 进入项目根目录
cd ../

# 激活虚拟环境
source venv/bin/activate

# 安装依赖（如果还没安装）
pip install -r requirements.txt
```

### 2. 运行 MCP 服务器

```bash
# 进入 MCP 服务器目录
cd mcp_server

# 启动服务器
python weather_mcp_server.py
```

### 3. 测试 API 功能

```bash
# 测试天气 API（注意频率限制）
python test_weather_api.py
```

## 支持的工具

| 工具名称                    | 描述               | 参数                                       |
| --------------------------- | ------------------ | ------------------------------------------ |
| `query_weather_today`       | 查询今天的天气     | `city` (可选，默认北京)                    |
| `query_weather_tomorrow`    | 查询明天的天气     | `city` (可选，默认北京)                    |
| `query_weather_future_days` | 查询未来几天天气   | `city` (可选)、`days` (1-15 天，默认 3 天) |
| `get_supported_cities`      | 获取支持的城市列表 | 无参数                                     |

## 支持的城市

北京、上海、广州、深圳、杭州、南京、武汉、成都、西安、重庆、天津、苏州、青岛、宁波、无锡、济南、大连、沈阳、长春、哈尔滨、福州、厦门、昆明、南昌、合肥、石家庄、太原、郑州、长沙、南宁、海口、贵阳、兰州、银川、西宁、乌鲁木齐、拉萨

## 注意事项

- ⚠️ **API 频率限制**：彩云天气 API 有调用频率限制，测试时请控制调用频率
- 🔑 **API 密钥**：当前使用的是示例密钥，生产环境请替换为自己的密钥
- 📡 **网络连接**：需要稳定的网络连接访问彩云天气 API
- 🚫 **无降级机制**：API 失败时直接返回错误信息，确保数据真实性

## 集成到 Claude Desktop

将此 MCP 服务器添加到 Claude Desktop 配置中：

```json
{
  "mcpServers": {
    "weather": {
      "command": "python",
      "args": ["/path/to/weather_mcp_server.py"],
      "cwd": "/path/to/mcp_server"
    }
  }
}
```

## 错误处理

- **城市不支持**：返回支持的城市列表
- **API 频率限制**：提示请稍后再试
- **网络错误**：返回具体的错误信息
- **数据格式错误**：返回解析失败提示

## 开发说明

- 基于 `mcp` Python SDK
- 使用 `httpx` 进行 HTTP 请求
- 采用字典映射模式管理工具处理函数
- 完整的异步处理和资源管理
