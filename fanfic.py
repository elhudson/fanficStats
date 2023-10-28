import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder

from structs.works import TV, FanWork

enc=OneHotEncoder()

res=TV.retrieve(TV.search(title='Our Flag Means Death')[0])
ofmd=TV(title=res.get('title'), 
        data=res, 
        genres=res.get('genres'), 
        id=res.movieID, 
        author=res.get('writers')[0], 
        date=res.get('year'), 
        fandom='Our Flag Means Death (TV 2022)')


class FanficModel:
    def __init__(self, target='tags'):
        self.target=target

    @staticmethod
    def to_dataframe(fics):
        return pd.DataFrame.from_records([f.__dict__ for f in fics.values()])
        
    def get_top_tags(self, fics):
        df=self.to_dataframe(fics)
        s=[]
        for d in df['tags']:
            s.extend(d)
        tags={t:s.count(t) for t in list(set(s))}
        counts=pd.DataFrame({'tag':tags.keys(), 'occurrences':tags.values()})
        return counts.loc[counts['occurrences']>=np.percentile(counts['occurrences'], 95)]['tag'].values.tolist()
        
    def preprocess(self, fics):
        tags=self.get_top_tags(fics)
        tag_matrix=pd.DataFrame(index=fics.keys(), columns=tags)
        return tag_matrix.apply(lambda x: 1 if len([i for i in fics[x.name].tags if i in tags])>0 else 0, axis=1, result_type='broadcast')
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


ofmd.get_fics()
ofmd_model=FanficModel(target='tags')
