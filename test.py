import re
from playwright.sync_api import sync_playwright
import time

def main():
    search_query = "jurnal rosi"
    url = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url, wait_until='domcontentloaded')

        # Melakukan scroll beberapa kali untuk memuat lebih banyak hasil
        for _ in range(5):
            page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
            time.sleep(2)

        # Tunggu elemen video muncul
        page.wait_for_selector('a#video-title', timeout=10000)

        # Ambil daftar video
        videos = page.eval_on_selector_all(
            'ytd-video-renderer',
            '''
            (elements) => {
                return elements.map(el => {
                    const titleEl = el.querySelector('a#video-title');
                    const viewEl = el.querySelector('span.ytd-video-meta-block');
                    const timeEl= el.querySelector('#metadata-line span:nth-child(4)');
                    return {
                        title: titleEl ? titleEl.textContent.trim() : '',
                        url: titleEl ? "https://www.youtube.com" + titleEl.getAttribute('href') : '',
                        viewer_count: viewEl ? viewEl.textContent.trim() : '',
                        time_publish: timeEl ? timeEl.textContent.trim() : ''
                    };
                });
            }
            '''
        )

         # Loop untuk ambil deskripsi dari setiap video
        for video in videos[:3]:
            print(f"\nMengambil deskripsi untuk video: {video['title']}")
            try:
                page.goto(video['url'], wait_until='domcontentloaded')
                time.sleep(3)  # beri waktu halaman termuat
                # Klik tombol 'Show more' atau tombol lain jika ada
                # Biasanya tombol ini dengan tag <tp-yt-paper-button>
                try:
                    page.wait_for_selector('#description-inner', timeout=5000)
                    # Klik tombol jika muncul
                    page.get_by_role("button", name="...more").click()
                    print("Klik tombol 'Show more' berhasil.")
                    time.sleep(2)  # tunggu halaman update
                except:
                    print("Tombol 'Show more' tidak ditemukan, lewati.")
                # Pastikan deskripsi sudah muncul
                page.wait_for_selector('#description-inner', timeout=15000)
                description = page.text_content('#description-inline-expander')
                if description:
                    description = description.strip()
                else:
                    description = "Deskripsi kosong"
            except Exception as e:
                description = f"Error saat pengambilan deskripsi: {str(e)}"

        print("Hasil Pencarian:")
        for video in videos:
            print(f"Judul: {video['title']}")
            print(f"URL: {video['url']}")
            print(f"Jumlah Penonton: {video['viewer_count']}")
            print(f"Publish: {video['time_publish']}")
            print(f"Deskripsi:\n{description}")
            print("-" * 50)

        browser.close()

if __name__ == "__main__":
    main()