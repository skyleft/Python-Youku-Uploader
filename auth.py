# -*- coding: utf-8 -*-
__author__ = 'andy'

from youku import youku_oauth
import config

def get_access_token_by_code(code):
    yo = youku_oauth.YoukuOauth(config.CLIENT_ID,config.CLIENT_SECRET,config.REDIRECT_URL)
    return yo.get_token_by_code(code)


if __name__ == '__main__':
    print get_access_token_by_code('code')
