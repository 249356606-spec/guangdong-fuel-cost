#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
广东省动力煤价格数据采集脚本
功能：从官方渠道采集CCTD动力煤价格和广州港进口动力煤价格
作者：小小罗
创建时间：2026年6月2日
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import os
import time
from bs4 import BeautifulSoup
import json

class CoalPriceCollector:
    """煤炭价格采集器"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
    def collect_cctd_price(self):
        """采集CCTD动力煤价格"""
        try:
            # 访问CCTD官网
            url = 'https://www.cctd.com.cn'
            response = self.session.get(url, timeout=10)
            response.encoding = 'utf-8'
            
            # 解析页面内容
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取价格信息（需要根据实际页面结构调整）
            price_data = {}
            
            # 这里需要根据CCTD官网的实际页面结构来解析价格
            # 示例：寻找价格相关的元素
            price_elements = soup.find_all(text=lambda text: text and '元/吨' in text)
            
            for elem in price_elements:
                # 解析价格数据
                # 实际实现需要根据页面结构调整
                pass
            
            return price_data
            
        except Exception as e:
            print(f'采集CCTD价格失败: {e}')
            return None
    
    def collect_guangzhou_port_price(self):
        """采集广州港进口动力煤价格"""
        try:
            # 访问广东省能源运销协会
            url = 'http://www.gdetsa.org.cn'
            response = self.session.get(url, timeout=10)
            response.encoding = 'utf-8'
            
            # 解析页面内容
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取价格信息
            price_data = {}
            
            # 这里需要根据网站的实际页面结构来解析价格
            # 示例：寻找价格相关的元素
            price_links = soup.find_all('a', href=lambda href: href and 'price' in href)
            
            for link in price_links:
                # 解析价格链接
                # 实际实现需要根据页面结构调整
                pass
            
            return price_data
            
        except Exception as e:
            print(f'采集广州港价格失败: {e}')
            return None
    
    def save_to_csv(self, data, filename):
        """保存数据到CSV文件"""
        try:
            df = pd.DataFrame(data)
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f'数据已保存到: {filename}')
            return True
        except Exception as e:
            print(f'保存数据失败: {e}')
            return False
    
    def collect_daily_data(self):
        """采集每日数据"""
        today = datetime.now().strftime('%Y-%m-%d')
        print(f'开始采集 {today} 的数据...')
        
        # 采集CCTD价格
        cctd_data = self.collect_cctd_price()
        
        # 采集广州港价格
        guangzhou_data = self.collect_guangzhou_port_price()
        
        # 合并数据
        daily_data = {
            '日期': today,
            'CCTD数据': cctd_data,
            '广州港数据': guangzhou_data
        }
        
        return daily_data

def main():
    """主函数"""
    print('=== 广东省动力煤价格数据采集程序 ===')
    print('采集时间:', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print()
    
    # 创建采集器
    collector = CoalPriceCollector()
    
    # 采集数据
    daily_data = collector.collect_daily_data()
    
    # 保存数据
    filename = f'coal_price_{datetime.now().strftime("%Y%m%d")}.csv'
    collector.save_to_csv(daily_data, filename)
    
    print()
    print('数据采集完成！')

if __name__ == '__main__':
    main()
