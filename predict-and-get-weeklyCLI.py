import pandas as pd
import pickle
from sklearn.linear_model import Lasso
from sklearn.preprocessing import StandardScaler

# 데이터 로딩
def pickleLoad(file):
    with open(file,"rb") as fr:
        dataframe = pickle.load(fr)
    return dataframe

X_train = pickleLoad('./dataset/dataset_mean/X_train.pkl')
X_test = pickleLoad('./dataset/dataset_mean/X_test.pkl')
y_train = pickleLoad('./dataset/dataset_mean/y_train.pkl')
ccsi = pickleLoad('./dataset/dataset_mean/ccsi.pkl')
predictors = pickleLoad('./dataset/dataset_mean/predictors.pkl')

# 변수 스케일링
scaler = StandardScaler()
scaler.fit(X_train)
X_train = scaler.transform(X_train)
X_test = scaler.transform(X_test)

# 모델 적합
model_final = Lasso(alpha = 0.1, random_state = 23)
model_final.fit(X_train, y_train)
y_pred = model_final.predict(X_test)

# 주간 데이터에 대한 주간 경제심리보조지수 값 얻기
X = scaler.transform(predictors.loc[:, ['keyword1', 'keyword2', 'keyword3', 'keyword4', 'keyword5', 'google', 'naver']])
pred_ccsi = model_final.predict(X)

tmp = pd.merge(predictors, ccsi)
tmp['pred'] = pred_ccsi
tmp['date'] = tmp[['year', 'month', 'day']].apply(lambda x: '.'.join(map(str, x)), axis=1)

weekly_CLI = []
for i in range(len(tmp)):
    if i == 0 :
        cli = tmp.pred.iloc[i]
        weekly_CLI.append(cli)
        continue
    
    cli = (tmp.pred.iloc[i-1] + tmp.pred.iloc[i]) / 2
    weekly_CLI.append(cli)
    
tmp['weeklyCLI'] = weekly_CLI

## final 모델 및 주간 지수 결과 저장
final_table = tmp[['date', 'keyword1', 'keyword2', 'keyword3', 'keyword4', 'keyword5', 'google', 'naver', 'ccsi', 'weeklyCLI']]
pickle.dump(model_final, open('./final_model.pkl', 'wb'))
pickle.dump(scaler, open('./final_scaler.pkl', 'wb'))
pickle.dump(final_table, open('./final_table.pkl', 'wb'))