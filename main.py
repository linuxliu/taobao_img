

from helper import do_fetch_taobao_img

from goods import goods



if __name__ == '__main__':
    for good in goods:
        do_fetch_taobao_img(good, '.\images')
