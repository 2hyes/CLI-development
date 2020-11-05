# CLI-development
Crawling news and sns data to develope new Composite Leading Indicator(경기선행지수) 

1. 데이터셋 준비(save to db table)
```
python get-data.py
```
[get-data.py](https://github.com/2hyes/CLI-development/blob/master/get-data.py)에 네이버데이터랩 API client id, pw / 한국은행 openAPI api key / 저장할 database의 id, pw, db를 입력하면, 필요한 데이터셋이 모두 데이터베이스에 저장된다.

2. 예측
