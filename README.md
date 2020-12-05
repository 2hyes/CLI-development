# CLI-development
## 1. Overview

- 목표: Use news counting and portal trends(google,naver,kakao) data to develope new Composite Leading Indicator <br>
뉴스기사수와 포털 트렌드의 주간 데이터들을 수집하여, 월간 경제 지표인 소비자심리지수를 예측하여 새로운 주간 경제심리보조지수를 개발한다. 

- 데이터: 
  - 부정적 경제 상황 키워드를 포함하는 뉴스 기사 수
  : 빅카인즈에서 json 파일 다운로드
  - 포털 트렌드의 '경제' 검색량 비율
    - 구글: 구글 트렌드에서 csv 파일 다운로드
    - 네이버: 네이버 데이터랩 openAPI 활용
    - 카카오: 카카오 트렌드에서 excel 파일 다운로드
  - 소비자심리지수(CCSI), 경기동행지수(CCI) 순환변동치
  : 한국은행 경제통계시스템 API 활용

  - 파일 소개
```
  📦CLI-development
 ┣ 📂data
 ┃ ┣ 📜all-news.csv
 ┃ ┣ 📜bigkinds.json
 ┃ ┣ 📜googletrend.csv
 ┃ ┗ 📜kakaotrend.csv
 ┣ 📂dataset
 ┃ ┣ 📂dataset_mean
 ┃ ┃ ┣ 📜ccsi.pkl
 ┃ ┃ ┣ 📜predictors.pkl
 ┃ ┃ ┣ 📜X_test.pkl
 ┃ ┃ ┣ 📜X_train.pkl
 ┃ ┃ ┣ 📜y_test.pkl
 ┃ ┃ ┗ 📜y_train.pkl
 ┃ ┣ 📂dataset_interpolation
 ┃ ┗ 📂dataset_median
 ┣ 📂getTrainTestSet
 ┃ ┣ 📜getTrainTestSet.py
 ┃ ┣ 📜getTrainTestSet_interpolation.py
 ┃ ┗ 📜getTrainTestSet_median.py
 ┣ 📜check-google-trends-with-CCI.ipynb
 ┣ 📜demonstrate_CLI-validity.ipynb
 ┣ 📜final_model.pkl
 ┣ 📜final_scaler.pkl
 ┣ 📜final_table.pkl
 ┣ 📜get-data.py
 ┣ 📜validation-and-Ttest(dataset_interpolation).ipynb
 ┣ 📜validation-and-Ttest(dataset_interpolation_shuffle).ipynb
 ┣ 📜validation-and-Ttest(dataset_mean).ipynb
 ┣ 📜validation-and-Ttest(dataset_mean_shuffle).ipynb
 ┣ 📜validation-and-Ttest(dataset_median).ipynb
 ┗ 📜validation-and-Ttest(dataset_median_shuffle).ipynb
```

- 고려한 전처리 및 데이터 분할 방법

  i. 주간 데이터를 월간 데이터로 변환 
    - 해당 달의 주간 변수값들의 평균
    - 해당 달의 주간 변수값들의 중앙값
    - 월간 지표인 CCSI에 선형보간법을 적용하여, 주간 데이터에 true y를 생성 

  ii. 트레이닝 테스트셋 분할(split train, testset)
    - random으로 섞어서, 분할
    - 시간의 흐름대로, 2016 ~ 2019년을 training set, 2020년을 test set으로 분할

- 고려한 예측 모델 <br>
y(월말에 제공되는 CCSI), yhat(주간 데이터 레코드로 CCSI를 예측한 값)
: 해당 월의 주차들 레코드들의 평균값들을 데이터셋으로 활용
    - multiple linear regression
    - lasso regression
    - random forest
    - GAMs for regression

| model | parameter | training RMSE | test RMSE | code |
|----------|:-----------:|:-------:|:----------------:|:----------------:|
| Multiple linear regression |  | 4.64 | 2.65 | [코드](https://github.com/2hyes/CLI-development/blob/master/prediction-multiregression.ipynb) |
| Lasso linear regression |  |  |  |  |
| Random forest |  |  |  | [코드](https://github.com/2hyes/CLI-development/blob/master/prediction-randomforest.ipynb) |
| GAMS |  |  |  |  |

## 2. Development environment
1) 개발 환경
- WSL Ubuntu-18.04 ver2.
2) 개발 언어
- Python 
3) 라이브러리
- pandas 1.0.5
- pymysql 0.9.2
- urlib3 1.25.9
- BeautifulSoup 4.9.1
- matplotlib 3.2.2

## 3. Reproduce results
: 최종 선택한 방법과 모델의 코드 재현 방법

#### 1) 데이터셋 준비(save to db table)
```
python get-data.py
```
[get-data.py](https://github.com/2hyes/CLI-development/blob/master/get-data.py)에 네이버데이터랩 API client id, pw / 한국은행 openAPI api key / 저장할 database의 id, pw, db를 입력하면, 필요한 데이터셋이 모두 데이터베이스에 저장된다.

#### 2) 데이터 전처리(data preprocessing) 

i. 주간 데이터를 월간 데이터로 변환 
- 해당 달의 주간 변수값들의 평균

ii. 트레이닝 테스트셋 분할(split train, testset)
- 2016~2019년은 training set, 2020년은 test set으로 분할
```
python ./getTrainTestSet/getTrainTestSet.py
```
[getTrainTestSet.py](https://github.com/2hyes/CLI-development/blob/master/getTrainTestSet/getTrainTestSet.py)를 실행하면, 본 연구에서 최종으로 선택한 전처리 및 분할 방법이 적용된 train, test set이 pkl파일로 저장된다.

#### 3) 예측 모형 적합(prediction model fitting)
