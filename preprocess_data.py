import numpy as np
import pandas as pd
import math

miles_to_meters = 1609.34

def get_distance_meters (lat1, long1, lat2, long2, earth_radius_meters = 6371000):
    '''
    Calculate the distance between two points in meters
    in order to guess the unit of TripDistance in company A's data
    Input: latitude, longitude of two points (in signed degrees)
    '''
    del_degree = ((lat2 - lat1)**2 + (long2 - long1)**2)**0.5
    del_radian = del_degree*math.pi/180
    distance_meters  = earth_radius_meters*del_radian
    return distance_meters

def load_data():
    # load company A data
    df_a = pd.read_csv('data/company_a_1.csv')
    df_a = pd.concat([df_a, pd.read_csv('data/company_a_2.csv')])
    df_a = pd.concat([df_a, pd.read_csv('data/company_a_3.csv')])
    df_a = pd.concat([df_a, pd.read_csv('data/company_a_4.csv')])
    df_a = pd.concat([df_a, pd.read_csv('data/company_a_5.csv')])

    # load company B data
    df_b = pd.read_csv('data/company_b_1.csv')
    df_b = pd.concat([df_b, pd.read_csv('data/company_b_2.csv')])

    # Match column names with B
    df_a.rename(columns={
        'TripID': 'trip_id',
        'ScooterID': 'scooter_id', 
        'StartTime': 'start_time',
        'EndTime': 'end_time',
        'StartLongitude': 'start_longitude', 
        'StartLatitude': 'start_latitude', 
        'EndLongitude': 'end_longitude', 
        'EndLatitude': 'end_latitude',
        'TripDistance': 'distance_m', # guess TripDistance is in miles
        }, inplace=True)
    
    # convert the unit correctly as guessed
    df_a.distance_m = df_a.distance_m*miles_to_meters
    
    df_b.rename(columns={
        'distance_meters': 'distance_m', 
        'completed_time': 'end_time'
        }, inplace=True)
    
    df_a['distance_compare_m'] = get_distance_meters(
        df_a.start_latitude, 
        df_a.start_longitude, 
        df_a.end_latitude, 
        df_a.end_longitude
        )
    
    df_b['distance_compare_m'] = get_distance_meters(
        df_b.start_latitude, 
        df_b.start_longitude, 
        df_b.end_latitude, 
        df_b.end_longitude
        )
    
    df_a['company'] = 'A'
    df_b['company'] = 'B'

    return df_a, df_b

def format_time(df_a, df_b):
    '''
    Match time format of df_a to df_b before concatenating.
    Assumes company B's time zone is in US/Eastern
    based on the coordinates.
    '''

    df_a.start_time = pd.to_datetime(df_a.start_time, format='%m/%d/%y %H:%M')
    df_a.end_time = pd.to_datetime(df_a.end_time, format='%m/%d/%y %H:%M')
    df_a['duration_s'] = (df_a.end_time-df_a.start_time).dt.total_seconds()

    df_b.start_time = pd.to_datetime(df_b.start_time)
    df_b.end_time = pd.to_datetime(df_b.end_time)
    df_b['duration_s'] = (df_b.end_time-df_b.start_time).dt.total_seconds()

    df_a['week'] = df_a.start_time.dt.to_period('W').dt.start_time
    df_b['week'] = df_b.start_time.dt.tz_convert('US/Eastern').dt.to_period('W').dt.start_time

    #df_a['date'] = df_a.start_time.dt.date
    #df_b['date'] = df_b.start_time.dt.tz_convert('US/Eastern').dt.date

    df_a['hour'] = df_a.start_time.dt.hour
    df_b['hour'] = df_b.start_time.dt.tz_convert('US/Eastern').dt.hour

    df_a['day'] = df_a.start_time.dt.day_name()
    df_b['day'] = df_b.start_time.dt.tz_convert('US/Eastern').dt.day_name()

    return df_a, df_b


def get_cleaned_data(min_distance_m = 5, min_duration_s = 10):
    '''
    Load data and return cleaned data (per log)
    '''
    df_a, df_b = load_data()
    df_a, df_b = format_time(df_a, df_b)

    df = pd.concat([df_a, df_b])

    # Make analysis features
    df['area'] = df.apply(
        lambda x:
        'Downtown' if (x.start_longitude < -85.73) & (x.start_latitude > 38.24) else
        'University' if (x.start_longitude < -85.73) & (x.start_latitude <= 38.24) else
        'Residential' if x.start_longitude >= -85.73 else
        'Unknown',
        axis=1)

    df['speed_mile_per_hour'] = (df.distance_m/miles_to_meters)/((df.duration_s)/3600) 

    df_uncleaned = df.copy()

    # drop incorrect logs
    # check plots in eda.ipynb to see outlier plots
    df = df[
        (df.distance_m < 1e5)
        & (df.distance_m > min_distance_m)
        & (df.duration_s > min_duration_s)
        & (df.speed_mile_per_hour<100) 
        # A few end coordinates does not look correct, but we will ignore it as we won't use them
        # & (abs(df.distance_compare_m/df.distance_m) > 100) 
    ]

    # Convert units to catch easier
    df['distance_mile'] = df['distance_m']/miles_to_meters
    df['duration_hour'] = df['duration_s']/3600
    df['duration_minute'] = df['duration_s']/60

    # return both cleaned and uncleaned data for comparison
    return df, df_uncleaned

