
# coding: utf-8

# In[53]:


import pandas as pd
import json
from datetime import date
import datetime
import numpy as np
from dateutil.parser import parse


# In[54]:


path='./static/socgen/'
df=pd.read_csv(path+'data.csv')



# In[55]:

tickers=pd.read_csv(path+"tickers.csv")
tickers["Market Cap ($M)"]=(tickers["Market Cap ($M)"]/1000).round(2)
tickers["P/E Ratio"]=(tickers["P/E Ratio"]).round(2)
tickers["Dividend Yield"]=(tickers["Dividend Yield"]).round(4)
tickers=tickers.rename(columns={"GICS Sector":"Sector",'Market Cap ($M)':"Market Cap"})
tickers=tickers[tickers["Symbol"].isin(df['symbol'])]
tickers["GICS Sub Industry"]=tickers["GICS Sub Industry"].str.replace('& ',',')
tickers.reset_index(drop=True,inplace=True)


df['date']=pd.to_datetime(df['date']).dt.date
df=df.sort_values('date',ascending=False)


# In[56]:


df.date=pd.to_datetime(df.date).dt.strftime('%d-%b-%Y')
df["tooltext"]="<b>"+df["date"]+"<br>Open: <b>$openDataValue</b><br>Close: <b>$closeDataValue</b><br>High: <b>$highDataValue</b><br>Low: <b>$lowDataValue</b><br>Volume: <b>$volumeDataValue</b>"


# In[119]:
returns={"6 Months":180,
         "1 Year" : 365,
         "3 Year" : 1095,
         "4 year" : 1400,
}

comp_returns_list=["1 Month","3 Months","6 Months","1 Year","2 Years","3 Years","4 years","5 Years"]
compareinfo=["Sector","Market Cap","P/E Ratio","Dividend Yield"]

up='fa fa-level-up c-red-500'
down='fa fa-level-down c-red-500'

comp_returns={"1 Month":30,
"3 Months": 90,
"6 Months":180,
"1 Year" : 365,
"2 Years" :730,
"3 Years" : 1095,
"4 years" : 1460,
"5 Years":1825
}


def get_ind(duration, symbol):
    data = df[df["symbol"] == symbol]
    data = data.reset_index(drop=True)

    end_date = data["date"].iloc[-1]
    end_date = parse(end_date)
    end_date = end_date.date()
    ind = []
    while (len(ind) == 0):
        to_date = date(2016, 12, 30) - datetime.timedelta(days=duration)
        if (end_date > to_date):
            to_date = end_date
        to_date = to_date.strftime('%d-%b-%Y')
        ind = data[data["date"] == to_date].index
        duration += 1

    ind = ind[0]

    data = data[0:ind]
    data = data.iloc[::-1]
    data = data.reset_index(drop=True)
    data = data.reset_index()

    data.columns = ["x", "label", "symbol", "open", "close", "low", "high", "volume", "tooltext"]

    return data


def get_json(duration, symbol):
    data = get_ind(duration, symbol)

    label_skip = int(len(data) / 7)

    cat = data.iloc[::label_skip, :]
    cat = cat[["x", "label"]]

    cat_json = cat.to_json(orient="records")

    dataset = data[["x", "open", "close", "low", "high", "volume", "tooltext"]]
    dataset_json = dataset.to_json(orient="records")

    return cat_json, dataset_json


def get_allcompanies(pd_df):
    pd_df = pd_df.reset_index(drop=True)
    df2 = pd_df[pd_df["date"] == pd_df["date"][501]]
    df1 = pd_df[pd_df["date"] == pd_df["date"][0]]
    df2 = df2.rename(columns={"close": "prev_close"})
    data = pd.merge(df1, df2[["symbol", "prev_close"]], on=["symbol"], how="left")
    data['change'] = data["close"] - data["prev_close"]
    data['per_change'] = (data['change'] / data['close']) * 100
    data[['open', 'close', 'low', 'high', 'prev_close', 'change', "per_change"]] = data[
        ['open', 'close', 'low', 'high', 'prev_close', 'change', "per_change"]].round(2)
    return data


def comapany_list_data(data, sector, subsector):
    if (sector == "ALL"):
        return data

    elif (subsector == "ALL"):
        data = data[data["Sector"] == sector]
    else:
        data = data[data["GICS Sub Industry"] == subsector]

    data.reset_index(drop=True, inplace=True)

    return data


