# JLPT 日本语文法抽查

## 1. 项目简介

本项目旨在打造一个自动化的日语语法学习推送系统。它能够解析特定格式的日语语法源数据，将其结构化后存储，并定时随机抽取一条语法知识，通过 [Bark](https://bark.day.app/#/tutorial) 推送到 iOS/macOS 设备，帮助用户利用碎片化时间学习和复习 JLPT 语法。

## 2. 主要特性

- **自动化数据转换**: 提供脚本将原始的、复杂的 JSON 数据转换为统一、清晰的结构化格式。
- **模板化内容生成**: 推送内容（标题、正文）基于配置文件中的模板生成，方便自定义。
- **Bark 服务集成**: 轻量化地集成了 Bark 推送服务，配置简单。
- **异步化推送**: 使用 `aiohttp` 进行异步网络请求，高效无阻塞。
- **定时任务调度**: 支持通过 `crontab` 实现无人值守的定时、自动化推送。
- **健壮的日志与配置**: 提供清晰的日志记录和独立的配置文件，易于管理和排错。

## 3. 环境配置与安装

1. **克隆仓库**

   ```bash
   git clone https://github.com/kuhung/jlpt-push.git
   cd jlpt-push
   ```
2. **创建虚拟环境 (推荐UV)**

   ```bash
   uv venv
   source .venv/bin/activate
   ```
3. **安装依赖**

   ```bash
   uv pip install -r requirements.txt
   ```
4. **准备原始数据**
   将你的日语语法源文件 `term_bank_all.json` 放入 `data/raw/` 目录下。
   数据源参考地址：

   - https://github.com/aiko-tanaka/Grammar-Dictionaries
   - https://drive.google.com/drive/folders/127R67ANHycDV8PwonlV6ZUYxdWVu6IQ6

   **建议下载 JLPT 相关数据**，后续数据处理也是依照于此。
5. **配置 Bark Key**
   复制 `config/config_example.yaml`为 `config/config.yaml`文件,编辑 `config.yaml` 文件，将 `key` 的值替换为你自己的 Bark 推送 Key。

   ```yaml
   bark:
     key: YOUR_BARK_KEY # <--- 修改这里
     url: https://api.day.app
   ```

## 4. 使用方法

### 步骤一：转换数据

在推送前，需要先将原始数据进行结构化处理。运行以下命令：

```bash
python src/converter/json_converter.py
```

该脚本会读取 `data/raw/term_bank_all.json`，处理后生成 `data/processed/grammar_bank.json`。

### 步骤二：手动测试推送

运行主脚本以测试单次推送是否成功：

```bash
python run_push.py
```

执行后，请检查你的设备是否收到推送，并查看终端和 `logs/push.log` 中的日志输出。

## 5. 部署 (定时推送)

使用 `crontab` 来实现定时自动推送。

1. **获取绝对路径**

   - Python 解释器路径: `which python3`
   - 项目根目录路径: `pwd` (在 `jlpt-push` 目录下执行)
2. **编辑 Crontab**
   运行 `crontab -e`，并添加以下任务（请务必替换为你的绝对路径）：

   ```crontab
   # 每小时执行一次 JLPT 语法推送
   0 * * * * cd /path/to/your/project/jlpt-push && /path/to/your/python3 run_push.py >> /path/to/your/project/jlpt-push/logs/cron.log 2>&1
   ```

---

## 附：系统设计方案

（此部分为开发过程中的设计文档，可供参考）

### 系统架构

#### 文件结构

```
jlpt-push/
├── data/
│   ├── raw/
│   └── processed/
├── src/
│   ├── converter/
│   ├── pusher/
│   └── utils/
├── config/
├── logs/
├── requirements.txt
├── run_push.py
└── README.md
```

#### 核心模块

- **数据转换模块** (`src/converter`): 处理原始JSON数据。
- **推送模块** (`src/pusher`): 处理Bark推送。
- **内容格式化模块** (`src/utils`): 格式化推送内容。
- **主脚本** (`run_push.py`): 调度和执行整个流程。

### 数据结构设计

- **输入**: `data/raw/term_bank_6.json` (嵌套数组格式)
- **输出**: `data/processed/grammar_bank.json` (结构化对象格式)
  ```json
  {
      "id": "gram_001",
      "title": "...",
      "pattern": "...",
      "meaning": "...",
      "usage": "...",
      "examples": [{"jp": "...", "en": "..."}],
      "source_url": "...",
      "level": "N3"
  }
  ```

### 技术选型

- **核心依赖**: `PyYAML`, `aiohttp`
- **日志**: `logging` (Python 标准库)
- **调度**: `crontab`

### 灵感来源

- [日本語JLPT文法](https://jumble.social/users/npub1xr4jdgh7htsuraq8y34pufv3kc5mz2h9h0r9lv9a9t0xeuctvp6smrfyy8) - 每小时自动发送一条日语文法，包含文法，日文例句及中文翻译。
