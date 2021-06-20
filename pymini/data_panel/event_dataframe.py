import pandas as pd

class EventDataFrame(pd.DataFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clear(self):
        xs = self.events.index
        try:
            self.events.drop(self.events.index, inplace=True)
        except:
            pass
        return list(xs) #returns successfully deleted indices

    # def append(self, *args, **kwargs):
    #     try:
    #         self = super(self.__class__, self).append(*args, **kwargs)
    #         # self.sort_values(by=['t'], inplace=True, ascending=True)
    #         # print(self)
    #         # return self
    #         return self
    #     except Exception as e:
    #         return self
    #         print(e)
    #

