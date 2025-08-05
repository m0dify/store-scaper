import requests
import json
import csv
import os
from datetime import datetime
from bs4 import BeautifulSoup
import time
import random


class GooglePlayStoreTopScraper:
    @staticmethod
    def get_google_play_top_apps():
        # 다양한 URL 시도
        urls = [
            "https://play.google.com/store/apps/collection/topselling_free",
            "https://play.google.com/store/apps/category/GAME/collection/topselling_free",
            "https://play.google.com/store/apps/top"
        ]
        
        # 더 현실적인 헤더
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }

        session = requests.Session()
        session.headers.update(headers)

        for url in urls:
            try:
                print(f"시도 중인 URL: {url}")
                
                # 랜덤 지연
                time.sleep(random.uniform(2, 5))
                
                response = session.get(url, timeout=30)
                print(f"응답 상태 코드: {response.status_code}")
                
                if response.status_code == 200:
                    # HTML 내용 확인
                    html_content = response.text
                    print(f"HTML 길이: {len(html_content)}")
                    
                    # 응답 내용을 파일로 저장하여 구조 확인
                    with open('debug_response.html', 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    print("디버그용 HTML 파일 저장 완료: debug_response.html")
                    
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    # 여러 가능한 선택자 시도
                    selectors = [
                        'div[data-ds-package-name]',  # 앱 패키지명이 있는 div
                        'a[href*="/store/apps/details?id="]',  # 앱 상세 링크
                        '.ULeU3b',  # 일반적인 앱 컨테이너 클래스
                        '.Qfxief',  # 다른 가능한 클래스
                        '.VfPpkd-EScbFb-JIbuQc',  # 원래 시도했던 클래스
                        '.Si6A0c'   # 또 다른 가능한 클래스
                    ]
                    
                    apps = []
                    
                    for selector in selectors:
                        print(f"선택자 시도: {selector}")
                        elements = soup.select(selector)
                        print(f"찾은 요소 수: {len(elements)}")
                        
                        if elements:
                            apps = GooglePlayStoreTopScraper.parse_apps_from_elements(elements, selector)
                            if apps:
                                print(f"성공적으로 {len(apps)}개 앱 정보 추출")
                                return apps
                    
                    # 직접 앱 링크 찾기
                    app_links = soup.find_all('a', href=lambda x: x and '/store/apps/details?id=' in x)
                    print(f"발견된 앱 링크 수: {len(app_links)}")
                    
                    if app_links:
                        apps = GooglePlayStoreTopScraper.parse_apps_from_links(app_links[:10])
                        if apps:
                            return apps
                
                else:
                    print(f"HTTP 오류: {response.status_code}")
                    
            except requests.RequestException as e:
                print(f"요청 오류 ({url}): {e}")
                continue
            except Exception as e:
                print(f"파싱 오류 ({url}): {e}")
                continue

        print("모든 URL에서 데이터 추출 실패")
        return []

    @staticmethod
    def parse_apps_from_elements(elements, selector):
        apps = []
        for i, element in enumerate(elements[:10], 1):
            try:
                app_info = GooglePlayStoreTopScraper.extract_app_info(element, i)
                if app_info:
                    apps.append(app_info)
            except Exception as e:
                print(f"요소 {i} 파싱 오류: {e}")
                continue
        return apps

    @staticmethod
    def parse_apps_from_links(app_links):
        apps = []
        for i, link in enumerate(app_links[:10], 1):
            try:
                href = link.get('href', '')
                if not href.startswith('http'):
                    href = 'https://play.google.com' + href
                
                app_id = href.split('id=')[-1].split('&')[0] if 'id=' in href else 'unknown'
                
                # 링크 텍스트나 주변 요소에서 앱 이름 찾기
                name = link.get_text(strip=True) or link.get('title', '') or 'Unknown App'
                
                # 부모 요소에서 추가 정보 찾기
                parent = link.parent
                developer = 'Unknown Developer'
                
                # 개발자 정보 찾기
                dev_elements = parent.find_all(text=True) if parent else []
                for text in dev_elements:
                    text = text.strip()
                    if text and text != name and len(text) > 2:
                        developer = text
                        break

                app_info = {
                    'rank': i,
                    'name': name,
                    'developer': developer,
                    'rating': 'N/A',
                    'app_id': app_id,
                    'url': href,
                    'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                apps.append(app_info)
                
            except Exception as e:
                print(f"링크 {i} 파싱 오류: {e}")
                continue
                
        return apps

    @staticmethod
    def extract_app_info(element, rank):
        try:
            # 다양한 방법으로 앱 정보 추출 시도
            name = 'Unknown App'
            developer = 'Unknown Developer'
            app_id = 'unknown'
            app_url = ''
            
            # 앱 이름 찾기
            name_selectors = ['.Epkrse', '.DdYX5', '.WsMG1c', 'h3', '.BNeawe']
            for selector in name_selectors:
                name_elem = element.select_one(selector)
                if name_elem and name_elem.get_text(strip=True):
                    name = name_elem.get_text(strip=True)
                    break
            
            # 개발자 이름 찾기
            dev_selectors = ['.ubGTjb', '.wMUdtb', '.x4FaRb']
            for selector in dev_selectors:
                dev_elem = element.select_one(selector)
                if dev_elem and dev_elem.get_text(strip=True):
                    developer = dev_elem.get_text(strip=True)
                    break
            
            # 앱 링크 찾기
            link_elem = element.find('a', href=True) or element.find_parent('a', href=True)
            if link_elem:
                href = link_elem['href']
                if not href.startswith('http'):
                    app_url = 'https://play.google.com' + href
                else:
                    app_url = href
                    
                if 'id=' in href:
                    app_id = href.split('id=')[-1].split('&')[0]
            
            # data 속성에서 패키지명 찾기
            if app_id == 'unknown':
                package_name = element.get('data-ds-package-name')
                if package_name:
                    app_id = package_name

            return {
                'rank': rank,
                'name': name,
                'developer': developer,
                'rating': 'N/A',
                'app_id': app_id,
                'url': app_url,
                'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            print(f"앱 정보 추출 오류: {e}")
            return None

    @staticmethod
    def get_app_details(app_id):
        """개별 앱의 상세 정보를 가져오는 함수"""
        try:
            url = f"https://play.google.com/store/apps/details?id={app_id}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # 평점 추출
                rating_elem = soup.select_one('[data-g-id="text"] div')
                rating = rating_elem.get_text(strip=True) if rating_elem else 'N/A'
                
                return rating
                
        except Exception as e:
            print(f"앱 상세 정보 가져오기 오류 ({app_id}): {e}")
            
        return 'N/A'

    @staticmethod
    def save_to_csv(data, filepath):
        if not data:
            print("저장할 데이터가 없습니다.")
            return

        try:
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = ['rank', 'name', 'developer', 'rating', 'app_id', 'url', 'scraped_at']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            print(f"CSV 저장 완료: {filepath}")
        except Exception as e:
            print(f"CSV 저장 중 오류: {e}")

    @staticmethod
    def save_to_json(data, filepath):
        if not data:
            print("저장할 데이터가 없습니다.")
            return

        try:
            with open(filepath, 'w', encoding='utf-8') as jsonfile:
                json.dump(data, jsonfile, ensure_ascii=False, indent=2)
            print(f"JSON 저장 완료: {filepath}")
        except Exception as e:
            print(f"JSON 저장 중 오류: {e}")

    @staticmethod
    def main():
        print("구글 플레이스토어 Top 10 무료 앱 스크래핑 시작...")
        print("주의: Google Play Store는 봇 차단 정책이 있어 성공률이 낮을 수 있습니다.")

        script_dir = os.path.dirname(os.path.abspath(__file__))
        exports_dir = os.path.join(script_dir, "exports")
        os.makedirs(exports_dir, exist_ok=True)

        date_str = datetime.now().strftime("%Y%m%d-%H")
        csv_filepath = os.path.join(exports_dir, f"google_apps_{date_str}.csv")
        json_filepath = os.path.join(exports_dir, f"google_apps_{date_str}.json")

        apps_data = GooglePlayStoreTopScraper.get_google_play_top_apps()

        if apps_data:
            print(f"\n{len(apps_data)}개 앱 정보를 가져왔습니다.")
            print("\n=== 수집된 앱 목록 ===")
            for app in apps_data:
                print(f"{app['rank']}. {app['name']} - {app['developer']}")
                print(f"   ID: {app['app_id']}")
                print(f"   URL: {app['url'][:80]}...")
                print()

            GooglePlayStoreTopScraper.save_to_csv(apps_data, csv_filepath)
            GooglePlayStoreTopScraper.save_to_json(apps_data, json_filepath)
        else:
            print("\n데이터 수집 실패.")
            print("\n대안 방법:")
            print("1. VPN 사용")
            print("2. Google Play Store API 사용 (공식)")
            print("3. 써드파티 API 서비스 이용")
            print("4. Selenium 같은 브라우저 자동화 도구 사용")

if __name__ == "__main__":
    GooglePlayStoreTopScraper.main()