from django.conf.urls import url
from polls.views import chart,PageObjects,Charttype,CompanyName,redi
from polls.compare import compare,Compare_New
from polls.companies import companies



urlpatterns = [
    url('^$',redi),
    url('index', chart,name='dashboard_html'),
    url('PageObjects',PageObjects),
    url('Charttype',Charttype),
    url('CompanyName',CompanyName),
    url('companies',companies,name="companies_html"),
    url('compare',compare,name="compare_html"),
    url('Compare_New',Compare_New)
]


