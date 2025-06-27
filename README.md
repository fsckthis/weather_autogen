# AutoGen 多代理协作天气查询系统

基于 Microsoft AutoGen 框架的多代理协作天气查询系统，支持智能IP定位。

## 🌟 项目特色

- 🧠 **意图解析代理** - 分析用户查询意图，提取城市和时间信息
- 🌤️ **天气查询代理** - 调用天气 API 获取数据，支持自动IP定位
- ✨ **响应格式化代理** - 格式化输出并提供生活建议
- 🎯 **多代理协作** - 三个代理协作完成查询任务
- 📍 **智能定位** - 用户无需指定城市，自动通过IP获取地理位置

## 📁 项目结构

```plain
weather_autogen/
├── src/                 # 核心源代码
│   ├── weather_team.py  # 多代理协作管理器
│   ├── weather_agents.py# 代理定义和 MCP 工具集成
│   └── weather_cli.py   # 命令行界面
├── mcp_server/          # MCP 服务器
│   └── weather_mcp_server.py # 彩云天气MCP服务器(支持IP定位)
├── tests/               # 测试套件
├── requirements.txt     # 依赖包
└── README.md           # 项目文档
```

## 🚀 快速开始

### 1. 进入项目目录

```bash
cd mcp/weather_autogen
```

### 2. 激活虚拟环境（如果还没有）

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
source .venv/bin/activate  # macOS/Linux
# 或 .venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 设置 API 密钥

```bash
# 复制配置模板
cp .env.example .env.local

# 编辑 .env.local 文件，填入API密钥：
# OPENAI_API_KEY=your-openai-api-key
# CAIYUN_API_KEY=your-caiyun-api-key
```

### 5. 运行天气查询系统

```bash
# 推荐：简洁的命令行界面
python src/weather_cli.py

# 直接查询（支持IP自动定位）
python src/weather_cli.py "今天天气怎么样"

# 演示模式
python src/weather_cli.py --demo

# 多代理协作演示（详细日志）
python src/weather_team.py
```

## 🎭 多代理协作流程

```mermaid
graph LR
    A[用户查询] --> B[意图解析代理]
    B --> C[天气查询代理] 
    C --> D[响应格式化代理]
    D --> E[最终回复]
```

### 协作示例

**用户输入**：`"上海明天天气"`

1. 🧠 **意图解析代理**：

   ```plain
   城市：上海
   时间：tomorrow
   查询：查询上海明天的天气
   ```

2. 🌤️ **天气查询代理**：

   ```plain
   调用 query_weather_tomorrow("上海")
   获取天气数据
   ```

3. ✨ **响应格式化代理**：

   ```plain
   美化输出 + 添加生活建议
   ```

## 🎯 支持的查询类型

| 查询类型 | 示例           | 特殊功能 | 代理协作流程     |
| -------- | -------------- | -------- | ---------------- |
| 今日天气 | "今天天气"     | IP自动定位 | 解析→定位→查询→格式化 |
| 明日天气 | "明天会下雨吗" | IP自动定位 | 解析→定位→查询→格式化 |
| 未来天气 | "未来三天天气" | IP自动定位 | 解析→定位→查询→格式化 |
| 城市指定 | "北京明天天气" | 直接查询 | 解析→查询→格式化 |
| 城市指定 | "上海今天天气" | 直接查询 | 解析→查询→格式化 |

### 🆕 智能IP定位功能

当用户查询**没有明确指定城市**时，系统会：
1. 自动通过IP地址获取用户地理位置
2. 智能匹配到支持的中国城市
3. 为非中国地区提供友好提示

## 🛠️ 技术架构

### 核心组件

- **WeatherAgentTeam**: 多代理协作管理器
- **意图解析代理**: 分析用户查询意图
- **天气查询代理**: 通过 MCP 协议调用天气工具
- **响应格式化代理**: 格式化输出结果

### MCP 工具函数

- `query_weather_today(city)` - 查询今天天气
- `query_weather_tomorrow(city)` - 查询明天天气
- `query_weather_future_days(city, days)` - 查询未来几天天气
- `get_user_location_by_ip()` - **新增**：通过IP自动获取用户地理位置
- `get_supported_cities()` - 获取支持的城市列表
- `get_city_coordinates(city)` - 获取城市坐标信息

## 🔧 自定义扩展

### 添加新的 agent

```python
def create_new_agent(model_client):
    return AssistantAgent(
        name="new_agent",
        model_client=model_client,
        description="新代理的描述",
        system_message="代理的系统消息..."
    )
```

### 添加新的工具

在 MCP 服务器中添加新的工具，然后 AutoGen 会自动发现并使用。

## 🌈 运行示例

```plain
🤖 初始化天气查询系统...
✅ 系统准备就绪！

🗣️  用户查询: 今天北京天气怎么样
──────────────────────────────────────────────────
🔄 启动多代理协作...
   📋 意图解析代理 → 解析查询意图
   🌤️  天气查询代理 → 获取天气数据
   ✨ 响应格式化代理 → 美化输出结果

📋 查询结果:
根据最新天气预报，北京今天的天气是阴天，气温在27°C到35°C之间...
```

## 🔍 故障排除

### 常见问题

1. **API 密钥未设置**

   ```bash
   export OPENAI_API_KEY='your-api-key-here'
   ```

2. **依赖包问题**

   ```bash
   pip install -r requirements.txt --force-reinstall
   ```

3. **Python 环境问题**

   ```bash
   python --version  # 确保 Python 3.8+
   ```

### 🧪 测试和开发

```bash
# 运行完整测试套件
python tests/run_tests.py

# 测试结果：50/50 (100%) 通过
```

## 📊 项目信息

- **代理数量**: 3 个（意图解析、天气查询、响应格式化）
- **MCP 工具**: 6 个（包含IP定位功能）
- **支持城市**: 37 个中国主要城市 + 全球IP定位
- **技术栈**: AutoGen + MCP + 彩云天气 API + IP定位服务
- **测试覆盖**: 50个测试用例，100%通过率

---