def get_aggregated_data(df, time_unit = ['week'], segment_area = True):
    '''
    Aggregate logs by time unit
    Used for plotting.
    Input: df, time unit ['week'], ['day'], ['hour'], or ['day','hour']

    - week: tracks weekly progress
    - day: tracks operational patterns by day of week
    - hour: tracks operational patterns by hour of day
    - ['day','hour']: tracks operational patterns by day of week and hour of day together
    '''
    assert time_unit in [['week'], ['day'], ['hour'], ['day','hour']], \
        "time_unit must be one of ['week'], ['day'], ['hour'], or ['day','hour']"
    
    groupby_list = ['area', 'company']
    if segment_area==False:
        groupby_list = ['company']

    df_agg = df.groupby(time_unit+groupby_list)[['duration_s', 'distance_m']].sum().reset_index()
    df_num_scooter= df.groupby(time_unit+groupby_list)['scooter_id'].nunique().rename('num_scooter')
    df_num_ride = df.groupby(time_unit+groupby_list).size().rename('num_ride')

    df_agg = df_agg.set_index(time_unit+groupby_list).join(
        df_num_ride, how='left'
        ).join(
        df_num_scooter, how='left'
        ).reset_index()
    
    df_agg['duration_s'] = df_agg['duration_s']/3600
    df_agg['distance_m'] = df_agg['distance_m']/miles_to_meters
    df_agg.rename(columns={'duration_s': 'driven_hours', 'distance_m': 'driven_miles'}, inplace=True)
    


    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    hourly_order = [i for i in range(24)]

    if 'day' in time_unit:
        df_agg['day'] = pd.Categorical(df_agg['day'], categories=day_order, ordered=True)
    if 'hour' in time_unit:
        df_agg['hour'] = pd.Categorical(df_agg['hour'], categories=hourly_order, ordered=True)

    df_agg.sort_values(groupby_list+time_unit, inplace=True)

    if ('week' in time_unit) and (segment_area==True):
    # Drop the first and last week data because they might not have a complete week, 
    # so underestimate the weekly aggregated values
        first_week_index_list = [
            df_agg[(df_agg.company=='A') & (df_agg.area=='Downtown')].index.tolist()[0],
            df_agg[(df_agg.company=='A') & (df_agg.area=='University')].index.tolist()[0],
            df_agg[(df_agg.company=='A') & (df_agg.area=='Residential')].index.tolist()[0],
            df_agg[(df_agg.company=='B') & (df_agg.area=='Downtown')].index.tolist()[0],
            df_agg[(df_agg.company=='B') & (df_agg.area=='University')].index.tolist()[0],
            df_agg[(df_agg.company=='B') & (df_agg.area=='Residential')].index.tolist()[0]
        ]
        df_agg.drop(index=first_week_index_list, inplace=True)
        last_week_index_list = [
            df_agg[(df_agg.company=='A') & (df_agg.area=='Downtown')].index.tolist()[-1],
            df_agg[(df_agg.company=='A') & (df_agg.area=='University')].index.tolist()[-1],
            df_agg[(df_agg.company=='A') & (df_agg.area=='Residential')].index.tolist()[-1],
            df_agg[(df_agg.company=='B') & (df_agg.area=='Downtown')].index.tolist()[-1],
            df_agg[(df_agg.company=='B') & (df_agg.area=='University')].index.tolist()[-1],
            df_agg[(df_agg.company=='B') & (df_agg.area=='Residential')].index.tolist()[-1]
        ]
        df_agg.drop(index=last_week_index_list, inplace=True)

        df_agg['daily_ride_per_scooter'] = df_agg['num_ride']/df_agg['num_scooter']/7
        df_agg['daily_hours_per_scooter'] = df_agg['driven_hours']/df_agg['num_scooter']/7

    elif ('week' in time_unit) and (segment_area==False):
        first_week_index_list = [
            df_agg[(df_agg.company=='A')].index.tolist()[0],
            df_agg[(df_agg.company=='B')].index.tolist()[0],
        ]
        df_agg.drop(index=first_week_index_list, inplace=True)
        last_week_index_list = [
            df_agg[(df_agg.company=='A')].index.tolist()[-1],
            df_agg[(df_agg.company=='B')].index.tolist()[-1],
        ]
        df_agg.drop(index=last_week_index_list, inplace=True)

        df_agg['daily_ride_per_scooter'] = df_agg['num_ride']/df_agg['num_scooter']/7
        df_agg['daily_hours_per_scooter'] = df_agg['driven_hours']/df_agg['num_scooter']/7

    df_agg['miles_per_ride'] = df_agg['driven_miles']/df_agg['num_ride']

    return df_agg

def get_all_data_frames(min_distance_m = 5, min_duration_s = 10):
    '''
    Get all data frames
    Wrapper function for all the above
    '''
    df, df_uncleaned = get_cleaned_data(min_distance_m, min_duration_s)
    df_week = get_aggregated_data(df, ['week'])
    df_week_all_area = get_aggregated_data(df, ['week'], False)
    df_day = get_aggregated_data(df, ['day'])
    df_hour = get_aggregated_data(df, ['hour'])
    df_day_hour = get_aggregated_data(df, ['day','hour'])

    df_day_december = get_aggregated_data(df[df.week.dt.to_period('W').dt.month==12], ['day'])
    df_hour_december = get_aggregated_data(df[df.week.dt.to_period('W').dt.month==12], ['hour'])
    df_day_hour_december = get_aggregated_data(df[df.week.dt.to_period('W').dt.month==12], ['day','hour'])
    
    df_dict = {
        'df': df,
        'df_uncleaned': df_uncleaned,
        'df_week': df_week,
        'df_week_all_area': df_week_all_area,
        'df_day': df_day,
        'df_hour': df_hour,
        'df_day_hour': df_day_hour,
        'df_day_december': df_day_december,
        'df_hour_december': df_hour_december,
        'df_day_hour_december': df_day_hour_december
    }
    return df_dict
