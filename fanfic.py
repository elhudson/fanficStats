import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder

from structs.works import TV

enc=OneHotEncoder()

res=TV.retrieve(TV.search(title='Our Flag Means Death')[0])
ofmd=TV.create(res)
ofmd.fics

class FanficModel:
    def __init__(self, target='tags'):
        self.target=target

    @staticmethod
    def to_dataframe(fics):
        return pd.DataFrame.from_records([f.__dict__ for f in fics.values()], index='id')
        
    def preprocess(self, fics):
        tags=self.get_top_tags(fics)
        return tags        
        # for f in fics.values():
        #     for tag in f.tags:
        #         if tag in tags:
        #             tag_matrix.at[str(f.id), tag]=1
        #         else:
        #             tag_matrix.at[str(f.id), tag]=0
                        
        # cols=[d for d in df.columns if d!=target]
        # X=df[[cols]]
        # y=df[target]
        # X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle=True, train_size=0.7)
        # self.target=target
        # self.training={
        #     'X':X_train,
        #     'y':y_train
        # }
        # self.testing={
        #     'X':X_test,
        #     'y':y_test
        # }

    def train(self):
        model=LinearRegression()
        model.fit(self.training['X'], self.training['y'])
        self.model=model
        
    def predict(self, fic):
        fr=pd.DataFrame(fic.__dict__) 
        cols=[d for d in fr['columns'] if d!=self.target]
        data=fr[[cols]]
        res=self.model.predict(data)
        return {self.target: res}


