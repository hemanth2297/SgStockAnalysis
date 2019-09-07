from django.shortcuts import render
import json

try :
    from stock.data import company_list
    from stock.data import get_sector, get_subsector
except ImportError as e:
    print("Python Version greater than 3 is required")
path="./static"


def companies(request):

    with open(path+"/stocks.json") as f:
        data = json.load(f)




    if (request.GET.get('subsector', None)):
        data["subsector"]=request.GET.get('subsector', None)

    elif(request.GET.get('sector', None)):
        data["sector"]=request.GET.get('sector', None)
        data["subsector"]="ALL"

    sector=get_sector(data["sector"])

    sub_sector=get_subsector(data["sector"],data["subsector"])

    content={
        'company_list' :company_list(data["sector"],data["subsector"]),
        'sector':sector,
        'sub_sector':sub_sector

    }

    with open(path+"/stocks.json", 'w') as f:
        json.dump(data, f)

    return render(request, 'companies.html',content)