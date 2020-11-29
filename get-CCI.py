from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import json
import pymysql

"""
한국은행 openAPI를 활용하여
경기동행지수 받아옴
"""
def getEcosAPI(API_KEY, code, max, start_month, end_month):
    url = 'http://ecos.bok.or.kr/api/StatisticSearch/%s/json/kr/1/%s/%s/MM/%s/%s/?/?/?/' % (API_KEY, max, code, start_month, end_month)
    result = urlopen(url)
    html = result.read()
    
    return json.loads(html)

data = getEcosAPI(API_KEY = "YOUR_API_KEY", code = '085Y026', max = 100000, start_month = '200807', end_month = '202011')
data = data["StatisticSearch"]["row"]
produce = pd.DataFrame(data)
cci = produce[produce['ITEM_CODE1'] == 'I16D']
cci = cci.loc[:, ['TIME', 'DATA_VALUE']].reset_index(drop=True)

# 날짜에서 year, month 추출 함수
def extract_year_and_month(period):
    year = period[0:4]
    month = period[4:6]
    return year, month

"""
DB 
"""
## DB연동
conn = pymysql.connect(host = "127.0.0.1", user = [USER], passwd = [PASSWORD], db = [DATABASE])
cur = conn.cursor()

## Coincident Composite Index 저장할 table 생성
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


## table 저장
for i in range(len(cci)):
    query = """ 
    Insert into coincident_composite_index (year, month, cci) values (%d, %d, %f) ;
    """
    year, month = extract_year_and_month(cci.iloc[i].TIME)
    coincident_value = cci.iloc[i].DATA_VALUE

    mystring = (query % (int(year), int(month), float(coincident_value)))
    print(mystring)
    cur.execute(mystring)

conn.commit()
cur.close()
conn.close()