def company_list(sector, subsector):
    data = get_allcompanies(df)
    data = data.rename(columns={"symbol": "Symbol"})
    data = pd.merge(data, tickers[["Symbol", "Sector", "GICS Sub Industry"]], on=["Symbol"], how="left")

    data = comapany_list_data(data, sector, subsector)

    company_render = ""
    for i in range(len(data)):
        company_render += "<tr>"
        company_render += "<td><a href='/index?company_name=" + str(data["Symbol"].iloc[i]) + """'>""" + str(
            data["Symbol"].iloc[i]) + "</a></td>"
        company_render += "<td>" + str(data["close"].iloc[i]) + "</td>"
        company_render += "<td>" + str(data["change"].iloc[i]) + "</td>"
        company_render += "<td>" + str(data["per_change"].iloc[i]) + "</td>"
        company_render += "<td>" + str(data["open"].iloc[i]) + "</td>"
        company_render += "<td>" + str(data["high"].iloc[i]) + "</td>"
        company_render += "<td>" + str(data["low"].iloc[i]) + "</td>"
        company_render += "<td>" + str(data["prev_close"].iloc[i]) + "</td>"
        company_render += '</tr>'

    return company_render


def get_company_series(duration, symbol, if_return):
    data = get_ind(duration, symbol)

    high = np.max(data["high"]).round(2)
    low = np.min(data["low"]).round(2)

    data = data[["x", "label", "symbol", "close"]]
    data["start"] = data["close"][0]
    data["return"] = ((data["close"] - data["start"]) / data["start"]).round(2)
    data["return"] = (data["return"] * 100).round(2)

    if (if_return == 1):
        return data["return"].iloc[-1]

    if (if_return == 2):
        return data["return"].iloc[-1], high, low

    dataset = data[["x", "return"]]
    dataset.columns = ["x", "value"]

    dataset_json = dataset.to_json(orient="records")

    series = {}
    series["seriesname"] = symbol
    series["data"] = json.loads(dataset_json)
    return series

def get_series(duration, companies):
    series_dataset = []
    for i in companies:
        series_dataset.append(get_company_series(duration, i,0))

    series_dataset = json.dumps(series_dataset)

    return series_dataset


def get_x_compare(duration, symbol):
    data = get_ind(duration, symbol)

    cat = data[["x", "label"]]
    labelstep = int(len(cat) / 7)
    cat_json = cat.to_json(orient="records")

    return cat_json, labelstep


def get_compare_table(companies):
    head = "<thead><tr><th>index</th>"
    for i in companies:
        head += "<th>" + i + "</th>"
    head += "</tr></thead>"

    comp_return = {}
    for i in returns.keys():
        ret = []
        for j in companies:
            ret.append(get_company_series(returns[i], j, 1).round(1))

        comp_return[i] = ret

    body = "<tbody>"
    for i in comp_return.keys():
        body += "<tr><td>" + i + "</td>"
        for j in comp_return[i]:
            if (j > 0):
                color = "green"
            else:
                color = "red"

            body += "<td><font color='" + color + "'>" + str(j) + "%</font></td>"

        body += "</tr>"
    body += "</tbody>"

    return head + body


def get_return_table(symbol):
    body = ""
    for i in range(0, len(comp_returns_list), 2):
        body += "<tr>"
        body += "<td>" + comp_returns_list[i] + "</td>"
        a = get_company_series(comp_returns[comp_returns_list[i]], symbol, 1).round(1)
        arrow = ""
        if (a > 0):
            arrow = up
            color = "green"
        else:
            arrow = down
            color = "red"

        body += "<td><font color='" + color + "'>" + str(np.abs(a)) + " %<i class='" + arrow + "'></i></font></td>"

        body += "<td>" + comp_returns_list[i + 1] + "</td>"
        a = get_company_series(comp_returns[comp_returns_list[i + 1]], symbol, 1)
        arrow = ""
        if (a > 0):
            arrow = up
            color = "green"
        else:
            arrow = down
            color = "red"
        body += "<td><font color='" + color + "'>" + str(np.abs(a)) + " %<i class='" + arrow + "'></i></font></td>"

        body += "</tr>"

    return body


