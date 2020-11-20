import pandas as pd
from sklearn.model_selection import train_test_split
import pymysql
import numpy as np
import pickle

"""
Step1. data load
"""
def loading_data():
    ## DB connection
    conn = pymysql.connect(host = "127.0.0.1", user = [USER], passwd = [PASSWORD], db = [DATABASE], cursorclass = pymysql.cursors.DictCursor)
    cur = conn.cursor()
    
    cur.execute("show databases")
    cur.execute("use crawling")

    ## Table data loading
    # news
    query = """ 
    select * from news_counting;
    """
    cur.execute(query)
    news_df = pd.DataFrame(list(cur.fetchall())).drop(['id'], axis=1)
    news_df.head()

    # portal
    # 카카오변수 제외, 구글/네이버를 활용하기위해 
    # 네이버 변수가 값을 갖는 2016년 1월부터 데이터 사용
    query = """ 
    select * from portal_trends_ratio ;
    """
    cur.execute(query)
    portal_df = pd.DataFrame(list(cur.fetchall()))
    portal_df = portal_df[['year', 'month', 'day', 'google', 'naver']][17:]

    ## response y: CCSI(소비자심리지수)
    query = """ 
    select * from ccsi ;
    """
    cur.execute(query)
    conn.close()
    cur.close()
    # X와 기간을 맞춤
    ccsi = pd.DataFrame(list(cur.fetchall()))[4:].reset_index(drop = True)

    return news_df, portal_df, ccsi

"""
Step2. X, y dataframe
"""

# 달의 마지막주인지 확인하는 function
def isLastWeekOfThisMonth(X, index):
    if(index == (len(X) - 1)):
        return True
    if ( X.iloc[index].month != X.iloc[index + 1].month ):
        return True
    return False

# 같은 달의 주차별 데이터들을 저장하는 list를 초기화하는 function
def initializeStacks():
    global keyword1_stack, keyword2_stack, keyword3_stack, keyword4_stack, keyword5_stack, google_stack, naver_stack
    keyword1_stack = []
    keyword2_stack = []
    keyword3_stack = []
    keyword4_stack = []
    keyword5_stack = []
    google_stack = []
    naver_stack = []

# 달의 마지막 주차이면, 해당 달의 데이터들의 평균값들을 하나의 record로 갖는 dataframe 생성
def getXdataframe(X):
    initializeStacks()
    X_monthly = pd.DataFrame()
    for i in range(len(X)):
        keyword1_stack.append(X.iloc[i].keyword1)
        keyword2_stack.append(X.iloc[i].keyword2)
        keyword3_stack.append(X.iloc[i].keyword3)
        keyword4_stack.append(X.iloc[i].keyword4)
        keyword5_stack.append(X.iloc[i].keyword5)
        google_stack.append(X.iloc[i].google)
        naver_stack.append(X.iloc[i].naver)

        if ( isLastWeekOfThisMonth(X, i) ):
            
            # 달의 마지막 주차이면, 해당 달의 데이터들의 최솟값을 저장. 
            keyword1 = np.min(keyword1_stack)
            keyword2 = np.min(keyword2_stack)
            keyword3 = np.min(keyword3_stack)
            keyword4 = np.min(keyword4_stack)
            keyword5 = np.min(keyword5_stack)
            google = np.min(google_stack)
            naver = np.min(naver_stack)
            
            record = pd.Series([int(X.iloc[i].year), int(X.iloc[i].month), keyword1, keyword2, keyword3, keyword4, keyword5, google, naver])
            row_df = pd.DataFrame([record])
            X_monthly = pd.concat([X_monthly, row_df], ignore_index=True)
            initializeStacks()
            
    return X_monthly

# df column명 정해주는 function
def renameXdataframe(X):
    X.rename(columns={0: 'year', 1: 'month', 2: 'keyword1', 3: 'keyword2', 4: 'keyword3', 5: 'keyword4', 6: 'keyword5', 7: 'google', 8: 'naver'}, inplace = True)
    return X.astype({"year": int, "month": int})

def getX_y_dateframe():
    news_df, portal_df, ccsi = loading_data()
    predictors = pd.merge(news_df, portal_df)
    X_df = getXdataframe(predictors)
    X_df = renameXdataframe(X_df)
    
    return X_df, predictors, ccsi

"""
Step3. Modeling
- split train and test set
"""
def getTrainTestSet(X_df, ccsi):
    df = pd.merge(X_df, ccsi)
    X = df[['keyword1', 'keyword2', 'keyword3', 'keyword4', 'keyword5', 'google', 'naver']] # X: 예측변수 dataframe
    y = df[['ccsi']] # y: 반응변수 dataframe

    # CV를 활용하기 위해, validate set은 따로 분할하지 않는다.
    X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.8, test_size=0.2, shuffle=False)

    return X_train, X_test, y_train, y_test
    

###################### main ######################
if __name__ == "__main__":
    X_df, predictors, ccsi = getX_y_dateframe()
    X_train, X_test, y_train, y_test = getTrainTestSet(X_df, ccsi)  
    pickle.dump(X_train, open('./dataset_min/X_train.pkl','wb'))
    pickle.dump(X_test, open('./dataset_min/X_test.pkl','wb'))
    pickle.dump(y_train, open('./dataset_min/y_train.pkl','wb'))
    pickle.dump(y_test, open('./dataset_min/y_test.pkl','wb'))
    pickle.dump(ccsi, open('./dataset_min/ccsi.pkl','wb'))
    pickle.dump(predictors, open('./dataset_min/predictors.pkl','wb'))
