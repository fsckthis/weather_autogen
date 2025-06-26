# 天级别预报

```bash
curl "https://api.caiyunapp.com/v2.6/TAkhjf8d1nlSlspN/101.6656,39.2072/daily?dailysteps=1"
```

- `dailysteps`: 控制返回多少天的数据，`[1, 15]`

```json
{
  "status": "ok", // 返回状态
  "api_version": "v2.6", // API 版本
  "api_status": "alpha", // API 状态
  "lang": "zh_CN", // 语言
  "unit": "metric", // 单位
  "tzshift": 28800, // 时区偏移
  "timezone": "Asia/Shanghai", // 时区
  "server_time": 1653552787, // 服务器时间
  "location": [
    39.2072, // 纬度
    101.6656 // 经度
  ],
  "result": {
    "daily": {
      "status": "ok",
      "astro": [ // 日出日落时间
        {
          "date": "2022-05-26T00:00+08:00",
          "sunrise": {
            "time": "05:51" // 日出时间
          },
          "sunset": {
            "time": "20:28" // 日落时间
          }
        }
      ],
      "precipitation_08h_20h": [ // 白天降水数据
        {
          "date": "2022-05-26T00:00+08:00",
          "max": 0, // 白天最大降水量
          "min": 0, // 白天最小降水量
          "avg": 0, // 白天平均降水量
          "probability": 0 // 白天降水概率
        }
      ],
      "precipitation_20h_32h": [ // 夜晚降水数据
        {
          "date": "2022-05-26T00:00+08:00",
          "max": 0, // 夜晚最大降水量
          "min": 0, // 夜晚最小降水量
          "avg": 0, // 夜晚平均降水量
          "probability": 0 // 夜晚降水概率
        }
      ],
      "precipitation": [ // 降水数据
        {
          "date": "2022-05-26T00:00+08:00",
          "max": 0, // 全天最大降水量
          "min": 0, // 全天最小降水量
          "avg": 0, // 全天平均降水量
          "probability": 0 // 全天降水概率
        }
      ],
      "temperature": [ // 全天地表 2 米气温
        {
          "date": "2022-05-26T00:00+08:00",
          "max": 27, // 全天最高气温
          "min": 18, // 全天最低气温
          "avg": 23.75 // 全天平均气温
        }
      ],
      "temperature_08h_20h": [ // 白天地表 2 米气温
        {
          "date": "2022-05-26T00:00+08:00",
          "max": 27, // 白天最高气温
          "min": 18, // 白天最低气温
          "avg": 24.57 // 白天平均气温
        }
      ],
      "temperature_20h_32h": [ // 夜晚地表 2 米气温
        {
          "date": "2022-05-26T00:00+08:00",
          "max": 24.8, // 夜晚最高气温
          "min": 18, // 夜晚最低气温
          "avg": 20.02 // 夜晚平均气温
        }
      ],
      "wind": [ // 全天地表 10 米风速
        {
          "date": "2022-05-26T00:00+08:00",
          "max": {
            "speed": 28.24,
            "direction": 122.62
          },
          "min": {
            "speed": 9,
            "direction": 104
          },
          "avg": {
            "speed": 21.61,
            "direction": 118.02
          }
        }
      ],
      "wind_08h_20h": [ // 白天地表 10 米风速
        {
          "date": "2022-05-26T00:00+08:00",
          "max": {
            "speed": 28.24,
            "direction": 122.62
          },
          "min": {
            "speed": 9,
            "direction": 104
          },
          "avg": {
            "speed": 22.74,
            "direction": 115.78
          }
        }
      ],
      "wind_20h_32h": [ // 夜晚地表 10 米风速
        {
          "date": "2022-05-26T00:00+08:00",
          "max": {
            "speed": 22.39,
            "direction": 97.46
          },
          "min": {
            "speed": 9.73,
            "direction": 125.93
          },
          "avg": {
            "speed": 16,
            "direction": 121.62
          }
        }
      ],
      "humidity": [ // 地表 2 米相对湿度(%)
        {
          "date": "2022-05-26T00:00+08:00",
          "max": 0.18,
          "min": 0.08,
          "avg": 0.09
        }
      ],
      "cloudrate": [ // 云量(0.0-1.0)
        {
          "date": "2022-05-26T00:00+08:00",
          "max": 1,
          "min": 0,
          "avg": 0.75
        }
      ],
      "pressure": [ // 地面气压
        {
          "date": "2022-05-26T00:00+08:00",
          "max": 84500.84,
          "min": 83940.84,
          "avg": 83991.97
        }
      ],
      "visibility": [ // 地表水平能见度
        {
          "date": "2022-05-26T00:00+08:00",
          "max": 25, // 最大能见度
          "min": 24.13, // 最小能见度
          "avg": 25 // 平均能见度
        }
      ],
      "dswrf": [ // 向下短波辐射通量(W/M2)
        {
          "date": "2022-05-26T00:00+08:00",
          "max": 741.9, // 最大辐射通量
          "min": 0, // 最小辐射通量
          "avg": 368.6 // 平均辐射通量
        }
      ],
      "air_quality": {
        "aqi": [
          {
            "date": "2022-05-26T00:00+08:00",
            "max": {
              "chn": 183, // 中国国标 AQI 最大值
              "usa": 160 // 美国国标 AQI 最大值
            },
            "avg": {
              "chn": 29, // 中国国标 AQI 平均值
              "usa": 57 // 美国国标 AQI 平均值
            },
            "min": {
              "chn": 20, // 中国国标 AQI 最小值
              "usa": 42 // 美国国标 AQI 最小值
            }
          }
        ],
        "pm25": [
          {
            "date": "2022-05-26T00:00+08:00",
            "max": 74, // PM2.5 浓度最大值
            "avg": 15, // PM2.5 浓度平均值
            "min": 10 // PM2.5 浓度最小值
          }
        ]
      },
      "skycon": [
        {
          "date": "2022-05-26T00:00+08:00",
          "value": "PARTLY_CLOUDY_DAY" // 全天主要天气现象
        }
      ],
      "skycon_08h_20h": [
        {
          "date": "2022-05-26T00:00+08:00",
          "value": "PARTLY_CLOUDY_DAY" // 白天主要天气现象
        }
      ],
      "skycon_20h_32h": [
        {
          "date": "2022-05-26T00:00+08:00",
          "value": "CLOUDY" // 夜晚主要天气现象
        }
      ],
      "life_index": {
        "ultraviolet": [
          {
            "date": "2022-05-26T00:00+08:00",
            "index": "1",
            "desc": "最弱" // 紫外线指数自然语言
          }
        ],
        "carWashing": [
          {
            "date": "2022-05-26T00:00+08:00",
            "index": "1",
            "desc": "适宜" // 洗车指数自然语言
          }
        ],
        "dressing": [
          {
            "date": "2022-05-26T00:00+08:00",
            "index": "4",
            "desc": "温暖" // 穿衣指数自然语言
          }
        ],
        "comfort": [
          {
            "date": "2022-05-26T00:00+08:00",
            "index": "4",
            "desc": "温暖" // 舒适度指数自然语言
          }
        ],
        "coldRisk": [
          {
            "date": "2022-05-26T00:00+08:00",
            "index": "4",
            "desc": "极易发" // 感冒指数自然语言
          }
        ]
      }
    },
    "primary": 0
  }
}
```

