import json
import random

import requests
import io
from bs4 import BeautifulSoup as BS
import time
import pandas as pd
from lxml import etree
import re
import math
import urllib3

cookies = {

}

proxies = {
    "http": "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890",
}

user_agent_list = ["Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
                    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
                    "Mozilla/5.0 (Windows NT 10.0; WOW64) Gecko/20100101 Firefox/61.0",
                    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36",
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36",
                    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
                    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
                    "Mozilla/5.0 (Macintosh; U; PPC Mac OS X 10.5; en-US; rv:1.9.2.15) Gecko/20110303 Firefox/3.6.15",
                    ]

headers = {
    "Origin": "https://bangumi.tv/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

requests.adapters.DEFAULT_RETRIES = 5

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

root_url = 'https://bangumi.tv/'


def getRankPageUrl(url):
    # root_url = 'https://bangumi.tv/'
    root_result = requests.get(url, headers=headers, verify=False, proxies=proxies)
    root_html = root_result.text
    root_soup = BS(root_html, 'lxml')
    rank_page_url = root_soup.find('ul', class_='clearit').find('a', class_='nav')['href']
    return rank_page_url


def getAnimePageUrl(url):
    urls = []
    root_result = requests.get(url, headers=headers, verify=False, proxies=proxies)
    root_html = root_result.text
    root_soup = BS(root_html, 'lxml')
    rank_page_urls = root_soup.find('ul', class_='browserFull')
    for rank_page_url in rank_page_urls:
        paths = rank_page_url.find_all('a', class_='subjectCover cover ll')
        for path in paths:
            urls.append(root_url + path['href'])
    return urls


def getTotalPage(url):
    root_result = requests.get(url, headers=headers, verify=False, proxies=proxies)
    root_html = root_result.text
    root_soup = BS(root_html, 'lxml')
    text = root_soup.find('div', class_='page_inner').find('span', class_='p_edge').text
    page_num = re.findall(r"\d+", text)[1]
    return page_num


def getAnimeName(url):
    root_result = requests.get(url, headers=headers, verify=False)
    root_result.encoding = 'utf-8'
    root_html = root_result.text
    root_soup = BS(root_html, 'lxml')
    anime_name_origin = root_soup.find('div', class_='infobox_container').find('li').text.split(":")[1]
    anime_name = anime_name_origin[1:]
    return anime_name


def getAnimeScore(url):
    root_result = requests.get(url, headers=headers, verify=False)
    root_result.encoding = 'utf-8'
    root_html = root_result.text
    root_soup = BS(root_html, 'lxml')
    anime_score = root_soup.find('div', class_='global_score').find('span', class_='number').text
    return anime_score


def getAnimeInfo(url):
    infoms = []
    root_result = requests.get(url, headers=headers, verify=False, proxies=proxies)
    root_result.encoding = 'utf-8'
    root_html = root_result.text
    root_soup = BS(root_html, 'lxml')
    infos = root_soup.find('div', class_='infobox_container').find_all('li')
    for info in infos:
        infoms.append(info.text)
    return infoms


def getAnimeDirector(infos):
    for info in infos:
        text = info.split(': ')
        if text[0] == "导演":
            return text[1]
        else:
            continue


def getAnimeYear(infos):
    for info in infos:
        text = info.split(': ')
        if text[0] == "放送开始":
            return text[1][0:4]
        else:
            continue


def getAnimeCompany(infos):
    for info in infos:
        text = info.split(': ')
        if text[0] == "动画制作":
            return text[1]
        else:
            continue


def getAnimeTagAndWeight(url):
    tags = []
    weights = []
    root_result = requests.get(url, headers=headers, verify=False, proxies=proxies)
    root_result.encoding = 'utf-8'
    root_html = root_result.text
    root_soup = BS(root_html, 'lxml')
    anime_tags = root_soup.find('div', class_='subject_tag_section').find_all('span')
    tag_weights = root_soup.find('div', class_='subject_tag_section').find_all('small')
    for anime_tag in anime_tags:
        tag = anime_tag.text
        tags.append(tag)
    for tag_weight in tag_weights:
        weight = tag_weight.text
        weights.append(weight)
    name_to_tag = []
    for i in range(0, len(tags)):
        pair = (tags[i], weights[i])
        name_to_tag.append(pair)
    return name_to_tag


def getAnimeTag(url):
    tags = []
    root_result = requests.get(url, headers=headers, verify=False, proxies=proxies)
    root_result.encoding = 'utf-8'
    root_html = root_result.text
    root_soup = BS(root_html, 'lxml')
    anime_tags = root_soup.find('div', class_='subject_tag_section').find_all('span')
    for anime_tag in anime_tags:
        tag = anime_tag.text
        tags.append(tag)
    return tags


def getMAnimeUrl(end_page: int, begin_page=1):
    origin_url = 'https://bangumi.tv/anime/browser?sort=rank&page='
    anime_urls = []
    for i in range(begin_page, end_page):
        url = origin_url + str(i)
        anime_urls = anime_urls + getAnimePageUrl(url)
        # anime_urls.append(getAnimePageUrl(url))
    return anime_urls


def getMAnimeUrl_f(begin_page: int, end_page: int):
    return getMAnimeUrl(end_page, begin_page)


def isIncludeTag(url, tar_tags):
    anime_tags = getAnimeTag(url)
    for tar_tag in tar_tags:
        for anime_tag in anime_tags:
            if tar_tag == anime_tag:
                break
            if tar_tag != anime_tag and anime_tag == anime_tags[-1]:
                return False
    return True


if __name__ == '__main__':
    rank_url = root_url + getRankPageUrl(root_url)
    animeUrls = getAnimePageUrl(rank_url)
    page_num = getTotalPage(rank_url)
    infoms = getAnimeInfo('https://bangumi.tv/subject/326')
    tags = ['原创', '日常']
    print(isIncludeTag('https://bangumi.tv/subject/110467', tags))
    # director_name = getAnimeCompany(infoms)
    # getAnimeTagAndWeight('https://bangumi.tv/subject/326')
    # print(getMAnimeUrl_f(1, 4))
    key_word = '青春'
