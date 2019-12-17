from google_images_download import google_images_download   # main library
import os
import urllib


class google_images_query:
    def __init__(self, keywords, keywords_to_exclude=[], time_min=None, time_max=None):
        self.keywords = ""
        for k in keywords:
            self.keywords += str(k)
            self.keywords += ","
        self.keywords = self.keywords[:-1]

        self.time_min = time_min
        self.time_max = time_max

        self.total_urls = set()

    def url_images(self):
        keywords = self.keywords

        response = google_images_download.googleimagesdownload()   # class inst

        # creating list of arguments
        arguments = {"keywords": keywords, "limit": 100, "no_download": True}

        if self.time_min is not None:
            arguments["time_min"] = self.time_min
        if self.time_max is not None:
            arguments["time_max"] = self.time_max

        # passing the arguments to the function
        query_res = response.download(arguments)

        init_urls_set = set()

        for k in keywords.split(','):
            for url in query_res[0][k]:
                init_urls_set.add(url)

        del arguments["keywords"]

        headers = {}
        headers['User-Agent'] = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.\
        36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"

        ct = len(init_urls_set)
        i = 1
        for u in init_urls_set:
            try:
                # this block is here because if request fails inside the
                # scraper, the system exits...
                # (then this block does a test to avoid any request fails)

                # url_test = response.build_search_url(None, None, None, u, None,
                #                                     None)

                # req = urllib.request.Request(url_test, headers=headers)
                # resp = urllib.request.urlopen(req)

                arguments["similar_images"] = u
                query_res = response.download(arguments)
                key = ""
                for j in query_res[0].keys():
                    key = j
                    break
                for url in query_res[0][key]:
                    self.total_urls.add(url)
                print('\x1b[6;30;42m' + "SCRAPING: " + str(round(i*100/ct, 2))
                      + '%\x1b[0m')
                i += 1
            except urllib.error.URLError as e:
                print(e)
                continue
            except urllib.error.HTTPError as e:
                print(e)
                continue
            except KeyboardInterrupt:
                raise
            except Exception as e:
                print(e)
                continue

        self.total_urls.union(init_urls_set)

    def download_urls(self):
        i = 1
        ct = len(self.total_urls)
        for url in self.total_urls:
            try:
                os.system("wget " + url)
                print('\x1b[6;30;42m' + "DOWNLOADING: " + str(round(i*100/ct, 2
                                                                    ))
                      + '%\x1b[0m')
                open("url_imgs.txt", "a").write(url+"\n")
                i += 1
            except KeyboardInterrupt:
                raise
            except Exception as e:
                print(e)

    def pipeline():
        self.url_media()
        self.download_urls()
