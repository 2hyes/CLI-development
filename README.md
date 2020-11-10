# CLI-development

- 목표: Use news counting and portal trends(google,naver,kakao) data to develope new Composite Leading Indicator(경기선행지수) \ 

주간 데이터들을 수집하여, 월간 경제 지표인 소비자심리지수를 예측한다.
예측 모델에 주간 레코드들을 집어넣어, 주간 경제 지표 값들을 내도록 한다.

1. 데이터셋 준비(save to db table)
```
python get-data.py
```
[get-data.py](https://github.com/2hyes/CLI-development/blob/master/get-data.py)에 네이버데이터랩 API client id, pw / 한국은행 openAPI api key / 저장할 database의 id, pw, db를 입력하면, 필요한 데이터셋이 모두 데이터베이스에 저장된다.

데이터 수집 과정
부정적 경제 상황 키워드를 포함하는 뉴스 기사 수
: 빅카인즈에서 json 파일 다운로드

포털 트렌드의 '경제' 검색량 비율
- 구글: 구글 트렌드에서 csv 파일 다운로드
- 네이버: 네이버 데이터랩 openAPI 활용
- 카카오: 카카오 트렌드에서 excel 파일 다운로드
소비자심리지수, 경기동행지수 순환변동치
: 한국은행 경제통계시스템 API 활용



2. 예측
