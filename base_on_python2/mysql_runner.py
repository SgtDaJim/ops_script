#!/usr/bin/python
# -*- coding:utf-8 -*-
# Author: Ro$es

import mysql.connector


class MysqlRunner(object):
    """Mysql连接类。"""
    def __init__(self, host, user, pwd, db, port=3306):
        self.host = host
        self.user = user
        self.pwd = pwd
        self.db = db
        self.port = port
        self.conn = mysql.connector.connect(user=self.user, password=self.pwd, host=self.host, database=self.db, port=self.port)
        self.cursor = self.conn.cursor(dictionary=True)

    def sql_runner(self, sql):
        """执行sql语句。
        Return:
            result: sql执行结果（列表[字典]）
        """
        self.cursor.execute(sql)
        result = list()
        for r in self.cursor:
            result.append(r)

        return result