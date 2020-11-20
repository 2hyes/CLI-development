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

# 달의 마지막 주차이면, 해당 달의 데이터들의 평균값들을 하나의 record로 갖는 dataframe 생성
def getYdataframe(X, y):
    count = 0
    y_weekly = pd.DataFrame()

    for i in range(len(X)):
        count+= 1

        if ( isLastWeekOfThisMonth(X, i) ):
            a = np.where((y.month == X.iloc[i].month) & (y.year == X.iloc[i].year ))[0]
            present_ccsi = float(y.iloc[a].ccsi)
            
            past_ccsi = float(y.iloc[a-1].ccsi)
            sub = present_ccsi - past_ccsi
            
            for index in range(count):
                n = ((index+1) / count)*(sub)+past_ccsi
                record = pd.Series([int(X.iloc[i].year), int(X.iloc[i].month), int(X.iloc[i-(count-index)+1].day), n])
                row_df = pd.DataFrame([record])
                y_weekly = pd.concat([y_weekly, row_df], ignore_index=True)
            
            
            count = 0
            
    return y_weekly

# df column명 정해주는 function
def renameXdataframe(X):
    X.rename(columns={0: 'year', 1: 'month',2:'day', 3: 'keyword1', 4: 'keyword2', 5: 'keyword3', 6: 'keyword4', 7: 'keyword5', 8: 'google', 9: 'naver'}, inplace = True)
    return X.astype({"year": int, "month": int, "day": int})


def renameYdataframe(y):
    y.rename(columns={0: 'year', 1: 'month',2:'day', 3: 'ccsi'}, inplace = True)
    return y.astype({"year": int, "month": int, "day": int})


def getX_y_dateframe():
    news_df, portal_df, ccsi = loading_data()
    predictors = pd.merge(news_df, portal_df)

    y_df = getYdataframe(predictors, ccsi)
    y_df = renameYdataframe(y_df)
    X_df = renameXdataframe(predictors)
    
    return X_df, predictors, y_df

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
    pickle.dump(X_train, open('./dataset_interpolation/X_train.pkl','wb'))
    pickle.dump(X_test, open('./dataset_interpolation/X_test.pkl','wb'))
    pickle.dump(y_train, open('./dataset_interpolation/y_train.pkl','wb'))
    pickle.dump(y_test, open('./dataset_interpolation/y_test.pkl','wb'))
    pickle.dump(ccsi, open('./dataset_interpolation/ccsi.pkl','wb'))
    pickle.dump(predictors, open('./dataset_interpolation/predictors.pkl','wb'))