def get_scroll_bar():
    data = get_allcompanies(df)
    data = data[["symbol", "close", "change"]]

    body = ""
    for i in range(len(data)):
        body += "<div class='scroll'>"
        body += "<a href='/index?company_name=" + str(data["symbol"].iloc[i]) + """'>"""
        body += '<div class="stat-heading">' + str(data["symbol"].iloc[i]) + '</div>'

        if (data["change"].iloc[i] > 0):
            arrow = "pe-7s-angle-up"
            color = "green"
        else:
            arrow = "pe-7s-angle-down"
            color = "red"

        body += "<div class='stat-text'><span>" + str(data["close"].iloc[i])
        body += "<i class='" + arrow + "'></i>"
        body += "<font color='" + color + "'style='font-size: 0.8em;'>" + str(
            data["change"].iloc[i]) + "</font></span></div>"
        body += "</a></div> "

    return body


def get_Companyinfo(symbol):
    ind = tickers[tickers["Symbol"] == symbol].index

    if (len(ind) == 0):
        ind = [134]

    body = "<tr><td>Sector</td><td>"
    body += str(tickers["Sector"].iloc[ind[0]])
    body += '</td></tr><tr><td>Market Cap</td><td>$ '
    body += str(tickers["Market Cap"].iloc[ind[0]])
    body += 'B</td></tr><tr><td>P/E Ratio</td><td>'
    body += str(tickers["P/E Ratio"].iloc[ind[0]])
    body += '</td></tr><tr><td>Dividend Yield</td><td>'
    body += str(tickers["Dividend Yield"].iloc[ind[0]])
    body += '</td></tr>'

    return body


def get_name(symbol):
    ind=tickers[tickers["Symbol"]==symbol].index
    if(len(ind)==0):
        return symbol
    return tickers.at[ind[0],"Security"]


def get_Compareinfo(symbol, col):
    ind = tickers[tickers["Symbol"] == symbol].index

    if (len(ind) == 0):
        ind = [134]

    return tickers[col].iloc[ind[0]]


def get_compare_info_table(companies):
    head = "<thead><tr><th>index</th>"
    for i in companies:
        head += "<th>" + i + "</th>"
    head += "</tr></thead>"

    comp_return = {}
    for i in compareinfo:
        ret = []
        for j in companies:
            ret.append(get_Compareinfo(j, i))

        comp_return[i] = ret


    body = "<tbody>"
    for i in comp_return.keys():
        body += "<tr><td>" + i + "</td>"
        for j in comp_return[i]:
            body += "<td>" + str(j) + "</td>"

        body += "</tr>"
    body += "</tbody>"

    return head + body


def get_sector(sector):
    if (sector == "ALL"):
        sector = "Sector"

    sectors = list(tickers["Sector"])
    sectors = list(set(sectors))
    sectors = ["ALL"] + sectors

    body = '<button class="btn btn-secondary dropdown-toggle" type="button" id="dropdownMenu" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">'
    body += sector
    body += "</button><div class='dropdown-menu' aria-labelledby='dropdownMenu'>"
    for i in sectors:
        body += '<a class="dropdown-item" href="/companies?sector=' + str(i) + '">' + str(i) + '</a>'

    body += "</div>"

    return body


def get_subsector(sector, subplace):
    if (sector == "ALL"):
        subplace = "Sub Sector"
        subsectors = ["ALL"]


    else:
        subsectors = list(tickers[tickers["Sector"] == sector]["GICS Sub Industry"])
        subsectors = list(set(subsectors))
        subsectors = ["ALL"] + subsectors

    if (subplace == "ALL"):
        subplace = "Sub Sector"

    body = '<button class="btn btn-secondary dropdown-toggle" type="button" id="dropdownMenu" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">'
    body += subplace
    body += "</button><div class='dropdown-menu' aria-labelledby='dropdownMenu'>"
    for i in subsectors:
        body += '<a class="dropdown-item" href="/companies?subsector=' + str(i) + '">' + str(i) + '</a>'
    body += "</div>"
    return body


def check_company(company):
    return pd.Series(company).isin(df["symbol"])[0]


def get_compare_list(companies):
    body = ""
    for i in companies:
        body += """<button class="button"   onclick='location.href="/compare?reset_company=""" + str(
            i) + """"'>""" + str(i)
        body += """<i class="fa fa-close" style="float:right; display:inline;"></i></button>"""

    return body


