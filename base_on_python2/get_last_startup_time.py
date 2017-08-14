#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: Ro$es

import re
import time
import datetime


def parse_crontab_time(conf_string):
    """
    解析crontab时间配置参数
    Args:
    conf_string  配置内容(共五个值：分 时 日 月 周) 
                取值范围 分钟:0-59 小时:0-23 日期:1-31 月份:1-12 星期:0-6(0表示周日)
    Return:
    crontab_range	 list格式，分 时 日 月 周 五个传入参数分别对应的取值范围
    """
    time_limit = ((0, 59), (0, 23), (1, 31), (1, 12), (0, 6))
    crontab_range = []
    clist = []
    conf_length = 5
    tmp_list = conf_string.split(' ')

    # 这个循环，把字符串中的非空字符串保留下来
    for val in tmp_list:
        # print val
        if len(clist) == conf_length:
            break
        # 只保留非空字符串
        if val:
            clist.append(val)

    # 防止读入配置的列数不正确
    if len(clist) != conf_length:
        return -1, 'config error with [%s]' % conf_string
    cindex = 0
    for conf in clist:
        res_conf = []
        res_conf = parse_conf(conf, ranges=time_limit[cindex], res=res_conf)
        if not res_conf:
            return -1, 'config error whith [%s]' % conf_string
        crontab_range.append(sorted(res_conf))
        cindex = cindex + 1
    return 0, crontab_range


def parse_conf(conf, ranges=(0, 100), res=list()):
    """解析crontab 五个时间参数中的任意一个"""
    # 去除空格，再拆分
    conf = conf.strip(' ').strip(' ')
    conf_list = conf.split(',')
    other_conf = []
    number_conf = []
    for conf_val in conf_list:
        if match_cont(PATTEN['number'], conf_val):
            # 记录拆分后的纯数字参数
            number_conf.append(conf_val)
        else:
            # 记录拆分后纯数字以外的参数，如通配符 * , 区间 0-8, 及 0－8/3 之类
            other_conf.append(conf_val)

    if other_conf:
        # 处理纯数字外各种参数
        for conf_val in other_conf:
            for key, ptn in PATTEN.items():
                if match_cont(ptn, conf_val):
                    res = PATTEN_HANDLER[key](val=conf_val, ranges=ranges, res=res)
    if number_conf:

        if len(number_conf) > 1 or other_conf:
            # 纯数字多于1，或纯数字与其它参数共存，则数字作为时间列表
            res = handle_nlist(val=','.join(number_conf), ranges=ranges, res=res)
        else:
            # 只有一个纯数字存在，则数字为时间 间隔
            res = handle_num(val=number_conf[0], ranges=ranges, res=res)
    return res

def match_cont(patten, cont):
    """
    正则匹配(精确符合的匹配)
    Args:
        patten 正则表达式
        cont____ 匹配内容
    Return:
        True or False
    """
    res = re.match(patten, cont)
    if res:
        return True
    else:
        return False
 
def handle_num(val, ranges=(0, 100), res=list()):
    """处理纯数字"""
    val = int(val)
    if val >= ranges[0] and val <= ranges[1]:
        res.append(val)
    return res
 
def handle_nlist(val, ranges=(0, 100), res=list()):
    """处理数字列表 如 1,2,3,6"""
    val_list = val.split(',')
    for tmp_val in val_list:
        tmp_val = int(tmp_val)
        if tmp_val >= ranges[0] and tmp_val <= ranges[1]:
            res.append(tmp_val)
    return res
 
def handle_star(val, ranges=(0, 100), res=list()):
    """处理星号"""
    if val == '*':
        tmp_val = ranges[0]
        while tmp_val <= ranges[1]:
            res.append(tmp_val)
            tmp_val = tmp_val + 1
    return res
 
def handle_starnum(val, ranges=(0, 100), res=list()):
    """星号/数字 组合 如 */3"""
    tmp = val.split('/')
    # mod on 2017/6/14 
    # 在0分或者0点时任务依然执行。
    if ranges[1] == 59 or ranges[1] == 23 or ranges[1] == 6:
        res.append(0)
    #####
    val_step = int(tmp[1])
    if val_step < 1:
        return res
    val_tmp = int(tmp[1])
    while val_tmp <= ranges[1]:
        res.append(val_tmp)
        val_tmp = val_tmp + val_step
    return res
 
