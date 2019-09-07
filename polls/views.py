from django.shortcuts import render
from fusioncharts import FusionCharts
from django.views.decorators.csrf import csrf_exempt
import json

try :
    from stock.data import get_json,company_list,get_return_table,get_scroll_bar,get_Companyinfo,get_name,get_company_series
    from stock.data import get_sector, check_company
except ImportError as e:
    raise ImportError("Pyhton Version greater than 3 is required")

path="./static"




def chart_type_palceholder(dur):
    if(dur==30):
        return '1 Month'
    if(dur==1825):
        return '5 Years'
    if(dur==183):
        return '6 Months'
    if(dur==365):
        return '1 Year'
    if(dur==1100):
        return '3 Years'
    else:
        return 'Duration'


@csrf_exempt
def chart(request):



    with open(path+"/stocks.json") as f:
        data = json.load(f)

    if(request.GET.get('company_name', None)):

        com=request.GET.get('company_name', None)
        if(check_company(com)):
            data['Company']=request.GET.get('company_name', None)


    if(request.GET.get('duration', None)):
        data['duration']=int(request.GET.get('duration', None))

    if(request.GET.get('chart_type', None)):
        data['chart_type']=request.GET.get('chart_type', None)

    if(request.GET.get('volume', None)):
        data['volume']=request.GET.get('volume', None)


    cat,dataset=get_json(data['duration'],data['Company'])
    return_table=get_return_table(data['Company'])
    comp_info=get_Companyinfo(data['Company'])
    Name=get_name(data['Company'])

    ret,high,low=get_company_series(data['duration'],data['Company'],2)

    scroll=get_scroll_bar()

    chartObj = FusionCharts(
         'candlestick',
         'ex1',
         '1000',
         '400',
         'chart-1',
         'json',
         """{
  "chart": {
    "caption":'"""+Name+""" ',
    "subcaption": "Stock Analysis",
    "numberprefix": "$",
    "pyaxisname": "Price (USD)",
    "vyaxisname": "Volume traded",
    "theme": "fusion",
    "plotpriceas":'""" + data['chart_type']+ """',
    "showvolumechart":'"""+str(data["volume"])+""" ',
    "vnumberprefix": "$"
  },
     "categories": [
        {
          "category": """+cat+
        """}
      ],
  "dataset": [
    {
      "data": """+dataset+
         """}
   ]
 }""")
    with open(path+"/stocks.json", 'w') as f:
        json.dump(data, f)

    content={
        'output': chartObj.render(),
        'duration_placeholder':chart_type_palceholder(data["duration"]),
        'chart_placeholder' :data['chart_type'],
        'company':data['Company'],
        'return_table':return_table,
        'scroll':scroll,
        'economical_indicators':comp_info,
        'ret':ret,
        'high':high,
        'low':low
    }


    return render(request, 'index.html', content)


@csrf_exempt
def PageObjects(request):
    with open(path+"/stocks.json") as f:
        data = json.load(f)

    answer = request.POST.get('duration', False)
    data['duration'] = int(answer)

    with open(path+"/stocks.json", 'w') as f:
        json.dump(data, f)

    return chart(request)


@csrf_exempt
def Charttype(request):
    with open(path+"/stocks.json") as f:
        data = json.load(f)

    answer = request.POST.get('chart_type', False)
    data['chart_type'] = answer

    with open(path+"/stocks.json", 'w') as f:
        json.dump(data, f)


    return chart(request)


@csrf_exempt
def CompanyName(request):
    with open(path+"/stocks.json") as f:
        data = json.load(f)

    answer = request.POST.get('company', False)

    if(answer):
        answer = answer.upper()
        if(check_company(answer)):
            data['Company'] = answer

    with open(path+"/stocks.json", 'w') as f:
        json.dump(data, f)


    return chart(request)




from django.shortcuts import redirect

def redi(request):
    return redirect('/index')