import pandas as pd
import pymysql
from urllib.request import urlopen
from bs4 import BeautifulSoup
import json
from datetime import datetime, date,timedelta
import os
import sys
import urllib.request
import re

## functions
# function that deal with date
"""
google: week를 sunday to saturday로 설정
--> 날짜를 하루씩 더함
"""
def plus_one_day(googletrends_df):
    date2 = []
    for i in range(len(googletrends_df)):
        after_one_day = datetime.strptime(googletrends_df.iloc[i].date, '%Y-%m-%d').date() + timedelta(days=1)
        after_one_day = after_one_day.strftime("%Y-%m-%d")
        date2.append(after_one_day)
    return date2

"""
db에 저장할 때, 
date를 년, 월, 일로 저장해서 반환
"""
def getDate(df_row):
    date = str(df_row)
    year = date[0:4]
    month = date[4:6]
    day = date[6:9]
    return int(year), int(month), int(day)

"""
날짜에서 year, month, day 추출
"""
def extract_year_and_month_day(period):
    year = period.split('-')[0]
    month = period.split('-')[1]
    day = period.split('-')[2]
    return year, month, day

def extract_year_and_month(period):
    year = period[0:4]
    month = period[4:6]
    return year, month

# get files
def getPortalTrendsFiles (): 
    # kakao trend
    kakaotrends_df = pd.read_csv('./data/kakaotrend.csv', header=7, sep=',', skip_blank_lines = True)
    kakaotrends_df = kakaotrends_df.rename({'일': 'date', '경제':'kakao'}, axis = 'columns')
    kakaotrends_df = kakaotrends_df[0:147]
    # google trend
    googletrends_df = pd.read_csv('./data/googletrend.csv', header=1, sep=',', skip_blank_lines = True)
    googletrends_df = googletrends_df.rename({'주': 'date', '경제: (대한민국)':'google'}, axis = 'columns')
    googletrends_df['date'] = plus_one_day(googletrends_df)
    return kakaotrends_df, googletrends_df

def getNaverDatalabAPI(client_id, client_secret):
    # naver datalab
    start_date = '2016-01-01'
    today = date.today().strftime('%Y-%m-%d')
    url = "https://openapi.naver.com/v1/datalab/search";
    body = "{\"startDate\":\""+start_date+"\",\"endDate\":\""+today+"\",\"timeUnit\":\"week\",\"keywordGroups\":[{\"groupName\":\"경제\",\"keywords\":[\"경제\"]}]}";

    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id",client_id)
    request.add_header("X-Naver-Client-Secret",client_secret)
    request.add_header("Content-Type","application/json")
    response = urllib.request.urlopen(request, data=body.encode("utf-8"))
    rescode = response.getcode()
    if(rescode==200):
        response_body = response.read()
        scrapped = response_body.decode('utf-8')
    else:
        print("Error Code:" + rescode)

    jsonResult = json.loads(scrapped)
    navertrends_df = pd.DataFrame(jsonResult['results'][0]['data'])
    navertrends_df = navertrends_df.rename({'period': 'date', 'ratio':'naver'}, axis = 'columns')
    
    return navertrends_df

def get3TrendsTable(googletrends_df, kakaotrends_df, navertrends_df):
    tmp = pd.merge(googletrends_df, kakaotrends_df, how='left')
    portaltrends_df = pd.merge(tmp, navertrends_df, how='left')
    portaltrends_df = portaltrends_df.fillna(0)
    return portaltrends_df

def getNewsCountingFiles():
    # news counting
    news_df = pd.read_json('./data/bigkinds.json')

    return news_df


def createTables():
    # portal trends
    create_table_query = """
    CREATE TABLE IF NOT EXISTS portal_trends_ratio(
        id BIGINT(7) NOT NULL AUTO_INCREMENT,
        year bigint(4) NOT NULL,
        month bigint(2) NOT NULL,
        day bigint(2) NOT NULL,
        google double,
        kakao double,
        naver double,
        primary key(id) )
        charset=utf8mb4;
    """
    cur.execute(create_table_query)
    
    # newscounting    
    create_table_query = """
    CREATE TABLE IF NOT EXISTS news_counting(
        id BIGINT(7) NOT NULL AUTO_INCREMENT,
        year bigint(4) NOT NULL,
        month bigint(2) NOT NULL,
        day bigint(2) NOT NULL, 
        keyword1 bigint(100),
        keyword2 bigint(100),
        keyword3 bigint(100),
        keyword4 bigint(100),
        keyword5 bigint(100),
        primary key(id) )
        charset=utf8mb4;
    """
    cur.execute(create_table_query)
    
    # ccsi
    create_table_query = """
    CREATE TABLE IF NOT EXISTS ccsi(
        id BIGINT(7) NOT NULL AUTO_INCREMENT,
        year bigint(4) NOT NULL,
        month bigint(2) NOT NULL,
        ccsi double,
        primary key(id) )
        charset=utf8mb4;
    """
    cur.execute(create_table_query)

    # cci
    create_table_query = """
    CREATE TABLE IF NOT EXISTS coincident_composite_index(
        id BIGINT(7) NOT NULL AUTO_INCREMENT,
        year bigint(4) NOT NULL,
        month bigint(2) NOT NULL,
        cci double,
        primary key(id) )
        charset=utf8mb4;
    """
    cur.execute(create_table_query)    