def handle_range(val, ranges=(0, 100), res=list()):
    """处理区间 如 8-20"""
    tmp = val.split('-')
    range1 = int(tmp[0])
    range2 = int(tmp[1])
    tmp_val = range1
    if range1 < 0:
        return res
    while tmp_val <= range2 and tmp_val <= ranges[1]:
        res.append(tmp_val)
        tmp_val = tmp_val + 1
    return res

def handle_rangedv(val, ranges=(0, 100), res=list()):
    """处理区间/步长 组合 如 8-20/3 """
    tmp = val.split('/')
    range2 = tmp[0].split('-')
    val_start = int(range2[0])
    val_end = int(range2[1])
    val_step = int(tmp[1])
    if (val_step < 1) or (val_start < 0):
        return res
    val_tmp = val_start
    while val_tmp <= val_end and val_tmp <= ranges[1]:
        res.append(val_tmp)
        val_tmp = val_tmp + val_step
    return res

def get_last_startup_time(cron = "25-50 17 14-27 6-9 *"):
    """
    计算计划任务上一个启动时间。
    Args:
        cron: 计划任务的启动周期
    Returns:
        last_startup_time: 上一个启动时间的timestamp
    """



    # 现在时间
    datetime_now = datetime.datetime.now()
    now = time.strftime("%M-%H-%d-%m-%w",time.localtime(time.time()))
    # print time.strftime("%Y-%m-%d-%H-%M",time.localtime(time.time()))
    # print datetime_now
    now = now.split("-")
    now_minite = int(now[0])
    now_hour = int(now[1])
    now_day = int(now[2])
    now_month = int(now[3])
    now_weekday = int(now[4])
    # print now_minite, now_hour, now_day, now_month, now_weekday

    # 算出计划任务的所有启动时间
    res, desc = parse_crontab_time(cron)
    if res == 0:
        cron_time = desc
    else: # res不为0即存在出错，输出错误信息
        print(desc)
        sys, exit(-1)
    
    small_month = [2,4,6,9,11]

    cron_minite = cron_time[0]
    cron_hour = cron_time[1]
    cron_day = cron_time[2]
    cron_month = cron_time[3]
    cron_weekday = cron_time[4]

    # print cron_minite
    # print cron_hour
    # print cron_day
    # print cron_month
    # print cron_weekday

    run_minite = int()
    run_hour = int()
    run_day = int()
    run_month = int()
    run_weekday = int()
    run_year = int()

    is_today = False # 今天是否执行任务标记

    year = time.strftime("%Y",time.localtime(time.time())) # 年份

    hour_push_front = False
    day_push_front = False
    month_push_front = False
    year_push_front = False

    # 计算分钟部分
    if now_hour in cron_hour and now_day in cron_day and now_month in cron_month: # 当月份、日期、小时都不在执行周期范围内时，分钟值毫无疑问是list的最后一个值
        if now_minite < cron_minite[0]: # 当现在的分钟比执行周期的分钟第一个值还要小，则上一次执行的分钟是执行周期分钟中的最后一个值
            run_minite = cron_minite[-1]
            # 此时，若现在小时在执行周期中，那么上次执行的小时就是现在小时往前推一位
            hour_push_front = True
        else:
            for i in range(len(cron_minite)):
                if cron_minite[i] <= now_minite:
                    run_minite = cron_minite[i]
    else:
        run_minite = cron_minite[-1]

    # 计算小时部分
    if now_day in cron_day and now_month in cron_month: # 当日期、月份都不在执行周期范围内时，小时值毫无疑问是list的最后一个值
        if now_hour < cron_hour[0]: # 当现在的小时比执行周期的小时第一个值还要小，则上一次执行的小时是执行周期小时中的最后一个值
            run_hour = cron_hour[-1]
            # 此时，若现在日期在执行周期中，那么上次执行的日期就是现在日期往前推一位
            day_push_front = True
        else:
            for i in range(len(cron_hour)):
                if cron_hour[i] <= now_hour:
                    run_hour = cron_hour[i] # 当前小时不在执行周期中时，不用推前。
                    if run_hour == now_hour and hour_push_front : # 若当前小时在执行周期中，而且处理分钟时导致小时往前推
                        run_hour = cron_hour[cron_hour.index(run_hour)-1]
                        if cron_hour.index(run_hour) == len(cron_hour) - 1: # 若小时从执行周期的小时List的第一位变为最后一位时，日期也要往前推
                            day_push_front = True
    else:
        run_hour = cron_hour[-1]
                
    # 计算日期部分
    if now_month in cron_month: # 当月份不在执行周期范围内时，日期值毫无疑问是list的最后一个值
        if now_day < cron_day[0]: # 当现在的日期比执行周期的日期第一个值还要小，则上一次执行的日期是执行周期日期中的最后一个值
            run_day = cron_day[-1]
            # 此时，若现在月份在执行周期中，那么上次执行的月份就是现在月份往前推一位
            month_push_front = True
        else:
            for i in range(len(cron_day)):
                if cron_day[i] <= now_day:
                    run_day = cron_day[i] # 当前日期不在执行周期中时，不用推前。
                    if run_day == now_day and day_push_front : # 若当前日期在执行周期中，而且处理小时时导致日期往前推
                        run_day = cron_day[cron_day.index(run_day)-1]
                        if cron_day.index(run_day) == len(cron_day) - 1: # 若日期从执行周期的日期List的第一位变为最后一位时，月份也要往前推
                            month_push_front = True
    else:
        run_day = cron_day[-1]
    
    # 计算月份部分
    if now_month < cron_month[0]: # 当现在的月份比执行周期的小时第一个值还要小，则上一次执行的小时是执行周期小时中的最后一个值
        run_month = cron_month[-1]
        # 此时，若现在日期在执行周期中，那么上次执行的日期就是现在日期往前推一位
        year_push_front = True
    else:
        for i in range(len(cron_month)):
            if cron_month[i] <= now_month:
                run_month = cron_month[i] # 当前小时不在执行周期中时，不用推前。
                if run_month == now_month and month_push_front : # 若当前小时在执行周期中，而且处理分钟时导致小时往前推
                    run_month = cron_month[cron_month.index(run_month)-1]
                    if cron_month.index(run_month) == len(cron_month) - 1: # 若小时从执行周期的小时List的第一位变为最后一位时，月份也要往前推
                        year_push_front = True

    # 计算年份
    if year_push_front:
        run_year = int(year) - 1
    else:
        run_year = year

    time_str = "%s-%s-%s-%s-%s" % (run_year, run_month, run_day, run_hour, run_minite)
    # print time_str

    # 计算星期
    if len(cron_weekday) != 7: # 当每周执行的天数不是7天时，星期的设置与月份、日期的设置是"或"的关系

        hour_push_front = False
        weekday_push_front = False

        # 找出距离今天最近的上一个执行任务的星期值
        now_weekday = int(time.strftime("%w",time.localtime(time.time()))) # 今天星期几
        # 计算分钟部分
        if now_hour in cron_hour and now_weekday in cron_weekday: # 当月份、日期、小时都不在执行周期范围内时，分钟值毫无疑问是list的最后一个值
            if now_minite < cron_minite[0]: # 当现在的分钟比执行周期的分钟第一个值还要小，则上一次执行的分钟是执行周期分钟中的最后一个值
                run_minite = cron_minite[-1]
                # 此时，若现在小时在执行周期中，那么上次执行的小时就是现在小时往前推一位
                hour_push_front = True
            else:
                for i in range(len(cron_minite)):
                    if cron_minite[i] <= now_minite:
                        run_minite = cron_minite[i]
        else:
            run_minite = cron_minite[-1]

        # 计算小时部分
        if now_weekday in cron_weekday: # 当日期、月份都不在执行周期范围内时，小时值毫无疑问是list的最后一个值
            if now_hour < cron_hour[0]: # 当现在的小时比执行周期的小时第一个值还要小，则上一次执行的小时是执行周期小时中的最后一个值
                run_hour = cron_hour[-1]
                # 此时，若现在日期在执行周期中，那么上次执行的日期就是现在日期往前推一位
                weekday_push_front = True
            else:
                for i in range(len(cron_hour)):
                    if cron_hour[i] <= now_hour:
                        run_hour = cron_hour[i] # 当前小时不在执行周期中时，不用推前。
                        if run_hour == now_hour and hour_push_front : # 若当前小时在执行周期中，而且处理分钟时导致小时往前推
                            run_hour = cron_hour[cron_hour.index(run_hour)-1]
                            if cron_hour.index(run_hour) == len(cron_hour) - 1: # 若小时从执行周期的小时List的第一位变为最后一位时，日期也要往前推
                                weekday_push_front = True
        else:
            run_hour = cron_hour[-1]

        if now_weekday < cron_weekday[0]:
            run_weekday = cron_weekday[-1]
        else:
            for i in range(len(cron_weekday)):
                if cron_weekday[i] <= now_weekday:
                    run_weekday = cron_weekday[i]
                    if run_weekday == now_weekday and weekday_push_front : # 若当前小时在执行周期中，而且处理分钟时导致小时往前推
                        run_weekday = cron_weekday[cron_weekday.index(run_weekday)-1]

        # print run_weekday
        # 计算run_weekday是几号
        run_weekday_date = datetime_now - datetime.timedelta(days=(now_weekday-run_weekday) % 7)
        # 将星期设置与月份日期设置所得到的上一个执行时间对比，
        run_weekday_date = datetime.datetime.strftime(run_weekday_date, "%Y-%m-%d")
        run_weekday_date = datetime.datetime.strptime("%s-%s-%s" % (run_weekday_date, run_hour, run_minite), "%Y-%m-%d-%H-%M")
        time_str_date = datetime.datetime.strptime(time_str, "%Y-%m-%d-%H-%M")
        # print run_weekday_date
        # print time_str_date

        # 若从星期设置算出的执行时间比从月份、日期设置算出的执行时间更靠近今天，那么从星期设置算出的执行时间就是上个执行时间
        if run_weekday_date > time_str_date:
            # print u"上一个执行时间为： %s" % (run_weekday_date)
            last_startup_time = time.mktime(run_weekday_date.timetuple())
            # print last_startup_time
        else:
            # print u"上一个执行时间为： %s" % (time_str_date)
            last_startup_time = time.mktime(time_str_date.timetuple())
            # print last_startup_time
    
    else:
        # print u"上一个执行时间为： %s" % (datetime.datetime.strptime(time_str, "%Y-%m-%d-%H-%M"))
        last_startup_time = time.mktime(datetime.datetime.strptime(time_str, "%Y-%m-%d-%H-%M").timetuple())
        
    return last_startup_time

