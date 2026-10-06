# 🧪 小学科学 · 每日前沿拓展推送

面向小学 4-6 年级科学课堂的每日科技新闻拓展素材。每天早上自动生成网页并推送到微信，**电脑不开机也照常运行**（全部在 GitHub 云端定时执行，本地没有任何任务，不会重复推送）。

## 每天你会收到什么

微信里收到一条推送卡片，点开是当天的网页，包含约 5 条新闻，每条有：

- 通俗标题 + 讲给小学生听的摘要
- 解读（这件事是什么、为什么重要）
- 对应教材知识点（如 六上《工具与技术》、四下《电路》）
- **原文链接**（防杜撰，AI 给出的链接会与抓取结果比对，对不上就丢弃）
- 好用程度 ★~★★★★★，好用的排前面

## 一次性配置（约 20 分钟）

### 1. 注册 GitHub 并建仓库
1. 到 https://github.com 注册（免费）
2. 新建一个**公开**仓库，名字如 `sci-daily`
3. 把本文件夹里的所有内容上传到仓库（网页拖拽上传即可，注意 `.github` 文件夹也要传）

### 2. 开启 GitHub Pages（免费托管网页）
1. 仓库页面 → Settings → Pages
2. Source 选 `Deploy from a branch`，分支 `main`，目录 `/ (root)`
3. 保存后等一两分钟，网页地址为 `https://你的用户名.github.io/sci-daily/`

### 3. 拿智谱 API Key（免费，AI 解读用）
1. 到 https://open.bigmodel.cn 注册并实名
2. 右上角头像 → API Keys → 创建，复制保存

### 4. 拿 PushPlus Token（免费，微信推送用）
1. 微信关注公众号 **pushplus 推送加**
2. 登录 https://www.pushplus.plus ，首页即可看到你的 token

### 5. 配置 Secrets
仓库 → Settings → Secrets and variables → Actions → New repository secret，添加三个：

| Name | Value |
|---|---|
| `ZHIPU_API_KEY` | 第 3 步的 Key |
| `PUSHPLUS_TOKEN` | 第 4 步的 token |
| `SITE_URL` | 第 2 步的网页地址 |

### 6. 试运行一次
仓库 → Actions → 每日科学推送 → Run workflow → 手动点一次。跑完后微信应收到推送，网页也会更新。

## 日常使用

之后**什么都不用管**：每天北京时间约 06:50 自动运行，07 点左右微信收到推送。网页首页永远是最新一期，`/archive.html` 可看全部历史。

## 想调整时

- **推送时间**：改 `.github/workflows/daily.yml` 里的 cron（UTC 时间，北京时间 = UTC + 8）
- **条数**：workflow 里 curate 步骤加环境变量 `NEWS_COUNT: 8`
- **新闻源**：改 `scripts/fetch_news.py` 顶部的 `SOURCES` 列表
- **AI 模型**：默认 `glm-4-flash`（免费），可改环境变量 `GLM_MODEL`

## 目录结构

```
.github/workflows/daily.yml  # 云端定时任务
scripts/fetch_news.py        # 抓取 RSS（科普中国/人民网/果壳/NASA/ScienceDaily…）
scripts/curate.py            # GLM 筛选+解读+分级+链接校验
scripts/build_page.py        # 生成网页（首页/日期页/归档页）
scripts/push.py              # PushPlus 微信推送 + 去重记录
site/                        # 生成的网页
data/                        # 中间数据与去重记录
```

## 为什么不会重复推送

- 本地电脑零任务，定时只在 GitHub Actions 跑一处
- `data/pushed_dates.json` 保证同一日期只推一次；`pushed_links.json` 保证同一新闻不再出现
