#!/usr/bin/env python
#encoding=utf-8
import time, sys, os
import re, json
import threading
import urllib, urllib2, cookielib
import conf

class CourseSelector(object):
    
    def __init__(self, username=None, 
            password=None, serveraddr=None,
            cookiefile='./config/courseselector.cookie',
            coursesetfile='./config/courseset.conf',
            coursefile='./config/self.__course.conf',
            xkviewstatefile='./config/xkviewstate.conf'):
        self.__username = username
        self.__password = password
        self.__serveraddr = serveraddr
        self.__cookiefile = cookiefile
        self.__coursesetfile = coursesetfile
        self.__coursefile = coursefile
        self.__xkviewstatefile = xkviewstatefile
        self.__infourl = 'http://' + self.__serveraddr + '/xs_main_zzjk.aspx?xh=' + self.__username
        self.__cookie = cookielib.MozillaCookieJar(self.__cookiefile)
        self.__header = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Charset':'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                'Accept-Encoding':'gzip,deflate,sdch',
                'Accept-Language':'en-US,en;q=0.8',
                'Cache-Control':'max-age=0',
                'Connection':'keep-alive',
                'Host':'','Referer':'',
                'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.110 Safari/537.36'}

        try:
        #加载已存在的cookie，尝试此cookie是否还有效
            self.__cookie.load(ignore_discard=True, ignore_expires=True)
            print 'cookie exited'
        except Exception:
        #加载失败，说明从未登录过，需登录并创建一个cookie文件
            self.__LoginSaveCookie(self.__password)

    def __LoginSaveCookie(self, password):
        '''登录并保存本地cookie'''
        self.__loginheader = self.__header
        self.__loginheader['HOST'] = self.__serveraddr
        self.__loginheader['Referer'] = self.__serveraddr + '/default_ldap.aspx'
        self.__loginurl = 'http://' + self.__serveraddr + '/default_ldap.aspx'
        tmpcontent = urllib2.urlopen(self.__loginurl).read().decode('gb2312').encode('utf-8')
        tmpviewstate = re.search('name="__VIEWSTATE" value="([^"]+)"', tmpcontent).group(1)
        #self.__SaveFile(tmpcontent, './html.html') #for test

        tmpdata = {'__VIEWSTATE':tmpviewstate, 'tbYHM':self.__username, 'tbPSW':password, 'Button1':' 登 录 '.decode('utf-8').encode('gb2312')}
        tmpdata = urllib.urlencode(tmpdata)
        tmpopener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.__cookie))
        tmpreq = urllib2.Request(self.__loginurl, tmpdata, self.__loginheader)
        tmpopener.open(tmpreq, tmpdata)
        self.__cookie.save(self.__cookiefile, ignore_discard=True,ignore_expires=True)

    def CourseSet(self):
        '''设置预选课程'''
        coursechoose = 0
        course = []
        while coursechoose != -1:
            try:
                coursenum = self.__show_course()
            except:
                print 'show_course error! Cancering...'
                time.sleep(1)
                continue

            print '请输入你要选择的课程, -1为退出预选课'
            coursechoose = raw_input('>')

            try:
                coursechoose = int(coursechoose)
            except:
                print '你的输入错误, 请重新输入...'
                continue

            if coursechoose == -1:
                print '正在退出预选课...'
                continue

            if coursechoose not in range(coursenum):
                print '你的输入错误, 请重新输入...'
                continue

            teacherchooselist = [0]
            while teacherchooselist[0] != -1:
                choosesuccess = False
                teacherchooselist = []
                teacherinfo = self.__show_teacher(coursechoose)

                print '请输入你要选择的老师(支持优先级模式, 先输入的老师优先级高, 用','分隔), -1为退出预选老师...'
                str_teacherchooselist = raw_input('>').split(',')

                for eachstr_teacherchoose in str_teacherchooselist:
                    #检测是否按规定格式输入, 是则转化为整型, 否则重新输入
                    try:
                        eachteacherchoose = int(eachstr_teacherchoose)
                    except:
                        print '输入无效，请重新输入...'
                        choosesuccess = False
                        break

                    if eachteacherchoose not in range(len(teacherinfo)):
                        print '你的输入错误, 请重新输入...'
                        choosesuccess = False
                        break

                    teacherchooselist.append(eachteacherchoose)
                    choosesuccess = True

                if choosesuccess == True:
                    teacherlist = []
                    for item in teacherchooselist:
                        teacherlist.append(teacherinfo[item][0])
                    coursetuple = (coursechoose, teacherlist)
                    course.append(coursetuple)
                    print course
                    teacherchooselist[0] = -1
        if len(course):
            jsoncourse = json.dumps(course)#使用json存储预选课表
            self.__SaveFile(jsoncourse, self.__coursesetfile)

    def __show_course(self):
        '''打印待选课程列表, 并返回待选课程数目'''
        self.__infoheader = self.__header
        self.__infoheader['Referer'] = self.__infourl
        tmpopener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.__cookie))
        try:
            tmpcontent = tmpopener.open(self.__infourl).read().decode('gb2312').encode('utf-8')
        except:
            print 'infourl open error! Cancering...'
            exit(-1)
        tmpaddr = re.search('href="(xsxk.aspx\?xh=[^"]+)',tmpcontent).group(1)
        self.__xkurl = 'http://' + self.__serveraddr + '/' + tmpaddr
        self.__xkurl = self.__xkurl.decode('utf-8').encode('gb2312')
        #self.__SaveFile(tmpcontent, './html.html') #for test

        tmpreqhandle = urllib2.Request(self.__xkurl, None, self.__infoheader)
        tmpcontent = tmpopener.open(tmpreqhandle, None).read().decode('gb2312').encode('utf-8')
        tmpviewstate = re.search('name="__VIEWSTATE" value="([^"]+)"', tmpcontent).group(1)
        #self.__SaveFile(tmpcontent, './html.html') #for test

        tmpdata = {'__EVENTTARGET':'','__EVENTARGUMENT':'','__VIEWSTATE':tmpviewstate,'DrDl_Nj':'2011','zymc':'0101通信工程主修专业'.decode('utf-8').encode('gb2312'),'Button5':'本专业选课'.decode('utf-8').encode('gb2312')}
        tmpdata = urllib.urlencode(tmpdata)
        self.__infoheader['Referer'] = self.__xkurl
        tmpreqhandle = urllib2.Request(self.__xkurl, tmpdata, self.__infoheader)
        tmpcontent = tmpopener.open(tmpreqhandle, tmpdata).read().decode('gbk').encode('utf-8')
        #self.__SaveFile(tmpcontent, './html.html') #for test
        
        self.__course = re.findall('onclick="window.open\(\'xsxjs.aspx\?xkkh=([^&]+)&xh=' + self.__username + '\',\'xsxjs\',\'toolbar=0,location=0,directories=0,status=0,menubar=0,scrollbars=1,resizable=1\'\)">([^<]+)</a>', tmpcontent)
        tmppage = re.findall('<a href="javascript:__doPostBack\(\'([^\']+)\',\'([^\']?)\'\)">', tmpcontent)
        tmpviewstate = re.search('name="__VIEWSTATE" value="([^"]+)"', tmpcontent).group(1)
        #print self.__course #for test
        #print tmppage #for test

        for iterator in range(len(tmppage)):
            tmptarget = ':'.join(tmppage[iterator][0].split('$'))
            tmpargument = tmppage[iterator][1]
            tmpdata = {'__EVENTTARGET':tmptarget, '__EVENTARGUMENT':tmpargument, '__VIEWSTATE':tmpviewstate, 'zymc':'0101通信工程主修专业||2011'.decode('utf-8').encode('gb2312'), 'xx':''}
            tmpdata = urllib.urlencode(tmpdata)
            tmpreqhandle = urllib2.Request(self.__xkurl, tmpdata, self.__infoheader)
            tmpcontent = tmpopener.open(tmpreqhandle, tmpdata).read().decode('gbk').encode('utf-8')
            tmpcourse = re.findall('onclick="window.open\(\'xsxjs.aspx\?xkkh=([^&]+)&xh=' + self.__username + '\',\'xsxjs\',\'toolbar=0,location=0,directories=0,status=0,menubar=0,scrollbars=1,resizable=1\'\)">([^<]+)</a>', tmpcontent)
            self.__course = self.__course + tmpcourse
            #print tmpcourse #for test 
            
        #保存self.__course为json格式文件, 方便选课时读取
        #print self.__course
        json__course = json.dumps(self.__course)
        self.__SaveFile(json__course, self.__coursefile)

        for iterator in range(len(self.__course)):
            if iterator%2 == 0:
                print "%d" % (iterator//2),
                print '、课程编号:' + self.__course[iterator][1]+'   ',
            else:
                print '课程名称:'+self.__course[iterator][1]

        return len(self.__course)/2

    def __get_courseurl(self):
        '''得到选课网址'''
        self.__courseurl = []

        for iterator in range(len(self.__course)):
            if iterator % 2 == 0:
                self.__courseurl.append('http://' + self.__serveraddr + '/xsxjs.aspx?xkkh=' + self.__course[iterator][0] + '&xh=' + self.__username)

    def __show_teacher(self, parmcourse):
        '''打印待选课程教师信息, 并返回列表'''
        self.__viewflag = 0
        self.__get_courseurl()
        
        tmpopener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.__cookie))
        tmpreqhandle = urllib2.Request(self.__courseurl[parmcourse], None, self.__infoheader)
        tmpcontent = tmpopener.open(tmpreqhandle, None).read().decode('gb2312').encode('utf-8')

        tmpcourseinfo = re.findall('onclick="window.open\(\'jsxx.aspx\?xh=' + self.__username + '&xkkh=([^&]+)&amp;jszgh=([^\']+)\',\'jsxx\',\'toolbar=0,location=0,directories=0,status=0,menubar=0,scrollbars=1,resizable=0\'\)" href="#" >([^<]+)</A>', tmpcontent)
        

        if self.__viewflag == 0 :
            tmptime = 1
            while self.__viewflag == 0:
                try:
                    self.__xkviewstate = re.search('name="__VIEWSTATE" value="([^"]+)"', tmpcontent).group(1)
                except:
                    time.sleep(tmptime)
                    tmptime <<= 1
                    continue
                #保存xkviewstate
                self.__SaveFile(self.__xkviewstate, self.__xkviewstatefile)
                self.__viewflag = 1

        for iterator in range(len(tmpcourseinfo)):
            print iterator,
            print '、 课程编号:' + tmpcourseinfo[iterator][0]+'   ',
            print '上课教师:' + tmpcourseinfo[iterator][2]

        return tmpcourseinfo

    def __threading_select(self, parmurl, parmdata, parmid):
        '''生成一个选课进程'''
        tmptarget = ':'.join('Button1'.split('$'))
        tmpdata = {'__EVENTTARGET':tmptarget, '__EVENTARGUMENT':'', '__VIEWSTATE':self.__xkviewstate, 'xkkh':None}
        tmpcourseurl = 'http://' + self.__serveraddr + '/xsxjs.aspx?xkkh=' + parmurl +'&xh=' + self.__username
        self.__xkheader['Referer'] = tmpcourseurl
        tmpopener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.__cookie))
        countlength = len(parmdata)#优先级表长度
        count = 0
        stopflag = False
        while (not stopflag ) and (count < countlength) :
            tmpdata = {'__EVENTTARGET':tmptarget, '__EVENTARGUMENT':'', '__VIEWSTATE':self.__xkviewstate, 'xkkh':None}
            tmpdata['xkkh'] = parmdata[count]
            tmpdata = urllib.urlencode(tmpdata)
            tmpreqhandle = urllib2.Request(tmpcourseurl, tmpdata, self.__xkheader)
            tmpcontent = tmpopener.open(tmpreqhandle, tmpdata).read().decode('gb2312').encode('utf-8')
            
            tmpre = re.search('五秒防刷', tmpcontent)
            if tmpre != None:
                time.sleep(6)
                continue

            tmpre = re.search('三秒防刷', tmpcontent)
            if tmpre != None:
                time.sleep(4)
                continue

            tmpre = re.search('Internal Server Error', tmpcontent)
            if tmpre != None:
                time.sleep(4)
                continue

                


            tmpre = re.search('Service Unavailable', tmpcontent)
            if tmpre != None:
                time.sleep(4)
                continue
            
            tmpre = re.search('人数超过限制', tmpcontent)
            if tmpre != None:
                print "%d号课程人数超过限制, 将选择另位一老师" % parmid
                count += 1
                time.sleep(1)
                continue
           
            tmpre = re.search('现在不是选课时间', tmpcontent)
            if tmpre != None:
                print "现在不是选课时间, 稍后重试"
                time.sleep(1)
                continue

            tmpre = re.search('上课时间冲突',tmpcontent)
            if tmpre != None:
                print "%d号课程上课时间冲突" % parmid
                stopflag = True
                continue

            tmpre = re.search('保存成功', tmpcontent)
            if tmpre != None:
                print "恭喜你, %d号课程保存成功, 选到%s老师" % (parmid, parmdata[count])
                stopflag = True
                continue


        self.__threadcnt -= 1
    
    def CourseSelect(self):
        '''迸发多进程选课'''
        try:
            jsoncourse = self.__ReadFile(self.__coursesetfile)
        except:
            print '预选课文件不存在, 正在退出...'
            exit(-1)
        course = json.loads(jsoncourse)
        
        try:
            json__course = self.__ReadFile(self.__coursefile)
        except:
            print "缺少配置文件'self.__course.conf', 预选课成功后可生成该文件, 正在退出..."
            exit(-1)
        self.__course = json.loads(json__course)
        
        try:
            self.__xkviewstate = self.__ReadFile(self.__xkviewstatefile)
        except:
            print "缺少配置文件'xkviewstate.conf', 预选课成功后可生成该文件, 正在退出..."
            exit(-1)
        

        self.__xkheader = self.__header
        self.__threadcnt = 0
        tmpitemlist = []

        for item in course:
            
            tmpthreadlist = []

            tmpthreadlist.append(threading.Thread(group=None, 
                target=self.__threading_select,
                name=self.__course[item[0]*2+1][0],
                args=(self.__course[item[0]*2+1][0],
                    item[1],item[0])))#其中item[1]为教师列表
            
            self.__threadcnt += 1

            for tmpthreaditem in tmpthreadlist:
                tmpthreaditem.start()
            
        while self.__threadcnt:
            for tmpthreaditem in tmpthreadlist:
                tmpthreaditem.join(0)
            time.sleep(1)
               

    def __SaveFile(self, content, filedirname):
        '''保存文件'''
        f = open(filedirname, 'w')
        f.write(content)
        f.close()
        if f.close:
            return True
        else:
            return False

    def __ReadFile(self, filedirname):
        '''读取文件'''
        f = open(filedirname, 'r')
        content = f.read()
        f.close()
        if f.close:
            return content
        else:
            return False