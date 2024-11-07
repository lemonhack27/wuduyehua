from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import time
import subprocess
import os
import sys
from you_get import common as you_get

import requests
from bs4 import BeautifulSoup

def get_links_and_names_from_url(url):
    # 发送 HTTP 请求获取网页内容
    response = requests.get(url)
    if response.status_code != 200:
        print(f"请求失败，状态码: {response.status_code}")
        return {}

    # 解析 HTML 内容
    soup = BeautifulSoup(response.content, 'html.parser')

    # 查找指定 class 的 ul 元素
    ul_element = soup.find('ul', class_="news-list")
    if not ul_element:
        print(f"未找到 class 为 news-list 的 ul 元素")
        return {}

    # 查找 ul 元素下的所有 a 标签
    links_and_names = {}
    for a_tag in ul_element.find_all('a'):
        href = a_tag.get('href')
        name = a_tag.get('title')
        if href and name:
            links_and_names[href] = name

    return links_and_names

def download_video(video_url, output_dir, filename):
    # 将 video_url 强制转换为字符串
    video_url = str(video_url)

    if not video_url:
        print("未找到视频地址")
        return

    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 构建完整的输出路径
    output_path = os.path.join(output_dir, filename)

    # 使用 you-get 下载视频并指定输出路径
    try:
        result = subprocess.run(
            ['you-get', '-o', output_dir, '-O', filename, video_url],
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8'  # 显式指定编码为 utf-8
        )
    except subprocess.CalledProcessError as e:
        print(f"下载失败: {e}")
        print(f"错误输出: {e.stderr}")
    else:
        print("下载成功")
        print(f"输出: {result.stdout}")


def get_video_url(url):
    # 设置 Edge 选项
    edge_options = Options()
    edge_options.add_argument("--headless")  # 无头模式，不打开浏览器窗口
    edge_options.add_argument("--disable-gpu")
    edge_options.add_argument("--no-sandbox")

    # 初始化 WebDriver
    service = Service(EdgeChromiumDriverManager().install())
    driver = webdriver.Edge(service=service, options=edge_options)

    try:
        # 打开目标网页
        driver.get(url)

        # 等待页面加载完成，可以根据实际情况调整等待时间
        time.sleep(1)

        # 查找视频元素
        video_element = driver.find_element(By.TAG_NAME, 'video')
        if video_element:
            video_url = video_element.get_attribute('src')
        else:
            video_url = None
    finally:
        # 关闭浏览器
        driver.quit()
    return video_url

if __name__ == '__main__':
    # 示例使用
    print("请输入需要下载的页码:start_page,end_page")
    start_page,end_page = map(int,input().split(','))
    start_url = f'https://www.cbg.cn/list/4904/{start_page}.html'
    end_url = f'https://www.cbg.cn/list/4904/{end_page}.html'
    for i in range(start_page,end_page+1):
        url = f'https://www.cbg.cn/list/4904/{i}.html'
        links_and_names = get_links_and_names_from_url(url)
        for link, name in links_and_names.items():
            video_url = get_video_url(link)
            download_video(video_url,'F:/python',name)
