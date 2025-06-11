import re
from playwright.sync_api import sync_playwright
import time

def main():
    search_query = "tokek kepeleset"
    url = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until='domcontentloaded')

        # Melakukan scroll beberapa kali untuk memuat lebih banyak hasil
        for _ in range(5):  # jumlah scroll, sesuaikan kebutuhan
            page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
            time.sleep(2)  # tunggu 2 detik agar halaman termuat

        # Tunggu elemen video muncul
        page.wait_for_selector('a#video-title', timeout=10000)

        # Ambil judul dan waktu upload
        videos = page.eval_on_selector_all(
            'ytd-video-renderer',  # Selector container video
            '''
            (elements) => {
                return elements.map(el => {
                    const titleEl = el.querySelector('a#video-title');
                    const viewEl = el.querySelector('span.ytd-video-meta-block');
                    const timeEl= el.querySelector('#metadata-line > span:nth-child(4)');
                    return {
                        title: titleEl ? titleEl.textContent.trim() : '',
                        url: titleEl ? titleEl.href : '',
                        // Untuk waktu upload, biasanya di dalam span dengan class tertentu
                        viewer_count: viewEl ? viewEl.textContent.trim() : '',
                        time_publish: timeEl ? timeEl.textContent.trim() : ''
                    };
                });
            }
            '''
        )

        print("Hasil Pencarian:")
        for video in videos:
            print(f"Judul: {video['title']}")
            print(f"URL: {video['url']}")
            print(f"Jumlah Penonton: {video['viewer_count']}")
            print(f"Publish: {video['time_publish']}")
            print("-" * 50)

        browser.close()

if __name__ == "__main__":
    main()