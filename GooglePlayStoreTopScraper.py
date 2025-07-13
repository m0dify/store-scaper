import requests
import json
import csv
import os
from datetime import datetime
from bs4 import BeautifulSoup
import time


class GooglePlayStoreTopScraper:

    @staticmethod
    def get_google_play_top_apps():
        url = "https://play.google.com/store/apps/collection/topselling_free"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            apps = []
            app_elements = soup.find_all('div', class_='VfPpkd-EScbFb-JIbuQc')[:10]  # 변경된 구조에 따라 수정 필요할 수 있음

            for i, app in enumerate(app_elements, 1):
                try:
                    name = app.find('div', class_='Epkrse').text.strip()
                    developer = app.find('div', class_='ubGTjb').text.strip()
                    link_element = app.find('a', href=True)
                    app_url = "https://play.google.com" + link_element['href']
                    app_id = link_element['href'].split('id=')[-1]

                    app_info = {
                        'rank': i,
                        'name': name,
                        'developer': developer,
                        'rating': 'N/A',  # 별도 접근 필요
                        'app_id': app_id,
                        'url': app_url,
                        'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }

                    apps.append(app_info)
                except Exception as e:
                    print(f"앱 {i} 정보 추출 중 오류: {e}")
                    continue

            return apps

        except requests.RequestException as e:
            print(f"웹 요청 오류: {e}")
            return []
        except Exception as e:
            print(f"스크래핑 오류: {e}")
            return []

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

        script_dir = os.path.dirname(os.path.abspath(__file__))
        exports_dir = os.path.join(script_dir, "exports")
        os.makedirs(exports_dir, exist_ok=True)

        date_str = datetime.now().strftime("%Y%m%d-%H")
        csv_filepath = os.path.join(exports_dir, f"google_apps_{date_str}.csv")
        json_filepath = os.path.join(exports_dir, f"google_apps_{date_str}.json")

        apps_data = GooglePlayStoreTopScraper.get_google_play_top_apps()

        if apps_data:
            print(f"{len(apps_data)}개 앱 정보를 가져왔습니다.\n")
            for app in apps_data[:5]:
                print(f"{app['rank']}. {app['name']} - {app['developer']}")

            GooglePlayStoreTopScraper.save_to_csv(apps_data, csv_filepath)
            GooglePlayStoreTopScraper.save_to_json(apps_data, json_filepath)
        else:
            print("데이터 수집 실패.")

if __name__ == "__main__":
    GooglePlayStoreTopScraper.main()
