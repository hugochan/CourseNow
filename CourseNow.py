#!/usr/bin/env python
#encoding=utf-8
import os, time
import conf
from CourseSelector import CourseSelector

if __name__ == '__main__':
    serverlist = conf.xkserver.split('|')
    cookieflie = './config/courseselector.cookie'
    coursesetfile = './config/courseset.conf'
    loginstate = 0
    cxfail = 10
    username = ''
    password = ''

    print "***********************************************"
    print "**************CourseNow v1.0*******************"
    print "***********************************************"


    print "输入学号..."
    username = raw_input('> ')

    if not os.path.exists('./config/courseselector.cookie'):
        print "输入密码..."
        password = raw_input('> ')

    while loginstate == 0:
        try:
            courseselector = CourseSelector(username, password, serverlist[(cxfail-1)%4])
            loginstate = 1
            print 'login sucessful'
        except:
            if cxfail :
                print '连接失败error %s' % (11-cxfail)
                #print '由于网络的原因，连接失败，%d秒后重试' % wait
                time.sleep(6)#5秒防刷
                cxfail -= 1
            else:
                print '连接失败error, 正在退出...'
                #print '连接超时，正在退出'
                exit(-1)

    while not os.path.isfile(coursesetfile):
        print "预选课文件不存在，是否先进行预选课(Y or N)"
        choose = raw_input('> ')
        if choose == 'Y':
            courseselector.CourseSet()
        elif choose == 'N':
            print "正在退出..."
            exit(-1)
        else:
            print '输入错误, 请重新输入...'
            continue

    print "预选课文件已存在，是否需要重新配置?(Y or N)"
    choose = raw_input('> ')
    if choose == 'Y':
        courseselector.CourseSet()

    print "是否开始选课?(Y or N)"
    choose = raw_input('> ')
    if choose == 'Y':
        courseselector.CourseSelect()
        print '恭喜你, 所有选课已全部完成'
    else:
        print "正在退出..."
        exit(-1)