import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder

from structs.works import TV, FanWork

res=TV.retrieve(TV.search(title='Our Flag Means Death')[0])
ofmd=TV(title=res.get('title'), 
        data=res, 
        genres=res.get('genres'), 
        id=res.movieID, 
        author=res.get('writers')[0], 
        date=res.get('year'), 
        fandom='Our Flag Means Death (TV 2022)')


class FanficModel:
    def __init__(self, fics, target='tags'):
        df=pd.DataFrame.from_records([f.__dict__ for f in fics.values()])
        df=self.preprocess(df)
        cols=[d for d in df['columns'] if d!=target]
        X=df[[cols]]
        y=df[target]
        X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle=True, train_size=0.7)
        self.target=target
        self.training={
            'X':X_train,
            'y':y_train
        }
        self.testing={
            'X':X_test,
            'y':y_test
        }
    
    def preprocess(self, fr):
        approval_rating=fr['kudos']/fr['hits']
        tags=OneHotEncoder(fr['tags'])
        f=pd.DataFrame()
        f['approval_rating']=approval_rating
        f['tags']=tags
        return f

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


ofmd.get_fics()
ofmd_model=FanficModel(ofmd.fics)