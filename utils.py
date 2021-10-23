import pandas as pd
import numpy as np
from pandas.io.pytables import AppendableFrameTable
from datetime import datetime
import matplotlib.pyplot as plt

Thres_hold = 10000 # means that the stock has at least 100 K shares traded per day

def getstockname(namestock):
    return len(namestock) == 3


def getValidList(filename, threshold):

    df = pd.read_csv(filename, index_col=0)
    df = df.sort_values(by = 'Volume', ascending = False)

    df =  df[df['Volume'] > threshold] # clean the stock that has small volume

    df =  df[df.Name.apply(getstockname) == True]
    df = df.sort_values(by = 'Name', ascending  = True)

    res = df.Name.to_list()

    with open(filename[:-4] + '.txt', 'w') as f:
        for item in res:
            f.write("%s\n" %item)

    return df.Name.to_list()

def getListStock(filename):
    res = []
    with open(filename, 'r') as f:
        res = f.read().splitlines()

        return res
def getAllStock():

    res = []
    hose = getListStock('hose.txt')
    hnx = getListStock('hnx.txt')
    upcom = getListStock('upcom.txt')

    for item in hose:
        res.append(item)

    for item in hnx:
        res.append(item)

    for item in upcom:
        res.append(item)

    return res
def stringToTimeStamp(stringtime):
    new_obj = datetime.strptime(stringtime, "%Y-%m-%d %H:%M")
    return datetime.timestamp(new_obj)
def convert5minute(datetime_object):

    hour = datetime_object.hour
    minute = datetime_object.minute

    current_time = hour*60 + minute  # the time fram calculate in the minutes
    return int(current_time / 5)  # divide by 5 minute


def convert1minute(datetime_object):
    hour = datetime_object.hour
    minute = datetime_object.minute

    return hour*60 + minute

def convertStringToMinute(timeString, time_interval):
    times = timeString.split(":")
    times = [int(time) for time in times]
    hour, minute, second = times

    return int((hour*60 + minute)/ time_interval)
def convert15minute(datetime_object):
    hour = datetime_object.hour
    minute = datetime_object.minute

    current_time = hour*60 + minute  # the time fram calculate in the minutes
    return int(current_time / 15)

def convertToMinute(datetime_object, time_interval):

    hour = datetime_object.hour
    minute = datetime_object.minute
    
    current_time = hour*60 + minute

    return int(current_time / time_interval)
def checkTimeInterval(number, time_interval, date): # remove the above three functions because of redundancy
    
    number =  number*time_interval
    hour = int(number /60)
    minute = number %60 
    return "{:} {:}:{:}".format(date, hour, minute)
# I am going to optimize my code by combining some funcitons into one smaller function
def getDailyData(csv_files, time_interval):

    # pre processing data loaded from vietstock 
    # contain all the data int the csv format so we need to pre-process them before transforming and analyzing
    csv_file = csv_files
    df = pd.read_csv(csv_file, usecols=[1,2,3,4])
    df = df.reindex(index=df.index[::-1])
    df.reset_index(inplace=True)
    df.drop(columns=['index'], inplace=True)
    df['Time']  = pd.to_datetime(df['Time'])
    df['VolumeChange'] =  df['Volume'].diff()
    df.loc[0,'VolumeChange'] = df.loc[0, 'Volume'] # assign the value of volume at the ATO 

    time_column = str(time_interval)+'minute'
    df[time_column] = df['Time'].apply(convertToMinute, args = (time_interval,)) # apply needs to match the object in the first parameter
    # if we use the (number) which means the int 
    # then we must pass the (number, ) which means a tuple
    #df['5minute'] = df['Time'].apply(convert5minute)
    #df['15minute'] = df['Time'].apply(convert15minute)
    #df['1minute'] = df['Time'].apply(convert1minute)
    return df

def getAveragePrice(group, args): # we pass args we two parameters time_interval and date
    # we are using a formula applied to price in a group
    
    time_interval, date = args 

    price = (group.Price*group.VolumeChange).sum() / group.VolumeChange.sum()
    volume = group.VolumeChange.sum()
    #value_index = int(group['1minute'].mean()) # aha the groupby summarize the information based on the 1minute column
    # but sitll use the beginning index and reset index later on
    # so we could use the value_index with the 1 minute colume
    time = checkTimeInterval(int(group[str(time_interval)+'minute'].mean()), time_interval, date) # get the time 
    timestamp = stringToTimeStamp(time)
    minPrice = group.Price.min()
    maxPrice = group.Price.max()
    openPrice = group.head(1).Price.iloc[0]
    closePrice = group.tail(1).Price.iloc[0] # return the first position of the Price conlumn and it is more effective
    return pd.Series([price, volume,time, timestamp, minPrice, maxPrice, openPrice, closePrice],
                    index = ['Price','Volume','TimeInterval','TimeStamp','MinPrice','MaxPrice','OpenPrice','ClosePrice'])
def getData1minute(df):
    #new_df = df.groupby(by=['5minute']).aggregate({'Price':'mean', 'VolumeChange':'sum','15minute':"mean",'1minute':'mean'})
    # the code sample before
    # the limite of the aggregate seems prevent us from using the our own function
    # then we should use the apply instead
    return df.groupby(by=['1minute']).apply(getAveragePrice, (1))
def getData5minute(df):
    return df.groupby(by=['5minute']).apply(getAveragePrice, (5))
def getData15minute(df):
    return df.groupby(by=['15minute']).apply(getAveragePrice, (15))

def getDataByTimeInterval(df, time_interval, date):
    group = str(time_interval)+'minute'
    return df.groupby(by=[group]).apply(getAveragePrice,(time_interval, date))

def process_past_data(csv_files, time_interval):
    days_csv = csv_files# convert to csv file name
    days = [item[-14:-4] for item in csv_files]
    merge_df =  pd.DataFrame()
    first_time = 0
    for i, csv_file in enumerate(days_csv):
        df = getDailyData(csv_file, time_interval)
        df = getDataByTimeInterval(df, time_interval = time_interval, date= days[i])
        if first_time == 0:
            merge_df = df
            first_time = 1
        else:
            merge_df = merge_df.append(df)
    merge_df.reset_index(inplace= True)
    return merge_df
if __name__ == '__main__':
    #print(getValidList('hose.csv', Thres_hold))
    #print(getValidList('hnx.csv', Thres_hold))
    #print(getValidList('upcom.csv', Thres_hold))
    
    print(getListStock('hose.txt'))