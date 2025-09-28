from requests_html import HTMLSession
import sys
import json
import re
import time

session = HTMLSession()


def fetch_advertiser_creatives(advertiser_id, creative_id):
    url = "https://adstransparency.google.com/anji/_/rpc/LookupService/GetCreativeById?authuser=0"
    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/x-www-form-urlencoded",
        "origin": "https://adstransparency.google.com",
        "priority": "u=1, i",
        "referer": "https://adstransparency.google.com",
        "sec-ch-ua": '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
        "x-browser-channel": "stable",
        "x-browser-copyright": "Copyright 2025 Google LLC. All rights reserved.",
        "x-browser-year": "2025",
        "x-same-domain": "1",
    }
    payload = {
        "1": advertiser_id,
        "2": creative_id,
        "5": {"1": 1, "2": 27, "3": 2586}
    }
    data = {"f.req": json.dumps(payload)}
    response = session.post(url, headers=headers, data=data)
    creatives_list = []

    if response.status_code == 200:

        creatives = response.json().get('1', {}).get('5')

        for c in creatives:
            creatives_list.append(c.get('1', {}).get('4'))

    else:

        return None

    return creatives_list


def extract_youtube_url(referrer, url):
    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "referer": referrer,
        "sec-ch-ua": '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "script",
        "sec-fetch-mode": "no-cors",
        "sec-fetch-site": "cross-site",
        "sec-fetch-storage-access": "active",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
        "x-browser-channel": "stable",
        "x-browser-copyright": "Copyright 2025 Google LLC. All rights reserved.",
        "x-browser-year": "2025",
    }
    response = session.get(url, headers=headers)
    print("Status:", response.status_code)
    if response.status_code == 200:
        # Regex for URLs starting with i1.ytimg.com and ending with jpg/png/jpeg
        pattern = r"https://i1\.ytimg\.com[^\s\"']+\.(?:jpg|png|jpeg)"

        matches = re.findall(pattern, response.text)

        if matches:
            print("Found image URLs:")
            for m in matches:
                return m
        else:
            return None
    else:
        return None


def controller(url):
    advertiser_id = url.split('advertiser/')[1].split('/')[0] if '/creative/' in url else url.split('advertiser/')[1]
    creative_id = url.split('/creative/')[1].split('?')[0] if '?' in url else url.split('/creative/')[1]
    creatives_list = fetch_advertiser_creatives(advertiser_id, creative_id)
    if creatives_list:
        res = extract_youtube_url(url, creatives_list[0])
        if res:
            return res
        else:
            return None
    else:
        return None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scrape.py <URL>")
        sys.exit(1)

    url = sys.argv[1]
    t1 = time.perf_counter()
    yt_url = controller(url)
    if yt_url:
        playable_url = 'https://www.youtube.com/watch?v={}'.format(yt_url.split('/vi/')[1].split('/')[0])
        print("Extracted playable:", playable_url)
    else:
        print('Provided Ad ID did not have any associated playable url')

    print('Total Execution Time: ', time.perf_counter() - t1)