def insertRecords(portaltrends_df, news_df, ccsi, cci):
    # portal trends
    for i in range(len(portaltrends_df)):
        query = """ 
        Insert into portal_trends_ratio (year, month, day, google, kakao, naver) values (%d, %d, %d, %f, %f, %f) ;
        """
        year, month, day = extract_year_and_month_day(portaltrends_df.iloc[i].date)
        google_cnt = portaltrends_df.iloc[i].google
        kakao_cnt = portaltrends_df.iloc[i].kakao
        naver_cnt = portaltrends_df.iloc[i].naver

        mystring = (query % (int(year), int(month), int(day), float(google_cnt), float(kakao_cnt), float(naver_cnt)))
        print(mystring)
        cur.execute(mystring)
    
    # news counting
    for i in range(len(news_df)):
        query = """ 
        Insert into news_counting (year, month, day, keyword1, keyword2, keyword3, keyword4, keyword5 ) values (%d, %d, %d, %d, %d, %d, %d, %d) ;
        """
        year, month, day = getDate(news_df.iloc[i]['date'])
        keyword1_cnt = news_df.iloc[i]['침체']
        keyword2_cnt = news_df.iloc[i]['금융위기']
        keyword3_cnt = news_df.iloc[i]['불황']
        keyword4_cnt = news_df.iloc[i]['폭락']
        keyword5_cnt = news_df.iloc[i]['외환위기']

        mystring = ( query % (year, month, day, keyword1_cnt, keyword2_cnt, keyword3_cnt, keyword4_cnt, keyword5_cnt) )
        if (i % 10 == 0):
            print(mystring)
        cur.execute(mystring)
    
    # ccsi
    for i in range(len(ccsi)):
        query = """ 
        Insert into ccsi (year, month, ccsi) values (%d, %d, %f) ;
        """
        year, month = extract_year_and_month(ccsi.iloc[i].TIME)
        ccsi_value = ccsi.iloc[i].DATA_VALUE

        mystring = (query % (int(year), int(month), float(ccsi_value)))
        print(mystring)
        cur.execute(mystring)

    ## cci    
    for i in range(len(cci)):
        query = """ 
        Insert into coincident_composite_index (year, month, cci) values (%d, %d, %f) ;
        """
        year, month = extract_year_and_month(cci.iloc[i].TIME)
        coincident_value = cci.iloc[i].DATA_VALUE

        mystring = (query % (int(year), int(month), float(coincident_value)))
        print(mystring)
        cur.execute(mystring)

def getEcosAPI(API_KEY, code, max, start_month, end_month):
    url = 'http://ecos.bok.or.kr/api/StatisticSearch/%s/json/kr/1/%s/%s/MM/%s/%s/?/?/?/' % (API_KEY, max, code, start_month, end_month)
    result = urlopen(url)
    html = result.read()
    
    return json.loads(html)

def getCCSI(API_KEY):
    data = getEcosAPI(API_KEY, code = '040Y002', max = 100000, start_month = '201509', end_month = '202011')["StatisticSearch"]["row"]
    produce = pd.DataFrame(data)
    ccsi = produce[produce['ITEM_CODE1'] == 'FME'] # CCSI는 item_code1 'FME'
    ccsi = ccsi.loc[:, ['TIME', 'DATA_VALUE']].reset_index(drop=True)
    return ccsi

def getCCI(API_KEY):
    data = getEcosAPI(API_KEY, code = '085Y026', max = 100000, start_month = '201509', end_month = '202011')["StatisticSearch"]["row"]
    produce = pd.DataFrame(data)
    cci = produce[produce['ITEM_CODE1'] == 'I16D'] # CCI는 item_code1 'I16D'
    cci = cci.loc[:, ['TIME', 'DATA_VALUE']].reset_index(drop=True)
    return cci



## main
# DB connection
conn = pymysql.connect(host = "127.0.0.1", user = [USER], passwd = [PASSWORD], db = [DATABASE], cursorclass = pymysql.cursors.DictCursor)
cur = conn.cursor()

cur.execute("show databases")
print(cur.fetchall())
cur.execute("use CLI")

# load data
kakaotrends_df, googletrends_df = getPortalTrendsFiles()
navertrends_df = getNaverDatalabAPI(client_id, client_secret)
portaltrends_df = get3TrendsTable(googletrends_df, kakaotrends_df, navertrends_df)
news_df = getNewsCountingFiles()
    
# 소비자심리지수, 소비자 동행지수 df 생성
API_KEY = "YOUR_API_KEY"
ccsi = getCCSI(API_KEY)
cci = getCCI(API_KEY)

# create table
createTables()

# insert records to table
insertRecords(portaltrends_df, news_df, ccsi, cci)

# db connection close
conn.commit()
cur.close()
conn.close()
