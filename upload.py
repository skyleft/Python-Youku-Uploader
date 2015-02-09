# -*- coding: utf-8 -*-
__author__ = 'andy'

import  config
import os
import re
from threading import Thread,Lock
from youku import YoukuUpload
from youku.util import YoukuError
import indicator

youku = None
bar = -1
mutex = Lock()
isDone = False

#process indicator
def show_process(no):

    global youku,bar,isDone

    while True:
        mutex.acquire()
        if isDone:
            indicator.update(100)
            isDone = False
            mutex.release()
            return
        mutex.release()
        if youku.transferred and bar!=youku.transferred:
            indicator.update(int(youku.transferred*100/youku.file_size))
            bar = youku.transferred

def upload_main(file_info):
    global already,failed,youku,mutex,isDone
    mutex.acquire()
    isDone = False
    mutex.release()
    video_id = youku.upload(file_info)
    mutex.acquire()
    isDone = True
    mutex.release()
    if video_id:
        result_log.write("%s link:http://v.youku.com/v_show/id_%s.html\n" % (f['title'],video_id))
        already = already + 1
    else:
        failed_log.write('video:%s faild!!!!!!!!!!\n' % (f['title']))
        failed = failed + 1


available_format = (
    '.wmv','.avi','.dat','.asf','.rm','.rmvb','.ram','.mpg','.mpeg','.3gp'
    ,'.mov','.mp4','.m4v','.dvix','.dv','.mkv','.flv','.vob' ,'.ram' ,'.qt',
    '.divx', '.cpk', '.fli', '.flc', '.mod'
)

ready_for_upload_list = []
result_log = file('result.txt','w+')
failed_log = file('fail.txt','w+')

for i,v,hs in os.walk(config.UPLOAD_FOLDER):
    for h in hs:
        for an in available_format:
            if re.match(r'.*'+an+'$',h,re.IGNORECASE):
                ready_for_upload_list.append({
                    'title':h.split('.')[0],
                    'desc':h.split('.')[0],
                    'tag':'other',
                    'path':os.path.join(config.UPLOAD_FOLDER,h)
                })
total = len(ready_for_upload_list)
already = 0
failed = 0
access_token = ''
print "Found %d videos,start uploading now." % (total)
if not config.CODE:
    print 'CODE is empty,please get the code first.'
    import sys
    sys.exit(-1)
print 'Geting the access token.'
tf = file('token.txt','r')
for tfl in tf:
    access_token = tfl
if not access_token:
    print 'No existed token,try to get a new one.'
    import auth
    try:
        access_token = auth.get_access_token_by_code(config.CODE)
    except YoukuError,e:
        print e
        print 'Failed to get an access token.'
        import sys
        sys.exit(-1)
    access_token = access_token['access_token']
    tf = file('token.txt','w+')
    tf.write(access_token)
    tf.close()
if not access_token:
    print 'Failed to get an access token'
    import sys
    sys.exit(-1)
print 'Access token is good, start uploading now, please be patient!'
print '-------------------------------------------------------------'
for f in ready_for_upload_list:
    file_info = {
        'title': f['title'],
        'tags': f['tag'],
        'description': f['desc']
    }
    youku = YoukuUpload(config.CLIENT_ID, access_token, f['path'])

    t1 = Thread(target=upload_main,args=(file_info,))
    t2 = Thread(target=show_process,args=(None,))
    t2.start()
    t1.start()
    t2.join()
    t1.join()

    print "\n%d videos have been processed, %d are finished, %d are failed, %d left." % (already+failed,already,failed,total-already-failed)
    print 'go to next'
