# _*_coding=utf-8_*_

import requests
import os
import json
from lxml import etree


def get_taobao_shop_by_goods_name(goodName):
    shops = []
    url = 'https://s.taobao.com/api?_ksTS=1503189695350_219&callback=jsonp220&ajax=true&m=customized&q=%s&s=36&imgfile=&bcoffset=0&commend=all&rn=0a54523512cdec785618ae85bd839881'%(goodName)
    try:
        data = requests.get(url)
        j_data =  json.loads(data.text.strip()[9:-2])
        auctions = j_data['API.CustomizedApi']['itemlist']['auctions']
        length = len(auctions)
        for i in range(3):
            shops.append('http:' + auctions[i]['detail_url'])
    except Exception as e:
        print(e)
    return shops

def getHtmlContent(url):
    data = None
    try:
        data = requests.get(url).text
    except Exception as e:
        print(e)
    return data


def js_filter(html):
    data = None
    try:
        selector = etree.HTML(html)
        data = selector.xpath('//script')
    except Exception as e:
        print(e)
    return data

def desc_img_filter(html):
    data = None
    try:
        selector = etree.HTML(html)
        data = selector.xpath('//img/@src')
    except Exception as e:
        print(e)
    data_s = []
    for d in data:
        if d[:4] != 'http':
            data_s.append('http:' + d)
        else :
            data_s.append(d)
    return data_s


def get_auction_images(shopurl):
    urls = []
    html = getHtmlContent(shopurl)
    if html is None:
        return None
    else:
        scripts = js_filter(html)

        if scripts is None:
            return None
        else:
            if shopurl[7:13] == 'detail':
                pass
            else :
                script = scripts[0].text
                lines = script.split('\n')
                for line in lines:
                    line = line.strip()
                    if len(line) > 13 and line[:13] == 'auctionImages':
                        temps = line.split(':')[-1].strip()[1:-1].split(',')
                        for i in temps:
                            if i[:4] != 'http':
                                urls.append('http:' + i[1:-1])
                            else :
                                urls.append(i[1:-1])
                        return urls





#获取商品描述的url
def get_shop_desc_url(shopurl):
    url = None
    html = getHtmlContent(shopurl)
    if html is None:
        return url
    else:
        scripts = js_filter(html)

        if scripts is None:
            return url
        else :
            if shopurl[7:13] == 'detail':
                script = scripts[22].text
                lines = script.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if line[:5] == '{"api':
                        j_data = json.loads(line)
                        return 'http:' + j_data['api']['descUrl']

            script = scripts[0].text
            lines = script.split('\n')
            for line in lines:
                line = line.strip()
                if len(line) > 7 and line[:7] == 'descUrl':
                    url = 'http:' + line.split(':')[-1].strip()[1:-1]

                    return url



def get_desc_imges(descUrl):
    desc_html = getHtmlContent(descUrl)

    if desc_html is None:
        return
    images = desc_img_filter(desc_html)
    return images


def download_imges(images, download_dir):
    if not os.path.exists(download_dir):
        try:
            os.makedirs(download_dir)
        except Exception as e:
            print(e)

    for i in images:
        try:
            data = requests.get(i)
            name = i.split('/')[-1]
            if name[-3:] != 'png' or name[-3:] != 'jpg':
                name = name.split('?')[0]
            with open(os.path.join(download_dir, name),  'wb') as fp:
                fp.write(data.content)
        except Exception as e:
            print("downloading %s erorr %s" %(i, e))



def do_fetch_taobao_img(goodName, dirname):
    shops = get_taobao_shop_by_goods_name(goodName)


    if shops is None:
        print('can not get shop list')
        exit()
    for shop in shops:
        desc_url = get_shop_desc_url(shop)
        auctions = get_auction_images(shop)
        if auctions is not None:
            download_imges(auctions, os.path.join(dirname, goodName))

        if desc_url is not None:
            images = get_desc_imges(desc_url)
            if images is not None:
                download_imges(images, os.path.join(dirname, goodName))