## 字段说明

| JSONPath `$.result.daily.`                       | 说明                                                    |
| ------------------------------------------------ | ------------------------------------------------------- |
| `temperature[max,min,avg]`                       | 全天地表 2 米气温                                       |
| `temperature_08h_20h[max,min,avg]`               | 白天地表 2 米气温                                       |
| `temperature_20h_32h[max,min,avg]`               | 夜晚地表 2 米气温                                       |
| `pressure[max,min,avg]`                          | 地面气压                                                |
| `humidity[max,min,avg]`                          | 地表 2 米相对湿度(%)                                    |
| `wind.speed[max,min,avg]`                        | 全天地表 10 米风速                                      |
| `wind_08h_20h.speed[max,min,avg]`                | 白天地表 10 米风速                                      |
| `wind_20h_32h.speed[max,min,avg]`                | 夜晚地表 10 米风速                                      |
| `precipitation_08h_20h[max,min,avg,probability]` | 白天降水数据                                            |
| `precipitation_20h_32h[max,min,avg,probability]` | 夜晚降水数据                                            |
| `precipitation[max,min,avg,probability]`         | 降水数据                                                |
| `cloudrate[max,min,avg]`                         | 云量(0.0-1.0)                                           |
| `dswrf[max,min,avg]`                             | 向下短波辐射通量(W/M2)                                  |
| `visibility[max,min,avg]`                        | 地表水平能见度                                          |
| `skycon.value`                                   | 全天主要天气现象                                        |
| `skycon_08h_20h.value`                           | 白天主要天气现象                                        |
| `skycon_20h_32h.value`                           | 夜晚主要天气现象                                        |
| `ultraviolet.desc`                               | 紫外线指数自然语言                                      |
| `comfort.desc`                                   | 舒适度指数自然语言                                      |
| `carWashing.desc`                                | 洗车指数自然语言                                        |
| `coldRisk.desc`                                  | 感冒指数自然语言                                        |
| `dressing.desc`                                  | 穿衣指数自然语言                                        |
| `pm25[max,min,avg]`                              | PM2.5 浓度(μg/m3)                                       |
| `aqi[max,min,avg]`                               | 国标 AQI                                                |
| `astro[sunrise,sunset]`                          | 日出日落时间，当地时区的时刻，tzshift 不作用在这个变量) |

对于 `xxx`, `xxx_08h_20h`, `xxx_20h_32h`:

- `xxx` 表示全天，0 时～24 时的
- `xxx_08h_20h` 表示当天 08～20 时
- `xxx_20h_32h` 表示当天 20～次日 08 时的

备注：

- 对于 `xxx.avg`，在当日，表示的是从当前时刻至当天结束的平均值，而不是全天的平均值
