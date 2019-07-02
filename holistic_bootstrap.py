import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import bs4
import datetime

#Need to work on algorithm for finding half years and closer proxies for traded curve pricing
#change all returned data structures to dataframe format?

def price_scrape():
    '''
    scrapes pricing and maturities from WSJ website for further processing
    :return: pandas dataframe containing information for further processing
    '''

    resp = requests.get('https://www.wsj.com/market-data/bonds/treasuries') #response from WSJ request
    soup = bs4.BeautifulSoup(resp.text,'lxml')
    data_label_one = 'WSJTables--table__cell--2dzGiO7q WSJTheme--table__cell--1At-VGNg ' #label for regular data in table
    data_label_two = 'WSJTables--table__cell--2dzGiO7q WSJTables--u-positive--3yr2uDqt WSJBase--u-positive--1lTKRQ01 WSJTheme--table__cell--1At-VGNg ' #label for positive movement in table
    data_label_three = 'WSJTables--table__cell--2dzGiO7q WSJTables--u-negative--3FjApdil WSJBase--u-negative--O0g6yWmX WSJTheme--table__cell--1At-VGNg ' #label for negative movement in table
    table = soup.find_all('td', {'class':[data_label_one,data_label_two,data_label_three]})
    date_label = 'WSJTables--table__cell--2dzGiO7q WSJTables--is-first--2Jt1dPu7 WSJTheme--table__cell--1At-VGNg ' #label for dates column
    dates = soup.find_all('td',{'class':date_label})

    #initialize data structures for storage
    date_list = list()
    data_list = list()
    master_data = list()
    combine = list()
    return_data = pd.DataFrame()

    #find date, process based on label, make datetime object
    for date in dates:
        str_date = str(date)
        sliced = str_date[len(date_label)+13:-5]
        month,day,year = sliced.split(sep='/')
        date_obj = datetime.date(int(year),int(month),int(day))
        date_list.append(sliced)

    #find data in each row, process based on label, try changing to float, otherwise unchanged
    for dat in table:
        str_dat = str(dat)
        if str_dat.find(data_label_one):
            sliced = str_dat[len(data_label_one) + 13:-5]
        elif str_dat.find(data_label_two):
            sliced = str_dat[len(data_label_two) + 13:-5]
        elif str_dat.find(data_label_three):
            sliced = str_dat[len(data_label_three) + 13:-5]
        try:
            flt_dat = float(sliced) #float data
            data_list.append(flt_dat)
        except:
            #might drop this as change is only marginally helpful for purpose of this analysis
            data_list.append(0.00) #otherwise zero
        if len(data_list) == 5:
            master_data.append(data_list)
            data_list = []
        else:
            continue
    combiner = list()
    for i,date in enumerate(date_list):
        combiner.append(date)
        combiner.extend(master_data[i])
        combine.append(combiner)
        combiner = list()
    columns = ['date','coupon','bid','ask','change','yield']
    df = pd.DataFrame(combine)
    df.columns = columns
    df.set_index('date',inplace=True)
    df['ba_spread'] = df['ask'] - df['bid']
    df['avg_price'] = (df['bid'] + df['ask']) / 2
    return df



def load(fname):
    '''
    load bond into pandas dataframe
    '''
    file = pd.read_excel(fname,header=1,index_col=0)
    return file

def load_curve():
    '''
    scrape yield curve data from treasury website
    :return: dictionary of yield curve data
    '''

    #curve response from treasury website
    resp = requests.get('https://www.treasury.gov/resource-center/data-chart-center/interest-rates/Pages/TextView.aspx?data=yieldYear&year=2019')
    soup = bs4.BeautifulSoup(resp.text,'lxml')
    table = soup.find_all('td', {'class': 'text_view_data'}) #data found with 'text_view_data' class

    #initialize data structures
    rate_dict = dict()
    rate_list = list()

    #loop through each row in table and find yield on each date
    for i,item in enumerate(table):
        if i==0: #initial row
            date = str(item)[-13:-5]
        elif i % 13 == 0: #new row of yields
            rate_dict[date] = rate_list
            rate_list = list()
            date = str(item)[-13:-5]
        elif i == len(table): #last row
            rate_dict[date] = rate_list
        else: #middle of row
            rate = str(item)[-9:-5]
            rate_list.append(float(rate))
    return rate_dict

