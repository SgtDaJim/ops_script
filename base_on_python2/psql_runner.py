#!/usr/bin/python
# -*- coding:utf-8 -*-
# Author: Ro$es

import psycopg2
import psycopg2.extras


class PostgresqlRunner(object):
    """Postgresql连接类，同时也能连接AWS Redshift。"""
    def __init__(self, host, user, pwd, db, port=5432):
        self.host = host
        self.port = port
        self.user = user
        self.pwd = pwd
        self.db = db
        self.conn = psycopg2.connect("host=%s port=%s user=%s password=%s dbname=%s" % (self.host, self.port, self.user, self.pwd, self.db))
        self.cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    def sql_runner(self, sql):
        """执行sql语句。
        Return:
            result: sql执行结果。（列表[字典]）
        """
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return result