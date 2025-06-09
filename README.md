# JLPT 日语语法推送系统

## 一、系统架构

### 1. 文件结构

```
jlpt-push/
├── data/
│   ├── raw/                 # 原始数据
│   │   └── term_bank_6.json
│   └── processed/           # 处理后的数据
│       └── grammar_bank.json
├── src/
│   ├── converter/          # 数据转换模块
│   │   ├── __init__.py
│   │   └── json_converter.py
│   ├── pusher/            # 推送模块
│   │   ├── __init__.py
│   │   └── bark_pusher.py
│   └── utils/             # 工具模块
│       ├── __init__.py
│       └── content_formatter.py
├── config/
│   └── config.yaml        # 配置文件（bark key等）
├── logs/                  # 日志目录
├── requirements.txt       # 依赖
└── README.md             # 项目说明
```

### 2. 核心模块

- **数据转换模块**：处理原始JSON数据
- **推送模块**：处理Bark推送
- **工具模块**：格式化内容、日志等

## 二、详细设计

### 1. 数据结构设计

#### 输入数据结构（原始）

```json
[
    [
        "すぎです",
        "すぎです",
        "・〜すぎです",
        "",
        0,
        [...],
        0,
        "日本語NET"
    ]
]
```

#### 输出数据结构（处理后）

```json
{
    "version": "1.0",
    "updated_at": "2024-xx-xx",
    "grammar": [
        {
            "id": "gram_001",
            "title": "すぎです",
            "pattern": "・〜すぎです",
            "meaning": "...",
            "usage": "...",
            "examples": [
                {
                    "jp": "...",
                    "en": "..."
                }
            ],
            "source": "...",
            "level": "N3",
            "tags": ["基础语法", "程度"]
        }
    ]
}
```

### 2. 模块设计

#### 2.1 数据转换模块 (converter)

```python
class GrammarConverter:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
  
    def convert(self, raw_data: List) -> Dict:
        """转换原始数据到标准格式"""
        pass

    def extract_examples(self, content: str) -> List[Dict]:
        """提取例句"""
        pass
```

#### 2.2 推送模块 (pusher)

```python
class BarkPusher:
    def __init__(self, config: Dict):
        self.api_key = config['bark_key']
        self.base_url = config['bark_url']
        self.logger = logging.getLogger(__name__)

    async def push(self, content: Dict) -> bool:
        """推送内容到Bark"""
        pass
```

#### 2.3 内容格式化模块 (formatter)

```python
class ContentFormatter:
    @staticmethod
    def format_grammar(grammar: Dict) -> str:
        """格式化语法内容"""
        pass

    @staticmethod
    def format_examples(examples: List[Dict]) -> str:
        """格式化例句"""
        pass
```

### 3. 配置设计 (config.yaml)

```yaml
bark:
  key: YOUR_BARK_KEY
  url: https://api.day.app

push:
  interval: 3600  # 推送间隔（秒）
  format:
    title_template: "【JLPT语法】{title}"
    body_template: "用法：{usage}\n意义：{meaning}\n例句：{example}"

logging:
  level: INFO
  file: logs/app.log
```

## 三、技术选型

### 1. 核心依赖

- **PyYAML**: 配置文件处理
- **aiohttp**: 异步HTTP请求
- **loguru**: 日志处理
- **pydantic**: 数据验证
- **click**: CLI工具

### 2. 开发工具

- **black**: 代码格式化
- **pylint**: 代码检查
- **pytest**: 单元测试

## 四、实现步骤

1. **环境搭建**

   - 创建项目结构
   - 配置依赖管理
2. **数据转换实现**

   - 实现数据解析
   - 实现数据转换
   - 数据验证和测试
3. **推送模块实现**

   - Bark接口封装
   - 内容格式化
   - 推送逻辑实现
4. **调度实现**

   - crontab配置
   - 错误处理
   - 日志记录
5. **测试和部署**

   - 单元测试
   - 集成测试
   - 部署文档

## 五、后续优化方向

1. **数据增强**

   - 添加更多语法数据源
   - 支持多级别筛选
2. **推送优化**

   - 支持多推送渠道
   - 支持推送历史记录
   - 支持推送效果统计
3. **用户体验**

   - 添加Web管理界面
   - 支持自定义推送模板
   - 支持推送时间自定义
