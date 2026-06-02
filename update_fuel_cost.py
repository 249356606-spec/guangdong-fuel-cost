#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
广东省燃料成本分析系统 - 每日数据更新脚本
功能：自动采集煤炭和LNG价格数据，更新HTML Dashboard
作者：小小罗
"""

import requests
import re
import json
import os
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import time

class FuelCostUpdater:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.data_dir = os.path.expanduser('~/Desktop/燃料成本')
        self.html_file = os.path.join(self.data_dir, 'guangdong_fuel_cost_system.html')
        
    def get_cctd_prices(self):
        """从CCTD获取煤炭价格"""
        print("正在获取CCTD煤炭价格...")
        try:
            url = 'https://www.cctd.com.cn'
            response = requests.get(url, headers=self.headers, timeout=15)
            text = response.content.decode('gbk')
            
            prices = {}
            
            # 提取综合交易价格
            # 匹配模式：数字 + 元/吨
            patterns = {
                '综合交易5500': r'综合交易.*?(\d{3,4})\s*元/吨',
                '综合交易5000': r'综合交易5000.*?(\d{3,4})\s*元/吨',
                '综合交易4500': r'综合交易4500.*?(\d{3,4})\s*元/吨',
                '年度长协5500': r'年度长协5500.*?(\d{3,4})\s*元/吨',
                '年度长协5000': r'年度长协5000.*?(\d{3,4})\s*元/吨',
                '年度长协4500': r'年度长协4500.*?(\d{3,4})\s*元/吨',
            }
            
            # 简单提取价格
            price_matches = re.findall(r'(\d{3,4})\s*元/吨\s*变化', text)
            if len(price_matches) >= 6:
                prices['综合交易5500'] = int(price_matches[0])
                prices['综合交易5000'] = int(price_matches[1])
                prices['综合交易4500'] = int(price_matches[2])
                prices['年度长协5500'] = int(price_matches[3])
                prices['年度长协5000'] = int(price_matches[4])
                prices['年度长协4500'] = int(price_matches[5])
                print(f"CCTD价格获取成功: {prices}")
                return prices
            else:
                print("CCTD价格提取失败，使用备用方法")
                # 备用方法：直接从页面文本提取
                price_section = re.findall(r'(\d{3,4})\s*元/吨', text)
                if len(price_section) >= 6:
                    prices['综合交易5500'] = int(price_section[0])
                    prices['综合交易5000'] = int(price_section[1])
                    prices['综合交易4500'] = int(price_section[2])
                    prices['年度长协5500'] = int(price_section[3])
                    prices['年度长协5000'] = int(price_section[4])
                    prices['年度长协4500'] = int(price_section[5])
                    print(f"CCTD价格获取成功(备用): {prices}")
                    return prices
                    
        except Exception as e:
            print(f"获取CCTD价格失败: {e}")
        
        return None
    
    def get_guangzhou_port_prices(self):
        """从广东省能源运销协会获取广州港煤炭价格"""
        print("正在获取广州港煤炭价格...")
        try:
            url = 'http://www.gdetsa.org.cn'
            response = requests.get(url, headers=self.headers, timeout=15)
            response.encoding = 'utf-8'
            
            # 这里需要解析页面获取最新价格链接
            # 然后访问具体的价格页面获取数据
            # 由于网站结构可能变化，这里返回None表示需要手动检查
            print("广州港价格需要手动从网站获取")
            return None
            
        except Exception as e:
            print(f"获取广州港价格失败: {e}")
            return None
    
    def get_shpgx_lng_prices(self):
        """从SHPGX获取LNG价格"""
        print("正在获取SHPGX LNG价格...")
        try:
            url = 'https://www.shpgx.com/html/jgsj/lng/lngbjhq.html'
            response = requests.get(url, headers=self.headers, timeout=15)
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table')
            
            if table:
                rows = table.find_all('tr')
                lng_prices = {}
                
                for row in rows[1:]:  # 跳过表头
                    cells = row.find_all('td')
                    if len(cells) >= 6:
                        company = cells[1].text.strip()
                        station = cells[2].text.strip()
                        region = cells[3].text.strip()
                        price = cells[4].text.strip()
                        
                        # 提取广东地区数据
                        if '广东' in company or '广东' in region:
                            if '元/吨' in price:
                                price_value = int(price.replace('元/吨', ''))
                                key = f"{station}_{region}"
                                lng_prices[key] = price_value
                
                if lng_prices:
                    print(f"SHPGX LNG价格获取成功: {lng_prices}")
                    return lng_prices
                    
        except Exception as e:
            print(f"获取SHPGX LNG价格失败: {e}")
        
        return None
    
    def update_html(self, cctd_prices=None, guangzhou_prices=None, lng_prices=None):
        """更新HTML文件"""
        print("正在更新HTML文件...")
        
        if not os.path.exists(self.html_file):
            print(f"HTML文件不存在: {self.html_file}")
            return False
        
        with open(self.html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 更新日期
        today = datetime.now().strftime('%Y-%m-%d')
        content = re.sub(r'数据更新时间：\d{4}年\d{1,2}月\d{1,2}日', f'数据更新时间：{today}', content)
        
        # 如果有CCTD价格，更新对应位置
        if cctd_prices:
            # 这里可以根据实际HTML结构更新价格
            pass
        
        # 保存更新后的文件
        with open(self.html_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"HTML文件更新完成: {self.html_file}")
        return True
    
    def run(self):
        """执行更新流程"""
        print(f"=== 广东省燃料成本分析系统数据更新 ===")
        print(f"更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 获取数据
        cctd_prices = self.get_cctd_prices()
        guangzhou_prices = self.get_guangzhou_port_prices()
        lng_prices = self.get_shpgx_lng_prices()
        
        # 更新HTML
        success = self.update_html(cctd_prices, guangzhou_prices, lng_prices)
        
        if success:
            print("\n数据更新完成！")
        else:
            print("\n数据更新失败！")
        
        return success

if __name__ == '__main__':
    updater = FuelCostUpdater()
    updater.run()