def price_zero(yld,period):
    '''
    utility for pricing a zero coupon bond
    :param yld: yield of security
    :param period: period of bond, semi-annual basis
    :return: price of zero coupon bond
    '''
    num = 100 #par
    denom = pow((1+yld),period) #period will be based on semi-annual convention
    return (num / denom)

def bootstrap_curve(latest_curve):
    '''
    bootstrap a spot curve based on information found
    '''
    sm = latest_curve['6m']
    oy = latest_curve['1y']
    print(sm)
    print(oy)

def traded_curve(df):
    '''
    processes traded yield curve and outright prices of traded securities
    :param df: dataframe with information passed from scraping function
    :return: dictionary of maturity and average price
    '''

    #dates to iterate over
    dates = df.index
    today = datetime.date.today()

    #initialize lists to pass data into
    thirty_year = list()
    twenty_year = list()
    ten_year = list()
    seven_year = list()
    five_year = list()
    three_year = list()
    two_year = list()
    one_year = list()
    averages = dict()

    #work on this logic to get closer proxy for pricing
    for it,date in enumerate(dates):
        month,day,year = date.split(sep='/')
        month = int(month)
        day = int(day)
        year = int(year)
        if today.year+30 == year:
            to_append = df['avg_price'].iloc[it]
            thirty_year.append(to_append)
        elif today.year+20 == year:
            to_append = df['avg_price'].iloc[it]
            twenty_year.append(to_append)
        elif today.year+10 == year:
            to_append = df['avg_price'].iloc[it]
            ten_year.append(to_append)
        elif today.year+7 == year:
            to_append = df['avg_price'].iloc[it]
            seven_year.append(to_append)
        elif today.year+5 == year:
            to_append = df['avg_price'].iloc[it]
            five_year.append(to_append)
        elif today.year+3 == year:
            to_append = df['avg_price'].iloc[it]
            three_year.append(to_append)
        elif today.year+2 == year:
            to_append = df['avg_price'].iloc[it]
            two_year.append(to_append)
        elif today.year+1 == year:
            to_append = df['avg_price'].iloc[it]
            one_year.append(to_append)

    #get average price of each maturity year
    thirty_year_price = sum(thirty_year) / len(thirty_year)
    twenty_year_price = sum(twenty_year) / len(twenty_year)
    ten_year_price = sum(ten_year) / len(ten_year)
    seven_year_price = sum(seven_year) / len(seven_year)
    five_year_price = sum(five_year) / len(five_year)
    three_year_price = sum(three_year) / len(three_year)
    two_year_price = sum(two_year) / len(two_year)
    one_year_price = sum(one_year) / len(one_year)

    #add average price of securities for given maturity to dictionary
    averages[30] = thirty_year_price
    averages[20] = twenty_year_price
    averages[10] = ten_year_price
    averages[7] = seven_year_price
    averages[5] = five_year_price
    averages[3] = three_year_price
    averages[2] = two_year_price
    averages[1] = one_year_price
    return averages

def unit_one():
    '''
    unit testing of completed modules
    '''
    curve_dict = load_curve()
    # print(curve_dict)
    header = ['1m', '2m', '3m', '6m', '1y', '2y', '3y', '5y', '7y', '10y', '20y', '30y']
    dates = sorted(curve_dict.keys())
    latest_date = dates[-1]
    latest_curve = curve_dict[latest_date]
    print(latest_curve)
    latest_dict = dict(zip(header,latest_curve))
    pricing_data = price_scrape()
    curve = traded_curve(pricing_data)

unit_one()
