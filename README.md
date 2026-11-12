# 网站内容和样式爬虫

这是一个功能强大的Python爬虫脚本，可以爬取指定网站的内容和样式，并将它们保存到本地，保持原网站的结构和样式。

## 功能特点

- 爬取并保存HTML内容
- 下载并处理CSS样式文件
- 处理CSS中的`@import`引用
- 下载JavaScript文件
- 下载图片、字体和其他媒体资源
- 支持递归爬取（可设置爬取深度）
- 自动处理相对路径
- 支持多线程并发爬取
- 遵守robots.txt规则（可选）
- 详细的日志记录
- 支持禁用SSL证书验证（用于自签名证书的网站）
- 支持爬取子域名的资源文件
- 保留原始网站的目录结构

## 安装依赖

在使用脚本前，需要安装以下Python依赖库：

```bash
pip install requests beautifulsoup4
```

## 使用方法

基本用法：

```bash
python index.py https://example.com
```

### 命令行参数

- `url`：要爬取的网站URL（必需）
- `-o, --output`：指定保存爬取内容的目录（默认为`./scraped_website`）
- `-d, --depth`：设置最大爬取深度（默认为2）
- `-t, --delay`：设置请求之间的延迟，单位为秒（默认为1.0秒）
- `-w, --workers`：设置并发线程数（默认为5）
- `--no-robots`：忽略robots.txt规则
- `--no-ssl-verify`：禁用SSL证书验证（对于自签名证书或证书问题的网站很有用）
- `--clean`：在爬取前清空输出目录（谨慎使用）

### 示例

爬取网站并保存到指定目录：

```bash
python index.py https://example.com -o ./my_website
```

设置爬取深度为3，延迟为0.5秒：

```bash
python index.py https://example.com -d 3 -t 0.5
```

使用10个线程并忽略robots.txt规则：

```bash
python index.py https://example.com -w 10 --no-robots
```

禁用SSL证书验证（适用于证书有问题的网站）：

```bash
python index.py https://example.com --no-ssl-verify
```

在爬取前清空输出目录：

```bash
python index.py https://example.com --clean
```

爬取并充分支持样式：

```bash
python index.py https://example.com --no-ssl-verify --no-robots --clean
```

## 注意事项

1. 请遵守网站的使用条款和法律法规，不要过度爬取网站内容
2. 设置合理的延迟时间，避免对目标网站造成过大负担
3. 某些网站可能有反爬虫措施，可能需要额外处理
4. 爬取大型网站时，请注意设置合理的爬取深度，避免爬取过多内容
5. 使用`--no-ssl-verify`选项时要谨慎，这会降低连接的安全性
6. 使用`--clean`选项会删除输出目录中的所有文件，请谨慎使用

## 输出结构

脚本将在输出目录中创建以下文件夹结构：

```
scraped_website/
├── css/           # 存放CSS文件
├── js/            # 存放JavaScript文件
├── images/        # 存放图片和媒体文件
├── fonts/         # 存放字体文件
└── ...            # 其他按照网站结构组织的HTML文件
```

## 样式支持

本爬虫特别关注网站样式的完整保存：

- 处理CSS文件中的`url()`引用
- 处理CSS中的`@import`引用
- 支持各种格式的字体文件
- 支持内联样式
- 处理跨子域名的资源引用

## 日志

脚本会生成一个名为`网站爬虫.log`的日志文件，记录爬取过程中的详细信息。 