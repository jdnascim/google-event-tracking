import requests
import os
import signal
import random
import shutil
import youtube_dl
import filetype
import glob
from newspaper import Article
from bs4 import BeautifulSoup


class full_coverage:
    def __init__(self, url, directory="./"):
        self.url = url
        self.links = None
        self.directory = directory

    @classmethod
    def fileplusextension(cls, path):
        """ It returns path + .extension (e.g. im/im1 -> im/im1.jpeg) """

        most_recent_file = ""
        most_recent_time = 0

        for i in glob.glob(path+"*"):
            time = os.path.getmtime(i)
            if time > most_recent_time:
                most_recent_file = i
        return most_recent_file

    @classmethod
    def __expandURL(self, link):
        """ returns "true" link to a page """
        try:
            return requests.get(link).url
        except Exception:
            return link

    @classmethod
    def __lastocc(cls, somestr, char):
        """ last occurence of a char in a string """

        if char in somestr:
            return max(i for i, c in enumerate(somestr) if c == char)
        else:
            return -1

    @classmethod
    def __handler_timeout(cls, signum, frame):
        """ just a timeout handler :) """

        print("timeout")
        raise Exception()

    @classmethod
    def __urlImageGenerator(cls, link):
        """ given a link, try to get images from it by the Article Library
        """

        try:
            a = Article(url=link)
            a.download()
            a.parse()
            a.fetch_images()

            for img in a.imgs:
                yield img
        except Exception:
            pass

    def full_cover_urls(self, real_url=True):
        """ given the google news full coverage of an event, get the urls """

        page = 1
        links = set()
        length = 0

        url = self.url

        urls = []
        if requests.get(url).url.startswith("https://news.google.com/"):
            while True:
                html = requests.get(url.format(page))
                soup = BeautifulSoup(html.content, "html.parser")
                links.update([a['href'] for a in soup.find_all('a',
                                                               href=True)])

                if len(links) == length:
                    break

                length = len(links)
                page += 1

            for link in sorted(links):
                if link.startswith("./article"):
                    urls.append(link)
        else:
            print("Not a Google News url")

        Surls = set(urls)

        if real_url is False:
            self.links = set(["https://news.google.com" + link[1:]
                              for link in Surls])
        else:
            self.links = set([requests.get(
                "https://news.google.com" + link[1:]).url for link in Surls])

    @classmethod
    def __youtube_download(cls, url, alarm=1000):
        try:
            # in order to avoid stalls in lives
            signal.signal(signal.SIGALRM, cls.__handler_timeout)
            signal.alarm(alarm)

            youtube_dl.YoutubeDL({}).download([url])
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(e)
        finally:
            signal.alarm(0)

    @classmethod
    def __request_download(cls, url, overwrite=False):
        for im in cls.__urlImageGenerator(url):
            try:

                if "base64," in im:
                    continue

                lo = cls.__lastocc(im, "/")+1

                if lo < len(im)-1:
                    output = im[cls.__lastocc(im, "/")+1:]
                else:
                    output = im[cls.__lastocc(im[:-1], "/")+1:-1]

                # random name
                if output == "" or len(output) > 80:
                    output = str(random.randint(1, 10000000000000))

                try:
                    if os.path.isfile(output) is False or overwrite is True:
                        open(output, "wb").write(requests.get(im).content)

                        if bool(filetype.guess_mime(output)) is True:
                            print(im, output)
                            return True
                        else:
                            return False
                    else:
                        print("File " + output + " exists.")
                        return False
                except KeyboardInterrupt:
                    if os.path.isfile(cls.fileplusextension(output)):
                        os.remove(cls.fileplusextension(output))
                    raise
                except Exception:
                    raise
            except requests.exceptions.ConnectionError as e:
                print(e)
                continue
            except requests.exceptions.InvalidSchema as e:
                print(e)
                continue

    def url_media(self, directory=None):
        """ scrap links """

        if directory is None:
            directory = self.directory

        setUrls = self.links

        if directory[-1] == '/':
            directory = directory[:-1]

        print(directory)
        try:
            os.mkdir(directory)
        except FileExistsError:
            pass

        seq = 1

        try:
            seqdir = os.path.realpath(directory + "/" + str(seq))

            # implemented in order to give a feedback about progresss %
            total_row = len(self.links)
            row_count = 0

            # iterate through each link
            for link in setUrls:
                row_count += 1

                url = self.__expandURL(link)

                print('\x1b[6;30;42m' + "Starting Scrapping for Link "
                      + str(url) + " (" + str(seq) + ")" + '\x1b[0m')

                os.mkdir(seqdir)
                os.chdir(seqdir)

                self.__youtube_download(url)

                self.__request_download(url)

                print('\x1b[6;30;42m' + "Scrap Finished for Link "
                      + str(url) + " ("
                      + str(round(row_count*100/total_row, 4)) + "%)"
                      + '\x1b[0m')

                os.chdir("../../")
                seq += 1
                seqdir = os.path.realpath(directory + "/" + str(seq))

        except KeyboardInterrupt:
            print("Stopping...")

            os.chdir(seqdir)
            shutil.rmtree(seqdir)
        except Exception as e:

            os.chdir(seqdir)
            shutil.rmtree(seqdir)
            print(e)
            raise