#crontab时间参数各种写法 的 正则匹配
PATTEN = {
    #纯数字
    'number':'^[0-9]+$',
    #数字列表,如 1,2,3,6
    'num_list':'^[0-9]+([,][0-9]+)+$',
    #星号 *
    'star':'^\*$',
    #星号/数字 组合，如 */3
    'star_num':'^\*\/[0-9]+$',
    #区间 如 8-20
    'range':'^[0-9]+[\-][0-9]+$',
    #区间/步长 组合 如 8-20/3
    'range_div':'^[0-9]+[\-][0-9]+[\/][0-9]+$'
    #区间/步长 列表 组合，如 8-20/3,21,22,34
    #'range_div_list':'^([0-9]+[\-][0-9]+[\/][0-9]+)([,][0-9]+)+$'
}
#各正则对应的处理方法
PATTEN_HANDLER = {
    'number':handle_num,
    'num_list':handle_nlist,
    'star':handle_star,
    'star_num':handle_starnum,
    'range':handle_range,
    'range_div':handle_rangedv
}

if __name__ == "__main__":
    cron = "*/5 * * * *"
    last_startup_time = get_last_startup_time(cron)
    print "You cron expression: %s " % cron
    print "Now: %s " % time.strftime("%m-%d %H:%M",time.localtime(time.time()))
    print "Timestamp of last startup time: %s " % last_startup_time
    print "In readable way: %s " % time.strftime("%m-%d %H:%M",time.localtime(last_startup_time))