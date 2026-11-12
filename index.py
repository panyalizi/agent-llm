#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网站内容和样式爬虫
该脚本可以爬取指定网站的内容和样式，并将它们保存到本地。
"""

import os
import requests
from bs4 import BeautifulSoup
import urllib.parse
import re
import time
from urllib.robotparser import RobotFileParser
import logging
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import ssl
import warnings

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("网站爬虫.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 自定义URL验证函数，替代validators模块
def is_valid_url(url):
    """检查URL是否有效"""
    try:
        result = urllib.parse.urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

class WebsiteScraper:
    """网站爬虫类，用于爬取网站内容和样式"""
    
    def __init__(self, base_url, output_dir='./scraped_website', max_depth=2, delay=1, threads=5, respect_robots=True, verify_ssl=True):
        """
        初始化爬虫
        
        参数:
            base_url (str): 要爬取的网站URL
            output_dir (str): 保存爬取内容的目录
            max_depth (int): 最大爬取深度
            delay (float): 请求之间的延迟（秒）
            threads (int): 并发线程数
            respect_robots (bool): 是否遵守robots.txt规则
            verify_ssl (bool): 是否验证SSL证书
        """
        self.base_url = base_url
        self.base_domain = urllib.parse.urlparse(base_url).netloc
        # 提取顶级域名，用于允许跨子域名爬取
        self.top_domain = '.'.join(self.base_domain.split('.')[-2:]) if len(self.base_domain.split('.')) > 1 else self.base_domain
        self.output_dir = output_dir
        self.max_depth = max_depth
        self.delay = delay
        self.threads = threads
        self.respect_robots = respect_robots
        self.verify_ssl = verify_ssl
        
        # 已爬取的URL集合
        self.visited_urls = set()
        
        # 设置请求头，模拟浏览器
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'css'), exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'js'), exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'images'), exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'fonts'), exist_ok=True)  # 添加字体目录
        
        # 解析robots.txt
        self.rp = None
        self.robots_can_fetch = True
        if self.respect_robots:
            self.rp = RobotFileParser()
            robots_url = urllib.parse.urljoin(base_url, '/robots.txt')
            self.rp.set_url(robots_url)
            try:
                if not self.verify_ssl:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        self.rp.read()
                else:
                    self.rp.read()
                logger.info(f"已读取 robots.txt: {robots_url}")
            except Exception as e:
                logger.warning(f"无法读取 robots.txt: {e}")
                # 无法读取robots.txt时，默认允许爬取
                self.robots_can_fetch = True
    
    def is_allowed(self, url):
        """检查是否允许爬取指定URL"""
        if not self.respect_robots or self.rp is None:
            return True
        try:
            return self.rp.can_fetch("*", url)
        except:
            # 如果robots.txt解析失败，则允许爬取
            return self.robots_can_fetch
    
    def normalize_url(self, url, base_url=None):
        """标准化URL"""
        if base_url is None:
            base_url = self.base_url
            
        # 处理相对URL
        if not url.startswith(('http://', 'https://')):
            url = urllib.parse.urljoin(base_url, url)
            
        # 移除URL片段标识符
        url = url.split('#')[0]
        
        # 如果URL包含查询参数，默认保留它们
        
        return url
    
    def is_same_domain(self, url):
        """检查URL是否属于同一域名或子域名"""
        # 如果是javascript链接等特殊情况，直接返回False
        if url.startswith(('javascript:', 'mailto:', 'tel:')):
            return False
            
        parsed_url = urllib.parse.urlparse(url)
        
        # 检查是否是相对URL
        if parsed_url.netloc == '':
            return True
            
        # 检查是否是相同的域名
        if parsed_url.netloc == self.base_domain:
            return True
            
        # 检查是否是子域名
        if self.top_domain in parsed_url.netloc:
            # 只处理CSS、JS、图片和字体资源，不爬取其他子域名的HTML
            path = parsed_url.path.lower()
            resource_extensions = ['.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.woff', '.woff2', '.ttf', '.eot']
            for ext in resource_extensions:
                if path.endswith(ext):
                    return True
                    
        return False
    
    def should_download(self, url):
        """确定是否应该下载该URL的内容"""
        # 排除一些常见的不需要的文件类型
        excluded_extensions = ['.pdf', '.zip', '.rar', '.exe', '.mp3', '.mp4', '.avi', '.mov']
        
        for ext in excluded_extensions:
            if url.lower().endswith(ext):
                return False
                
        return True
    
    def download_file(self, url, output_path):
        """下载文件并保存到指定路径"""
        if not self.is_allowed(url):
            logger.warning(f"根据robots.txt规则，不允许爬取: {url}")
            return False
            
        if not self.should_download(url):
            logger.info(f"跳过下载: {url} (文件类型被排除)")
            return False
            
        try:
            response = requests.get(url, headers=self.headers, timeout=10, verify=self.verify_ssl)
            response.raise_for_status()
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 保存文件
            with open(output_path, 'wb') as f:
                f.write(response.content)
                
            logger.info(f"已下载: {url} -> {output_path}")
            return True
        except Exception as e:
            logger.error(f"下载失败 {url}: {e}")
            return False
    
    def process_css(self, css_content, css_url):
        """处理CSS文件中的URL并下载相关资源"""
        if not css_content:
            return css_content
        
        # 查找CSS中的URL
        url_pattern = re.compile(r'url\([\'"]?(.*?)[\'"]?\)')
        img_urls = url_pattern.findall(css_content)
        
        # 查找CSS中的@import
        import_pattern = re.compile(r'@import\s+[\'"]([^\'"]+)[\'"]')
        import_urls = import_pattern.findall(css_content)
        
        # 处理@import的CSS
        for import_url in import_urls:
            # 构建完整URL
            full_import_url = urllib.parse.urljoin(css_url, import_url)
            
            # 如果不在允许的域名范围内，跳过
            if not self.is_same_domain(full_import_url):
                continue
            
            # 构建本地保存路径
            parsed_url = urllib.parse.urlparse(full_import_url)
            local_path = os.path.join(self.output_dir, 'css', os.path.basename(parsed_url.path))
            
            # 下载导入的CSS文件
            if self.download_file(full_import_url, local_path):
                # 读取CSS内容并处理其中的URL
                try:
                    with open(local_path, 'r', encoding='utf-8', errors='ignore') as f:
                        imported_css_content = f.read()
                    
                    # 处理导入的CSS中的URL
                    processed_imported_css = self.process_css(imported_css_content, full_import_url)
                    
                    # 保存处理后的导入CSS
                    with open(local_path, 'w', encoding='utf-8') as f:
                        f.write(processed_imported_css)
                    
                    # 更新CSS中的导入语句
                    relative_path = os.path.relpath(local_path, os.path.dirname(os.path.join(self.output_dir, 'css')))
                    css_content = css_content.replace(f'@import "{import_url}"', f'@import "{relative_path}"')
                    css_content = css_content.replace(f"@import '{import_url}'", f"@import '{relative_path}'")
                except Exception as e:
                    logger.error(f"处理导入的CSS文件失败 {full_import_url}: {e}")
        
        # 替换和下载CSS中的URL资源
        for img_url in img_urls:
            # 跳过数据URI
            if img_url.startswith('data:'):
                continue
                
            # 构建完整URL
            full_img_url = urllib.parse.urljoin(css_url, img_url)
            
            # 如果不在允许的域名范围内，跳过
            if not self.is_same_domain(full_img_url):
                continue
                
            # 确定资源类型
            path = urllib.parse.urlparse(full_img_url).path.lower()
            if path.endswith(('.woff', '.woff2', '.ttf', '.eot')):
                # 字体文件
                resource_dir = 'fonts'
            elif path.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg')):
                # 图片文件
                resource_dir = 'images'
            else:
                # 其他资源
                resource_dir = 'images'
            
            # 构建本地保存路径
            parsed_url = urllib.parse.urlparse(full_img_url)
            filename = os.path.basename(parsed_url.path)
            if not filename:  # 如果文件名为空，使用一个默认名
                filename = 'resource_' + str(hash(full_img_url))
            local_path = os.path.join(self.output_dir, resource_dir, filename)
            
            # 下载资源
            self.download_file(full_img_url, local_path)
            
            # 在CSS中替换URL为本地路径
            try:
                relative_path = os.path.relpath(local_path, os.path.dirname(os.path.join(self.output_dir, 'css')))
                # 替换原始URL
                css_content = css_content.replace(f'url({img_url})', f'url({relative_path})')
                css_content = css_content.replace(f'url("{img_url}")', f'url("{relative_path}")')
                css_content = css_content.replace(f"url('{img_url}')", f"url('{relative_path}')")
            except Exception as e:
                logger.error(f"替换CSS中的URL失败 {img_url}: {e}")
            
        return css_content
    
    def process_html(self, html_content, page_url, depth=0):
        """处理HTML内容，下载相关资源并保存修改后的HTML"""
        if depth > self.max_depth:
            return html_content
            
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 处理CSS文件
        for link in soup.find_all('link'):
            if not 'href' in link.attrs:
                continue
                
            # 只处理样式表
            if 'rel' in link.attrs and 'stylesheet' in link['rel']:
                css_url = self.normalize_url(link['href'], page_url)
                
                # 如果不在允许的域名范围内，跳过
                if not self.is_same_domain(css_url):
                    continue
                    
                # 构建本地保存路径
                parsed_url = urllib.parse.urlparse(css_url)
                filename = os.path.basename(parsed_url.path)
                if not filename:  # 如果文件名为空，使用URL的哈希值
                    filename = 'style_' + str(hash(css_url)) + '.css'
                local_path = os.path.join(self.output_dir, 'css', filename)
                
                # 下载CSS文件
                if self.download_file(css_url, local_path):
                    # 读取CSS内容并处理其中的URL
                    try:
                        with open(local_path, 'r', encoding='utf-8', errors='ignore') as f:
                            css_content = f.read()
                        
                        # 处理CSS中的URL
                        processed_css = self.process_css(css_content, css_url)
                        
                        # 保存处理后的CSS
                        with open(local_path, 'w', encoding='utf-8') as f:
                            f.write(processed_css)
                        
                        # 更新HTML中的链接
                        relative_path = os.path.relpath(local_path, self.output_dir)
                        link['href'] = relative_path
                    except Exception as e:
                        logger.error(f"处理CSS文件失败 {css_url}: {e}")
        
        # 处理内联样式
        for style in soup.find_all('style'):
            if style.string:
                style.string = self.process_css(style.string, page_url)
        
        # 处理JavaScript文件
        for script in soup.find_all('script', src=True):
            js_url = self.normalize_url(script['src'], page_url)
            
            # 如果不在允许的域名范围内，跳过
            if not self.is_same_domain(js_url):
                continue
                
            # 构建本地保存路径
            parsed_url = urllib.parse.urlparse(js_url)
            filename = os.path.basename(parsed_url.path)
            if not filename:  # 如果文件名为空，使用URL的哈希值
                filename = 'script_' + str(hash(js_url)) + '.js'
            local_path = os.path.join(self.output_dir, 'js', filename)
            
            # 下载JavaScript文件
            if self.download_file(js_url, local_path):
                # 更新HTML中的链接
                relative_path = os.path.relpath(local_path, self.output_dir)
                script['src'] = relative_path
        
        # 处理图片
        for img in soup.find_all('img', src=True):
            img_url = self.normalize_url(img['src'], page_url)
            
            # 如果不在允许的域名范围内，跳过
            if not self.is_same_domain(img_url):
                continue
                
            # 构建本地保存路径
            parsed_url = urllib.parse.urlparse(img_url)
            filename = os.path.basename(parsed_url.path)
            if not filename:  # 如果文件名为空，使用URL的哈希值
                filename = 'image_' + str(hash(img_url)) + '.png'
            local_path = os.path.join(self.output_dir, 'images', filename)
            
            # 下载图片
            if self.download_file(img_url, local_path):
                # 更新HTML中的链接
                relative_path = os.path.relpath(local_path, self.output_dir)
                img['src'] = relative_path
        
        # 处理页面中的链接
        if depth < self.max_depth:
            links_to_crawl = []
            
            for a in soup.find_all('a', href=True):
                link_url = self.normalize_url(a['href'], page_url)
                
                # 跳过特殊URL
                if link_url.startswith(('javascript:', 'mailto:', 'tel:')):
                    continue
                
                # 如果链接已经访问过或不是同一域名，跳过
                if link_url in self.visited_urls or not self.is_same_domain(link_url):
                    continue
                    
                # 将链接加入待爬取列表
                links_to_crawl.append((link_url, depth + 1))
                
                # 更新HTML中的链接（相对路径）
                parsed_url = urllib.parse.urlparse(link_url)
                local_path = os.path.join(self.output_dir, parsed_url.path.lstrip('/'))
                if not local_path.endswith('.html'):
                    if local_path.endswith('/'):
                        local_path += 'index.html'
                    else:
                        local_path += '.html'
                
                relative_path = os.path.relpath(local_path, self.output_dir)
                a['href'] = relative_path
                
            # 多线程爬取链接
            with ThreadPoolExecutor(max_workers=self.threads) as executor:
                future_to_url = {
                    executor.submit(self.crawl_url, url, depth): url 
                    for url, depth in links_to_crawl
                }
                
                for future in as_completed(future_to_url):
                    url = future_to_url[future]
                    try:
                        future.result()
                    except Exception as e:
                        logger.error(f"爬取 {url} 时出错: {e}")
        
        return str(soup)
    
    def crawl_url(self, url, depth=0):
        """爬取指定URL的内容"""
        # 跳过不支持的协议
        if url.startswith(('javascript:', 'mailto:', 'tel:')):
            logger.info(f"跳过不支持的URL协议: {url}")
            return
            
        if url in self.visited_urls:
            return
            
        self.visited_urls.add(url)
        
        if not self.is_allowed(url):
            logger.warning(f"根据robots.txt规则，不允许爬取: {url}")
            return
            
        logger.info(f"爬取 (深度 {depth}): {url}")
        
        # 添加延迟
        time.sleep(self.delay)
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10, verify=self.verify_ssl)
            response.raise_for_status()
            
            # 检查内容类型
            content_type = response.headers.get('Content-Type', '')
            
            # 处理CSS文件
            if 'text/css' in content_type:
                parsed_url = urllib.parse.urlparse(url)
                filename = os.path.basename(parsed_url.path)
                if not filename:
                    filename = 'style_' + str(hash(url)) + '.css'
                local_path = os.path.join(self.output_dir, 'css', filename)
                
                # 保存CSS文件
                with open(local_path, 'wb') as f:
                    f.write(response.content)
                
                # 处理CSS内容
                with open(local_path, 'r', encoding='utf-8', errors='ignore') as f:
                    css_content = f.read()
                
                processed_css = self.process_css(css_content, url)
                
                # 保存处理后的CSS
                with open(local_path, 'w', encoding='utf-8') as f:
                    f.write(processed_css)
                
                logger.info(f"已保存CSS: {url} -> {local_path}")
                return
            
            # 处理JavaScript文件
            if 'application/javascript' in content_type or 'text/javascript' in content_type:
                parsed_url = urllib.parse.urlparse(url)
                filename = os.path.basename(parsed_url.path)
                if not filename:
                    filename = 'script_' + str(hash(url)) + '.js'
                local_path = os.path.join(self.output_dir, 'js', filename)
                
                # 保存JavaScript文件
                with open(local_path, 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"已保存JavaScript: {url} -> {local_path}")
                return
                
            # 处理字体文件
            if any(content_type.startswith(x) for x in ['font/', 'application/font']):
                parsed_url = urllib.parse.urlparse(url)
                filename = os.path.basename(parsed_url.path)
                if not filename:
                    filename = 'font_' + str(hash(url))
                local_path = os.path.join(self.output_dir, 'fonts', filename)
                
                # 保存字体文件
                with open(local_path, 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"已保存字体: {url} -> {local_path}")
                return
                
            # 处理图片文件
            if content_type.startswith('image/'):
                parsed_url = urllib.parse.urlparse(url)
                filename = os.path.basename(parsed_url.path)
                if not filename:
                    ext = content_type.split('/')[-1]
                    filename = 'image_' + str(hash(url)) + '.' + ext
                local_path = os.path.join(self.output_dir, 'images', filename)
                
                # 保存图片文件
                with open(local_path, 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"已保存图片: {url} -> {local_path}")
                return
            
            # 只处理HTML内容
            if 'text/html' not in content_type and 'text/plain' not in content_type:
                logger.info(f"跳过非HTML内容: {url} (Content-Type: {content_type})")
                return
                
            # 处理HTML内容
            html_content = response.text
            processed_html = self.process_html(html_content, url, depth)
            
            # 保存处理后的HTML
            parsed_url = urllib.parse.urlparse(url)
            path_parts = parsed_url.path.lstrip('/').split('/')
            
            # 保持原始的URL路径结构
            if not path_parts or path_parts[0] == '':
                # 默认名为index.html
                local_path = os.path.join(self.output_dir, 'index.html')
            else:
                # 保持路径结构
                local_path = os.path.join(self.output_dir, *path_parts)
                
            # 处理目录URL和无文件扩展名的URL
            if local_path.endswith('/') or not os.path.splitext(local_path)[1]:
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                if local_path.endswith('/'):
                    local_path += 'index.html'
                else:
                    # 检查路径是否已存在作为目录
                    if os.path.isdir(local_path):
                        local_path = os.path.join(local_path, 'index.html')
                    else:
                        local_path += '.html'
            else:
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            # 写入处理后的HTML
            with open(local_path, 'w', encoding='utf-8') as f:
                f.write(processed_html)
                
            logger.info(f"已保存: {url} -> {local_path}")
            
        except Exception as e:
            logger.error(f"爬取失败 {url}: {e}")
    
    def start(self):
        """开始爬取网站"""
        logger.info(f"开始爬取网站: {self.base_url}")
        logger.info(f"保存到目录: {self.output_dir}")
        logger.info(f"最大深度: {self.max_depth}")
        logger.info(f"SSL验证: {'启用' if self.verify_ssl else '禁用'}")
        
        # 开始爬取
        start_time = time.time()
        self.crawl_url(self.base_url)
        end_time = time.time()
        
        logger.info(f"爬取完成！共爬取 {len(self.visited_urls)} 个URL，耗时 {end_time - start_time:.2f} 秒")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='网站内容和样式爬虫')
    parser.add_argument('url', help='要爬取的网站URL')
    parser.add_argument('-o', '--output', default='./scraped_website', help='保存爬取内容的目录')
    parser.add_argument('-d', '--depth', type=int, default=2, help='最大爬取深度')
    parser.add_argument('-t', '--delay', type=float, default=1.0, help='请求之间的延迟（秒）')
    parser.add_argument('-w', '--workers', type=int, default=5, help='并发线程数')
    parser.add_argument('--no-robots', action='store_true', help='忽略robots.txt规则')
    parser.add_argument('--no-ssl-verify', action='store_true', help='禁用SSL证书验证')
    parser.add_argument('--clean', action='store_true', help='在开始爬取前清空输出目录')
    
    args = parser.parse_args()
    
    # 如果禁用SSL验证，添加警告过滤器
    if args.no_ssl_verify:
        # 禁用SSL警告
        warnings.filterwarnings("ignore", message="Unverified HTTPS request")
    
    # 验证URL
    if not is_valid_url(args.url):
        logger.error(f"无效的URL: {args.url}")
        return
    
    # 如果需要，清空输出目录
    if args.clean and os.path.exists(args.output):
        import shutil
        try:
            shutil.rmtree(args.output)
            logger.info(f"已清空输出目录: {args.output}")
        except Exception as e:
            logger.warning(f"清空输出目录失败: {e}")
    
    # 创建爬虫对象并开始爬取
    scraper = WebsiteScraper(
        base_url=args.url,
        output_dir=args.output,
        max_depth=args.depth,
        delay=args.delay,
        threads=args.workers,
        respect_robots=not args.no_robots,
        verify_ssl=not args.no_ssl_verify
    )
    
    scraper.start()

if __name__ == "__main__":
    main()
