from django.shortcuts import render
from fusioncharts import FusionCharts
import json
from copy import deepcopy
from django.views.decorators.csrf import csrf_exempt

path="./static"


try :
    from stock.data import get_x_compare, get_series, get_compare_table, get_compare_info_table, check_company,get_compare_list
except ImportError as e:
    print("Pyhton Version greater than 3 is required")

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


def compare(request):

    with open(path+"/stocks.json") as f:
        data = json.load(f)

    if (request.GET.get('reset', None)):
        data['Compare'] = []

    if(request.GET.get('reset_company', None)):
        answer=request.GET.get('reset_company', None)
        data['Compare'].remove(answer)

    companies = deepcopy(data['Compare'])
    companies.append(data['Company'])

    companies=list(set(companies))


    if(request.GET.get('duration', None)):
        data['duration']=int(request.GET.get('duration', None))



    cat,labelstep= get_x_compare(data['duration'], companies[0])
    series_data=get_series(data['duration'],companies)
    table=get_compare_table(companies)
    info_table=get_compare_info_table(companies)


    chartObj = FusionCharts(
         'msline',
         'ex1',
         '1000',
         '400',
         'chart-1',
         'json',
         """{
  "chart": {
    "caption": "Comparison Analysis",
    "yaxisname": "Return",
    "showhovereffect": "1",
    "numbersuffix": "%",
    "drawcrossline": "1",
    "plottooltext": "<b>$dataValue</b> % return for $seriesName",
    "theme": "fusion",
    "drawAnchors": "0",
    "labelStep":"""+str(labelstep)+
  """},
  "categories": [
    {
      "category":"""+cat+
        """}
  ],
  "dataset": """+series_data+
"""}""")

    with open(path+"/stocks.json", 'w') as f:
        json.dump(data, f)

    content={
        'company_list_body': get_compare_list(data['Compare']),
        'compare_graph': chartObj.render(),
        "compare_table" : table,
        "info_table":info_table,
        'duration_placeholder': chart_type_palceholder(data["duration"])
    }

    return render(request, 'compare.html',content)


@csrf_exempt
def Compare_New(request):
    with open(path+"/stocks.json") as f:
        data = json.load(f)

    answer = request.POST.get('company', False)

    if(answer):
        answer = answer.upper()
        if (check_company(answer)):
            data['Compare'].append(answer)

    with open(path+"/stocks.json", 'w') as f:
        json.dump(data, f)


    return compare(request)