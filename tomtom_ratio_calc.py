""" This script scrape from TOMTOM the daily congestion index for 400+ cities,
 and calculate monthly averaged 21/19 congestion index ratio for the corresponding 57 countries
 and lastly fill in the 231 country table with the 57 countries' ratio"""

import os
import pandas as pd

def get_city_country_info_from(file_name):
    line = file_name.split('_')
    return line[0], line[1].split('.')[0]

def get_monthly_avg(TOM_dir):
    """loop through all the city files to calculate monthly average congestion index in 2019 and 2021 for each city
    write results to two DataFrames monthly21 and monthly19 which have city country name and congestion values in months 1-12 """
    monthly21 = pd.DataFrame()
    monthly19 = pd.DataFrame()
    files = os.listdir(TOM_dir)
    for file in files:
        if not os.path.isdir(file):
            file_path = os.path.join(TOM_dir, file)
            if file.split('.')[-1] != 'csv':
                continue
            print(f'process file path {file_path}')
            daily_data = pd.read_csv(file_path)
            if 'diffRatio' not in daily_data:
                print(f'warning {file_path} has no diffRatio')
                continue
            daily_data[['YYYY', 'M', 'D']] = daily_data['date'].str.split('-', expand=True)
            daily_data['conges19'] = daily_data['congestion'] / (1 + daily_data['diffRatio'])
            daily_data.rename(columns={"congestion": "conges21"}, inplace=True)
            conges21 = pd.DataFrame(daily_data.groupby('M')['conges21'].mean()).transpose()
            conges19 = pd.DataFrame(daily_data.groupby('M')['conges19'].mean()).transpose()
            assert  not conges21.empty
            assert  not conges19.empty
            country_name, city_name = get_city_country_info_from(file)
            conges21.insert(0, "country", country_name)
            conges21.insert(1, "city", city_name)
            conges19.insert(0, "country", country_name)
            conges19.insert(1, "city", city_name)
            monthly21 = monthly21.append(conges21)
            monthly19 = monthly19.append(conges19)
            assert not monthly21.empty
            assert not monthly19.empty
    return monthly21, monthly19

def get_country_avg(df21, df19):
    """  df21 and df19 are DataFrames that contain monthly averaged congestion index for each city This function takes
    the city level monthly data, calculate monthly country average for 2019 and 2020, and take ratio 2021/2020
    Output is a table with columns being monthly ratio 21/19, rows being all the countries"""
#    print(df21)
    country21 = df21.groupby('country').mean()
    country19 = df19.groupby('country').mean()
    # div() method divides element-wise division of one pandas DataFrame by another.
    country_avg = country21.div(country19).reset_index()
    return country_avg


def fill_country_list(data_countries, country_region_ref):
    C_names = pd.read_csv(country_region_ref)
    C_names = C_names[['Alpha-3 code', 'Region1_GID', 'Region2', 'Income_This study']]
    data_countries = C_names.merge(data_countries, how='left', left_on='Alpha-3 code', right_on='country')
    high = data_countries.groupby('Income_This study').get_group('High income')
    upper = data_countries.groupby('Income_This study').get_group('Upper middle income')
    lower = data_countries.groupby('Income_This study').get_group('Lower middle income')
    low = data_countries.groupby('Income_This study').get_group('Low income')
    high.fillna(high.mean(), inplace=True)
    upper.fillna(upper.mean(), inplace=True)
    lower.fillna(lower.mean(), inplace=True)

    full_TOMTOM = pd.concat([high, upper, lower, low]).sort_index()
    full_TOMTOM.fillna(1.0, inplace=True)
    num_of_NAN = full_TOMTOM.isnull().sum().sum()
    print('Number of NAN left = ', num_of_NAN)
    return full_TOMTOM


if __name__ == '__main__':
    TOM_dir = "/Users/yin/Documents/Near-real-time/pandas_scripts/TOMTOM/tomtom_data_test/"
#    TOM_dir = "/Users/yin/Documents/Near-real-time/pandas_scripts/TOMTOM/tomtom_data/"
    country_region_ref = '/Users/yin/Documents/Near-real-time/pandas_scripts/countries.csv'
    monthly21, monthly19 = get_monthly_avg(TOM_dir)
#    monthly19.to_csv(os.path.join(TOM_dir, 'monthly19.csv'))
    country_avg = get_country_avg(monthly21, monthly19)
#    country_avg.to_csv(os.path.join(TOM_dir, 'country_avg_monthly.csv'))
    full_TOMTOM = fill_country_list(country_avg, country_region_ref)
    full_TOMTOM.to_csv(os.path.join(TOM_dir, 'Ground_transportation_TOMTOM_21-19ratio.csv'))
