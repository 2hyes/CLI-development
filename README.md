# CLI-development
## 1. Overview

- 목표: 

  Use news counting and portal trends(google,naver,kakao) data to develope new Composite Leading Indicator <br>
  뉴스기사수와 포털 트렌드의 주간 데이터들을 수집하여, 월간 경제 지표인 소비자심리지수를 예측하여 새로운 주간 경제심리보조지수를 개발한다. 

- 기대 효과:
1. 기존의 경제지표보다 빠른 소비자의 피드백을 통해 부정적인 경제 상황에 보다 탄력적으로 대응이 가능하다.
2. 소비자심리지수 대비 속보성의 효과를 지닌다.
3. 표본 설계의 오류에서 벗어나, 보다 정확한 지표를 얻는다.
  
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
 ┣ 📜predict-and-get-weeklyCLI.py
 ┣ 📜validation-and-Ttest(dataset_interpolation).ipynb
 ┣ 📜validation-and-Ttest(dataset_interpolation_shuffle).ipynb
 ┣ 📜validation-and-Ttest(dataset_mean).ipynb
 ┣ 📜validation-and-Ttest(dataset_mean_shuffle).ipynb
 ┣ 📜validation-and-Ttest(dataset_median).ipynb
 ┗ 📜validation-and-Ttest(dataset_median_shuffle).ipynb
```

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

## 3. Methods and Experimental Results

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

- 예측 모델 <br>
각 전처리 및 데이터 분할 방법을 적용하여 생성한 6개의 다른 train, test set을 활용하여, 4가지의 모형족에 대해 10-fold CV를 진행한다. 10-fold에서 얻은 RMSE값들을 저장하여, t-검정을 하여 모델들의 성능을 비교한 후, 최적의 모델을 선택한다. 

- t검정(significance level = 0.05, two-sided test) <br>

```
H0: RMSE of model1 = RMSE of model2 
hence, there's no difference of performance between two models.
H1: there's difference of performance.
```

- 결과 표 <br>

| preprocessing | split | model | parameter | CV RMSE | code |
|----------|:----------|:----------|:-----------:|:-------:|:----------------:|
| mean | random | Multiple linear regression:point_left: |  | 3.5626 | [코드](https://github.com/2hyes/CLI-development/blob/master/validation-and-Ttest(dataset_mean_shuffle).ipynb) |
| | | Random forest | max_features = 3<br>n_estimators = 16 |  3.6059  |  |
| | | GAMS |  | 6.2651 | |
| | | Lasso linear regression | alpha = 1 | 3.6391 |  |
| mean | chronological order | Multiple linear regression |  | 3.4248 | [코드](https://github.com/2hyes/CLI-development/blob/master/validation-and-Ttest(dataset_mean).ipynb) |
| | | Random forest | max_features = 5<br>n_estimators = 32 |  2.3969  |  |
| | | GAMS |  | 7.2044 |  |
| | | Lasso linear regression:point_left: | alpha = 0.1  | 2.8664 |  |
| median | random | Multiple linear regression:point_left: |  | 3.3128 | [코드](https://github.com/2hyes/CLI-development/blob/master/validation-and-Ttest(dataset_median_shuffle).ipynb) |
| | | Random forest | max_features = 5<br>n_estimators = 16 |  3.4961  |  |
| | | GAMS |  | 7.3029 |    |
| | | Lasso linear regression | alpha = 0.1  | 3.4731 |  |
| median | chronological order | Multiple linear regression |  | 3.5008 | [코드](https://github.com/2hyes/CLI-development/blob/master/validation-and-Ttest(dataset_median).ipynb) |
| | | Random forest | max_features = 5<br>n_estimators = 16 |  2.4906  |  |
| | | GAMS |  | 6.9915 |    |
| | | Lasso linear regression:point_left: | alpha = 0.01  | 2.6935 |  |
| interpolation | random | Multiple linear regression |  | 4.6893 | [코드](https://github.com/2hyes/CLI-development/blob/master/validation-and-Ttest(dataset_interpolation).ipynb) |
| | | Random forest:point_left: | max_features = 4<br>n_estimators = 64 |  3.9490  |  |
| | | GAMS |  | 5.7114 |    |
| | | Lasso linear regression | alpha = 0.01  | 4.6332|  |
| interpolation | chronological order | Multiple linear regression |  | 3.9692 | [코드](https://github.com/2hyes/CLI-development/blob/master/validation-and-Ttest(dataset_interpolation).ipynb) |
| | | Random forest:point_left: | max_features = 3<br>n_estimators = 64 |  2.8083  |  |
| | | GAMS |  | 4.2404 |    |
| | | Lasso linear regression | alpha = 0.1  | 3.3675 |  |


## 4. Reproduce results
: 최종 선택한 방법과 모델의 코드 재현 방법

#### 1) 데이터셋 준비(save to db table)
```
python get-data.py
```
[get-data.py](https://github.com/2hyes/CLI-development/blob/master/get-data.py)에 네이버데이터랩 API client id, pw / 한국은행 openAPI api key / 저장할 database의 id, pw, db를 입력하면, 필요한 데이터셋이 모두 데이터베이스에 저장된다.

#### 2) 데이터 전처리(preprocess data)

i. 주간 데이터를 월간 데이터로 변환 
- 해당 달의 주간 변수값들의 평균

ii. 트레이닝 테스트셋 분할(split train, testset)
- 2016~2019년은 training set, 2020년은 test set으로 분할
```
python ./getTrainTestSet/getTrainTestSet.py
```
[getTrainTestSet.py](https://github.com/2hyes/CLI-development/blob/master/getTrainTestSet/getTrainTestSet.py)를 실행하면, 본 연구에서 최종으로 선택한 전처리 및 분할 방법이 적용된 train, test set이 pkl파일로 저장된다.

#### 3) 예측 모형 적합(fit prediction model)
#### 4) 주간 경제심리보조지수(get weekly CLI) 
```
python predict-and-get-weeklyCLI.py
```
[predict-and-get-weeklyCLI.py](https://github.com/2hyes/CLI-development/blob/master/predict-and-get-weeklyCLI.py)를 실행하면, 본 연구에서 최종으로 선택하여 적합시킨 모델이 생성되어, final_model.pkl로 저장된다. 더불어, 주간 데이터를 해당 모델에 input하여 얻은 값들에 이동 평균을 적용하여 주간 경제심리보조지수를 생성한다. 주간 경제심리보조지수는 table형태로 final_table.pkl에 저장된다.
