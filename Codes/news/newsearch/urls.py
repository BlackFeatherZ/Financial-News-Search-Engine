from django.urls import path
from . import views
app_name = 'newsearch'

urlpatterns = [
path('',views.search_index, name='search_view'),
path('',views.QA, name='QA'),
]
#path('/index',views.index)
