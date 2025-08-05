import os
from AppStoreTopScraper import AppStoreTopScraper
from GooglePlayStoreTopScraper import GooglePlayStoreTopScraper

def run_appstore():
    country = input("앱스토어 국가 코드 입력 (예: kr, us, jp) [기본값: kr]: ").strip() or "kr"
    limit = input("수집할 앱 개수 입력 (최대 200) [기본값: 100]: ").strip()
    limit = int(limit) if limit.isdigit() else 100
    chart_type = input("차트 타입 입력 (topfreeapplications, toppaidapplications, topgrossingapplications) [기본값: topfreeapplications]: ").strip() or "topfreeapplications"

    scraper = AppStoreTopScraper(country=country, limit=limit)
    apps = scraper.scrape_top_apps_with_details(chart_type=chart_type)
    if apps:
        save_type = input("저장 형식 선택 (csv/json) [기본값: csv]: ").strip().lower() or "csv"
        filename = input("저장 파일명 입력 (확장자 제외) [기본값: appstore_top_apps]: ").strip() or "appstore_top_apps"
        export_dir = os.path.join("exports")
        os.makedirs(export_dir, exist_ok=True)
        filepath = os.path.join(export_dir, filename + (".json" if save_type == "json" else ".csv"))
        if save_type == "json":
            scraper.save_to_json(apps, filepath)
        else:
            scraper.save_to_csv(apps, filepath)

def run_googleplay():
    print("구글 플레이스토어 Top 앱 정보 수집 시작...")
    apps = GooglePlayStoreTopScraper.get_google_play_top_apps()
    if apps:
        save_type = input("저장 형식 선택 (csv/json) [기본값: csv]: ").strip().lower() or "csv"
        filename = input("저장 파일명 입력 (확장자 제외) [기본값: googleplay_top_apps]: ").strip() or "googleplay_top_apps"
        export_dir = os.path.join("exports")
        os.makedirs(export_dir, exist_ok=True)
        filepath = os.path.join(export_dir, filename + (".json" if save_type == "json" else ".csv"))
        if save_type == "json":
            GooglePlayStoreTopScraper.save_to_json(apps, filepath)
        else:
            GooglePlayStoreTopScraper.save_to_csv(apps, filepath)
    else:
        print("앱 정보를 수집하지 못했습니다.")

def main():
    print("수집할 스토어를 선택하세요:")
    print("1. Apple App Store")
    print("2. Google Play Store")
    print("3. 둘 다")
    choice = input("번호 입력 (1/2/3): ").strip()

    if choice == "1":
        run_appstore()
    elif choice == "2":
        run_googleplay()
    elif choice == "3":
        run_appstore()
        run_googleplay()
    else:
        print("잘못된 입력입니다. 프로그램을 종료합니다.")

if __name__ == "__main__":
    main()