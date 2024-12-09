import re, requests
import urllib.parse


def getCookies():
    try:
        url = "https://cdn.jsdelivr.net/gh/testfwn/trbx/test.txt"
        resp = requests.get(url)
        cookies = resp.text.replace("##cookie##", "").strip()
        return cookies

    except Exception as e:
        print(f"Error while cookies {e}")


def extractJStoken(html_response):
    try:
        match = re.search(r"decodeURIComponent\(`(.*?)`\)", html_response)

        if match:
            encoded_string = match.group(1)
            decoded_string = urllib.parse.unquote(encoded_string)
            token_match = re.search(r'fn\("([A-F0-9]+)"\)', decoded_string)
            if token_match:
                token = token_match.group(1)
                # print("Extracted Token:", token)
                return token
            else:
                print("Token not found in decoded string.")
        else:
            print("Encoded string not found in HTML.")
    except:
        print("unable to extract jstoken")


cookie = getCookies()
# print(f"Cookies {cookie}")


def genKeys(surl):
    try:
        url = f"http://www.terabox.app/sharing/link?surl={surl}"
        headers = {
            "Cookie": cookie,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        }
        resp = requests.get(url=url, headers=headers)
        # print(f"Status Code: {resp.status_code}")
        # print(extractJStoken(resp.text))
        return extractJStoken(resp.text)
    except Exception as e:
        print(f"Error at genKeys(): {e}")


def getFilesList2(jsToken, surl, isRoot=True, dir=""):
    try:
        purl = "https://httpie.io/app/api/proxy"

        url = f"http://www.terabox.app/share/list?app_id=250528&web=1&channel=dubox&clienttype=5&jsToken={jsToken}&page=1&num=20&by=name&order=asc&site_referer=&shorturl={surl}&dir={dir}&"
        if isRoot:
            url += "root=1"

        headers = {
            "x-pie-req-meta-url": url,
            "x-pie-req-header-host": "www.terabox.app",
            "x-pie-req-meta-method": "GET",
            "x-pie-req-meta-follow-redirects": "true",
            "x-pie-req-header-Cookie": cookie,
            "x-pie-req-header-User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        }
        # headers = {
        #     "Cookie": cookie,
        #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        # }
        resp = requests.get(url=purl, headers=headers)
        # print(f"Status Code: {resp.status_code}")
        # print(url)
        # print(resp.text)

        if resp.status_code == 200 and resp.json() and resp.json()["list"]:
            return resp.json()

        else:
            print(resp.status_code)
    except Exception as e:
        try:
            respback = url
            respback += "\n\n" + str(headers)
            respback += "\n\n" + str(resp.text)
            with open("log.txt", "a+", encoding="utf-8") as file:
                file.write(respback)
        except Exception as ee:
            print(ee)
        # print(f"Jstoken: {jsToken}")
        print(f"Error at getFilesList2(): {e}")


def streamData(uk, shareid, fid):
    try:
        purl = "https://httpie.io/app/api/proxy"

        url = f"https://www.terabox.app/share/streaming?uk={uk}&shareid={shareid}&type=M3U8_FLV_264_480&fid={fid}&sign=1&timestamp=1&jsToken=1&esl=1&isplayer=1&ehps=1&clienttype=0&app_id=250528&web=1&channel=dubox"

        headers = {
            "x-pie-req-meta-url": url,
            "x-pie-req-header-host": "www.terabox.app",
            "x-pie-req-meta-method": "GET",
            "x-pie-req-meta-follow-redirects": "true",
            "x-pie-req-header-Cookie": cookie,
            "x-pie-req-header-User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        }
        resp = requests.get(url=purl, headers=headers)

        if resp.status_code == 200 and "" in resp.text:
            return resp.text

        else:
            print(resp.text)
    except Exception as e:
        print(f"Error at streamdata(): {e}")


def getFilesList(jsToken, surl, isRoot=True, dir=""):
    try:
        url = f"http://www.terabox.app/share/list?app_id=250528&web=1&channel=dubox&clienttype=5&jsToken={jsToken}&page=1&num=20&by=name&order=asc&site_referer=&shorturl={surl}&dir={dir}&"
        if isRoot:
            url += "root=1"

        headers = {
            "Cookie": cookie,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        }
        resp = requests.get(url=url, headers=headers)
        # print(f"Status Code: {resp.status_code}")
        # print(url)
        # print(resp.text)

        if resp.status_code == 200 and resp.json() and resp.json()["list"]:
            return resp.json()

        else:
            print(resp.status_code)
    except Exception as e:
        try:
            respback = url
            respback += "\n\n" + str(headers)
            respback += "\n\n" + str(resp.text)
            with open("log.txt", "a+", encoding="utf-8") as file:
                file.write(respback)
        except Exception as ee:
            print(ee)
        # print(f"Jstoken: {jsToken}")
        print(f"Error at getFilesList(): {e}")


def filesList(jsToken, surl, isRoot=True, dir=""):
    try:
        url = f"http://www.terabox.app/share/list?app_id=250528&web=1&channel=dubox&clienttype=5&jsToken={jsToken}&page=1&num=20&by=name&order=asc&site_referer=&shorturl={surl}&dir={dir}&"
        if isRoot:
            url += "root=1"
        headers = {
            "Cookie": cookie,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        }
        resp = requests.get(url=url, headers=headers)
        # print(f"Status Code: {resp.status_code}")
        # print(url)
        # print(resp.text)

        if resp.status_code == 200 and resp.json() and resp.json()["list"]:
            for file in resp.json()["list"]:
                if file["isdir"] == "1":
                    print(f"Directory : {file['server_filename']}")
                    print("->")
                    filesList(jsToken, surl, isRoot=False, dir=file["path"])
                else:
                    print(
                        f"-> {file['server_filename']} {'Download link available' if file.get('dlink', False) else ''}"
                    )

        else:
            print(resp.text)
    except Exception as e:
        print(f"Error at filesList(): {e}")


if __name__ == "__main__":
    surl = "12jesbAn0f0VtzQT-9Nc1rg"
    if surl.startswith("1"):
        surl = surl[1:]
    jsToken = genKeys(surl)
    filesList(jsToken=jsToken, surl=surl)
