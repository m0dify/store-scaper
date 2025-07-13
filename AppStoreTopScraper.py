import requests
import json
import pandas as pd
from datetime import datetime
import time

class AppStoreTopScraper:
    def __init__(self, country='kr', limit=100):
        """
        앱스토어 Top 앱 정보를 수집하는 클래스

        Args:
            country: 국가 코드 (kr, us, jp 등)
            limit: 수집할 앱 개수 (최대 200)
        """
        self.country = country
        self.limit = limit
        self.base_url = "https://itunes.apple.com"

    def get_top_apps(self, category="all", chart_type="topfreeapplications"):
        """
        iTunes RSS API를 사용하여 Top 앱 정보 수집

        Args:
            category: 카테고리 (all, games, productivity 등)
            chart_type: 차트 타입 (topfreeapplications, toppaidapplications, topgrossingapplications)

        Returns:
            list: 앱 정보 리스트
        """
        # iTunes RSS API 엔드포인트
        url = f"{self.base_url}/{self.country}/rss/{chart_type}/limit={self.limit}/json"

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            data = response.json()
            entries = data['feed']['entry']

            apps = []
            for entry in entries:
                try:
                    # 데이터 구조 안전하게 접근
                    app_info = {
                        'rank': len(apps) + 1,
                        'name': self._safe_get(entry, 'im:name', 'label'),
                        'artist': self._safe_get(entry, 'im:artist', 'label'),
                        'category': self._safe_get(entry, 'category', 'attributes', 'label'),
                        'price': self._safe_get(entry, 'im:price', 'label'),
                        'release_date': self._safe_get(entry, 'im:releaseDate', 'label'),
                        'app_id': self._safe_get(entry, 'id', 'attributes', 'im:id'),
                        'bundle_id': self._safe_get(entry, 'id', 'attributes', 'im:bundleId'),
                        'app_url': self._get_app_url(entry),
                        'icon_url': self._get_icon_url(entry),
                        'summary': self._safe_get(entry, 'summary', 'label'),
                        'rights': self._safe_get(entry, 'rights', 'label')
                    }
                    apps.append(app_info)
                except Exception as e:
                    print(f"앱 정보 파싱 실패 (순위 {len(apps) + 1}): {e}")
                    continue

            return apps

        except requests.RequestException as e:
            print(f"API 요청 실패: {e}")
            return []
        except KeyError as e:
            print(f"데이터 파싱 실패: {e}")
            return []

    def _safe_get(self, data, *keys):
        """안전하게 중첩된 딕셔너리 값 가져오기"""
        try:
            for key in keys:
                if isinstance(data, dict):
                    data = data.get(key, {})
                else:
                    return ''
            return data if isinstance(data, str) else ''
        except:
            return ''

    def _get_app_url(self, entry):
        """앱 URL 안전하게 가져오기"""
        try:
            link = entry.get('link', {})
            if isinstance(link, dict):
                return link.get('attributes', {}).get('href', '')
            elif isinstance(link, list) and len(link) > 0:
                return link[0].get('attributes', {}).get('href', '')
            return ''
        except:
            return ''

    def _get_icon_url(self, entry):
        """아이콘 URL 안전하게 가져오기"""
        try:
            images = entry.get('im:image', [])
            if isinstance(images, list) and len(images) > 0:
                # 가장 큰 이미지 선택 (마지막 요소)
                return images[-1].get('label', '')
            return ''
        except:
            return ''

    def get_app_details(self, app_id):
        """
        iTunes Search API를 사용하여 앱 상세 정보 수집

        Args:
            app_id: 앱 ID

        Returns:
            dict: 앱 상세 정보
        """
        url = f"{self.base_url}/lookup"
        params = {
            'id': app_id,
            'country': self.country,
            'entity': 'software'
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            if data['resultCount'] > 0:
                app = data['results'][0]
                return {
                    'version': app.get('version', ''),
                    'file_size': app.get('fileSizeBytes', 0),
                    'rating': app.get('averageUserRating', 0),
                    'rating_count': app.get('userRatingCount', 0),
                    'content_rating': app.get('contentAdvisoryRating', ''),
                    'description': app.get('description', ''),
                    'screenshots': app.get('screenshotUrls', []),
                    'languages': app.get('languageCodesISO2A', []),
                    'genres': app.get('genres', []),
                    'minimum_os_version': app.get('minimumOsVersion', ''),
                    'current_version_release_date': app.get('currentVersionReleaseDate', ''),
                    'developer_website': app.get('artistViewUrl', ''),
                    'support_url': app.get('supportUrl', '')
                }
            return {}

        except requests.RequestException as e:
            print(f"앱 상세 정보 요청 실패 (ID: {app_id}): {e}")
            return {}

    def scrape_top_apps_with_details(self, chart_type="topfreeapplications"):
        """
        Top 앱 정보와 상세 정보를 모두 수집

        Args:
            chart_type: 차트 타입

        Returns:
            list: 완전한 앱 정보 리스트
        """
        print(f"Top {self.limit} 앱 정보 수집 시작...")

        # 기본 Top 앱 정보 수집
        apps = self.get_top_apps(chart_type=chart_type)

        if not apps:
            print("기본 앱 정보 수집 실패")
            return []

        print(f"{len(apps)}개 앱 기본 정보 수집 완료")

        # 상세 정보 수집 여부 확인
        get_details = input("상세 정보도 수집하시겠습니까? (y/n): ").lower().strip()

        if get_details == 'y':
            print("상세 정보 수집 시작...")

            # 각 앱의 상세 정보 수집
            for i, app in enumerate(apps, 1):
                if app.get('app_id'):  # app_id가 있는 경우만 상세 정보 수집
                    print(f"({i}/{len(apps)}) {app['name']} 상세 정보 수집 중...")

                    details = self.get_app_details(app['app_id'])
                    app.update(details)

                    # API 요청 제한을 위한 대기
                    time.sleep(0.5)
                else:
                    print(f"({i}/{len(apps)}) {app['name']} - app_id 없음, 상세 정보 스킵")

            print("모든 앱 정보 수집 완료!")
        else:
            print("기본 정보만 수집 완료!")

        return apps

    def save_to_csv(self, apps, filename=None):
        """
        수집한 앱 정보를 CSV 파일로 저장

        Args:
            apps: 앱 정보 리스트
            filename: 저장할 파일명
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"app_store_top_{self.limit}_{self.country}_{timestamp}.csv"

        df = pd.DataFrame(apps)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"CSV 파일 저장 완료: {filename}")

    def save_to_json(self, apps, filename=None):
        """
        수집한 앱 정보를 JSON 파일로 저장

        Args:
            apps: 앱 정보 리스트
            filename: 저장할 파일명
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"app_store_top_{self.limit}_{self.country}_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(apps, f, ensure_ascii=False, indent=2)
        print(f"JSON 파일 저장 완료: {filename}")




# 추가 기능: 카테고리별 분석
def analyze_by_category(apps):
    """카테고리별 앱 분석"""
    category_count = {}
    for app in apps:
        category = app.get('category', 'Unknown')
        category_count[category] = category_count.get(category, 0) + 1

    print("\n=== 카테고리별 앱 분포 ===")
    for category, count in sorted(category_count.items(), key=lambda x: x[1], reverse=True):
        print(f"{category}: {count}개")


# 추가 기능: 평점 분석
def analyze_ratings(apps):
    """평점 분석"""
    ratings = [app.get('rating', 0) for app in apps if app.get('rating', 0) > 0]

    if ratings:
        print("\n=== 평점 분석 ===")
        print(f"평균 평점: {sum(ratings) / len(ratings):.2f}")
        print(f"최고 평점: {max(ratings)}")
        print(f"최저 평점: {min(ratings)}")
        print(f"평점 4.0 이상 앱 수: {sum(1 for r in ratings if r >= 4.0)}개")


# 사용 예제
if __name__ == "__main__":
    scraper = AppStoreTopScraper(country='kr', limit=10)  # 테스트용으로 10개만

    # 무료 앱 Top 수집
    print("=== 무료 앱 Top 수집 ===")
    free_apps = scraper.scrape_top_apps_with_details(chart_type="topfreeapplications")

    if free_apps:
        current_datetime = datetime.now()
        formatted_date = current_datetime.strftime("%Y%m%d-%H")
        scraper.save_to_csv(free_apps, f"exports/apple_free_apps_{formatted_date}.csv")
        scraper.save_to_json(free_apps, f"exports/apple_free_apps_{formatted_date}.json")

        # 간단한 통계 출력
        print("\n=== 수집 결과 통계 ===")
        print(f"총 수집 앱 수: {len(free_apps)}")

        # 평점 통계 (상세 정보가 있는 경우만)
        ratings = [app.get('rating', 0) for app in free_apps if app.get('rating', 0) > 0]
        if ratings:
            print(f"평균 평점: {sum(ratings) / len(ratings):.2f}")
            print(f"평균 평점 수: {sum(app.get('rating_count', 0) for app in free_apps) / len(free_apps):.0f}")

        # Top 앱 목록 출력
        print(f"\n=== Top {min(len(free_apps), 10)} 앱 목록 ===")
        for i, app in enumerate(free_apps[:10], 1):
            rating_info = f"평점: {app.get('rating', 'N/A')}" if app.get('rating') else "평점: N/A"
            print(f"{i}. {app['name']} - {app['artist']} ({rating_info})")

        # 카테고리별 분석
        analyze_by_category(free_apps)
    else:
        print("앱 정보 수집에 실패했습니다.")

    # 추가 차트 수집 여부 확인
    collect_more = input("\n다른 차트도 수집하시겠습니까? (y/n): ").lower().strip()

    if collect_more == 'y':
        print("\n=== 유료 앱 Top 수집 ===")
        paid_apps = scraper.scrape_top_apps_with_details(chart_type="toppaidapplications")

        if paid_apps:
            current_datetime = datetime.now()
            formatted_date = current_datetime.strftime("%Y%m%d-%H")
            scraper.save_to_csv(paid_apps, f"exports/apple_paid_apps_{formatted_date}.csv")
            scraper.save_to_json(paid_apps, f"exports/apple_paid_apps_{formatted_date}.json")
            print(f"유료 앱 {len(paid_apps)}개 수집 완료!")