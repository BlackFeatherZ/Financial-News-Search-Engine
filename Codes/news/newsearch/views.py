from django.shortcuts import render

# Create your views here.
from .news_query import booksearch_core
from django.views.decorators.csrf import csrf_exempt
import json
import operator


history = []
completion = []

def search_index(request):
 results = []
 search_term = ""
 type = ""
 chinese = 0 # 是否用中文搜索，默认为否
 date = 0 # 是否按日期排序，默认为否
 qa = 0
 news = 0 # 若为0，则需要初始页为：http://127.0.0.1:8000/search/?news=1
 txt = 0
 doc = 0
 pdf = 0
 img = 0
 mp4 = 0
 latest = 0
 other_site = ""
 recommend = ""
 page_limit = 20 
 
 #if request.method == 'POST':
  #search_term = request.POST.get('keyword')
 
 #if request.GET.get('type2'):
  #type = request.GET['type2']
 #else:
  #type = request.GET['type1']
 if request.GET.get('history'):
  search_term = request.GET['history']
 elif request.GET.get('keyword'):
  search_term = request.GET['keyword']
  
  #多类搜索test
 if request.GET.get('cn'):
  chinese = 1
 if request.GET.get('qa'):
  qa = 1
 if request.GET.get('date'):
  date = 1
 if request.GET.get('news'):
  news = 1
 if request.GET.get('txt'):
  txt = 1
 if request.GET.get('doc'):
  doc = 1
 if request.GET.get('pdf'):
  pdf = 1
 if request.GET.get('img'):
  img = 1
 if request.GET.get('mp4'):
  mp4 = 1
 if request.GET.get('latest'):
  latest = 1
 if request.GET.get('recommend'):
  recommend = request.GET['recommend']
 settings = [chinese, qa, date, news, txt, doc, pdf, img, mp4, latest, recommend]
 

  
 #if type=="cn": # 前端选择“中文新闻”后，使type变为cn
  #chinese = 1
 #elif type=="qa": # use semantic search foe questions
  #qa = 1
 #elif type=="bing": # use bing for aggregation search
  #other_site = type
 #elif type!="news" and type!="":
  #bool_search = 1 # 若不搜索news，用bool搜索
 history_nodup = []
 if search_term != "":
  history.append(search_term)
 # remover duplicates:
 history1 = set(history)
 history_nodup = list(history1)
 temp = 0
 # 找出最大热搜：
 max_h = ""
 for h in history:
     if history.count(h) > temp:
         max_h = h
         temp = history.count(h)
 results = booksearch_core(index = "news", keyword = 
search_term, count = 10, settings=settings)
 print(results)
 black_word = 0 # indicate whether there are words in black list
 black_list = []
 with open('/root/Downloads/news/newsearch/blacklist.txt', 'r') as file:
  for line in file:
   black_list.append(line.strip())
 for r in results[2]:
  if r not in completion:
   completion.append(r)
 no_results = 0
 if results[0] == [[],[],[],[],[],[],[],[]] and results[4] == []:
  no_results = 1
 if search_term in black_list:#若有black list词，则不显示结果
  black_word = 1 
  context = {'results': (),  'search_term': search_term, 'suggestion': [], 'completion': completion, 'recommendation': results[3], 'latest': results[4],'history': history_nodup, 'hot': max_h, 'black_word': black_word,  "other_site": other_site, "date": date, "settings":settings, "no_results":no_results}
 else: #无black，正常（tuple不可修改）
  context = {'results': results[0],  'search_term': search_term, 'suggestion': results[1], 'completion': completion, 'recommendation': results[3], 'latest': results[4], 'history': history_nodup, 'hot': max_h , 'black_word': black_word,  "other_site": other_site, "date": date,"settings":settings,"no_results":no_results}
 return render(request, 'search.html', context)
 
def index(request):
 results = []
 search_term = ""
 type = ""
 chinese = 0 # 是否用中文搜索，默认为否
 date = 0 # 是否按日期排序，默认为否
 qa = 0
 news = 0 # 若为0，则需要初始页为：http://127.0.0.1:8000/search/?news=1
 txt = 0
 doc = 0
 pdf = 0
 img = 0
 mp4 = 0
 latest = 0
 other_site = ""
 recommend = ""
 page_limit = 20 # 加上？
 
 #if request.method == 'POST':
  #search_term = request.POST.get('keyword')
 
 #if request.GET.get('type2'):
  #type = request.GET['type2']
 #else:
  #type = request.GET['type1']
 if request.GET.get('history'):
  search_term = request.GET['history']
 elif request.GET.get('keyword'):
  search_term = request.GET['keyword']
  
  #多类搜索test
 if request.GET.get('cn'):
  chinese = 1
 if request.GET.get('qa'):
  qa = 1
 if request.GET.get('date'):
  date = 1
 if request.GET.get('news'):
  news = 1
 if request.GET.get('txt'):
  txt = 1
 if request.GET.get('doc'):
  doc = 1
 if request.GET.get('pdf'):
  pdf = 1
 if request.GET.get('img'):
  img = 1
 if request.GET.get('mp4'):
  mp4 = 1
 if request.GET.get('latest'):
  latest = 1
 if request.GET.get('recommend'):
  recommend = request.GET['recommend']
 settings = [chinese, qa, date, news, txt, doc, pdf, img, mp4, latest, recommend]
 

  
 #if type=="cn": # 前端选择“中文新闻”后，使type变为cn
  #chinese = 1
 #elif type=="qa": # use semantic search foe questions
  #qa = 1
 #elif type=="bing": # use bing for aggregation search
  #other_site = type
 #elif type!="news" and type!="":
  #bool_search = 1 # 若不搜索news，用bool搜索
 history_nodup = []
 if search_term != "":
  history.append(search_term)
 # remover duplicates:
 history1 = set(history)
 history_nodup = list(history1)
 
 #temp = 0
 # 找出最大热搜：
 #max_h = ""
 #for h in history:
  #   if history.count(h) > temp:
   #      max_h = h
    #     temp = history.count(h)
         
 count_set = {}  # 存放元素和出现次数的字典，key为元素,value为出现次数
 for item in history_nodup:
  count_set[item] = history.count(item)
 sorted_history = sorted(count_set.items(), key=operator.itemgetter(1))

 max = []  # 存放最后的结果
 for item in sorted_history[::-1]: # 按value值从大到小排序
  max.append(item[0])
 max = max[0:5]
 
 results = booksearch_core(index = "news", keyword = 
search_term, count = 10, settings=settings)
 print(results)
 black_word = 0 # indicate whether there are words in black list
 black_list = []
 with open('/root/Downloads/news/newsearch/blacklist.txt', 'r') as file:
  for line in file:
   black_list.append(line.strip())
 for r in results[2]:
  if r not in completion:
   completion.append(r)
 no_results = 0
 if results[0] == [[],[],[],[],[],[],[],[]]:
  no_results = 1
 if search_term in black_list:#若有black list词，则不显示结果
  black_word = 1 
  context = {'results': (),  'search_term': search_term, 'suggestion': [], 'completion': completion, 'recommendation': results[3], 'latest': results[4],'history': history_nodup, 'hot': max, 'black_word': black_word,  "other_site": other_site, "date": date, "settings":settings, "no_results":no_results}
 else: #无black，正常（tuple不可修改）
  context = {'results': results[0],  'search_term': search_term, 'suggestion': results[1], 'completion': completion, 'recommendation': results[3], 'latest': results[4], 'history': history_nodup, 'hot': max , 'black_word': black_word,  "other_site": other_site, "date": date,"settings":settings,"no_results":no_results}
 return render(request, 'index.html', context)
 
def QA(request):
 results = []
 search_term = ""
 type = ""
 chinese = 0 # 是否用中文搜索，默认为否
 date = 0 # 是否按日期排序，默认为否
 qa = 0
 news = 0 # 若为0，则需要初始页为：http://127.0.0.1:8000/search/?news=1
 txt = 0
 doc = 0
 pdf = 0
 img = 0
 mp4 = 0
 latest = 0
 other_site = ""
 recommend = ""
 page_limit = 20 # 加上？
 
 #if request.method == 'POST':
  #search_term = request.POST.get('keyword')
 
 #if request.GET.get('type2'):
  #type = request.GET['type2']
 #else:
  #type = request.GET['type1']
 if request.GET.get('history'):
  search_term = request.GET['history']
 elif request.GET.get('keyword'):
  search_term = request.GET['keyword']
  
  #多类搜索test
 if request.GET.get('cn'):
  chinese = 1
 if request.GET.get('qa'):
  qa = 1
 if request.GET.get('date'):
  date = 1
 if request.GET.get('news'):
  news = 1
 if request.GET.get('txt'):
  txt = 1
 if request.GET.get('doc'):
  doc = 1
 if request.GET.get('pdf'):
  pdf = 1
 if request.GET.get('img'):
  img = 1
 if request.GET.get('mp4'):
  mp4 = 1
 if request.GET.get('latest'):
  latest = 1
 if request.GET.get('recommend'):
  recommend = request.GET['recommend']
 settings = [chinese, qa, date, news, txt, doc, pdf, img, mp4, latest, recommend]
 

  
 #if type=="cn": # 前端选择“中文新闻”后，使type变为cn
  #chinese = 1
 #elif type=="qa": # use semantic search foe questions
  #qa = 1
 #elif type=="bing": # use bing for aggregation search
  #other_site = type
 #elif type!="news" and type!="":
  #bool_search = 1 # 若不搜索news，用bool搜索
 history_nodup = []
 if search_term != "":
  history.append(search_term)
 # remover duplicates:
 history1 = set(history)
 history_nodup = list(history1)
 temp = 0
 # 找出最大热搜：
 max_h = ""
 for h in history:
     if history.count(h) > temp:
         max_h = h
         temp = history.count(h)
 results = booksearch_core(index = "news", keyword = 
search_term, count = 10, settings=settings)
 print(results)
 black_word = 0 # indicate whether there are words in black list
 black_list = []
 with open('/root/Downloads/news/newsearch/blacklist.txt', 'r') as file:
  for line in file:
   black_list.append(line.strip())
 for r in results[2]:
  if r not in completion:
   completion.append(r)
 no_results = 0
 if results[0] == [[],[],[],[],[],[],[],[]]:
  no_results = 1
 if search_term in black_list:#若有black list词，则不显示结果
  black_word = 1 
  context = {'results': (),  'search_term': search_term, 'suggestion': [], 'completion': completion, 'recommendation': results[3], 'latest': results[4],'history': history_nodup, 'hot': max_h, 'black_word': black_word,  "other_site": other_site, "date": date, "settings":settings, "no_results":no_results}
 else: #无black，正常（tuple不可修改）
  context = {'results': results[0],  'search_term': search_term, 'suggestion': results[1], 'completion': completion, 'recommendation': results[3], 'latest': results[4], 'history': history_nodup, 'hot': max_h , 'black_word': black_word,  "other_site": other_site, "date": date,"settings":settings,"no_results":no_results}
 return render(request, 'QA.html', context)
 
def backend(request):
 results = []
 search_term = ""
 type = ""
 chinese = 0 # 是否用中文搜索，默认为否
 date = 0 # 是否按日期排序，默认为否
 qa = 0
 news = 0 # 若为0，则需要初始页为：http://127.0.0.1:8000/search/?news=1
 txt = 0
 doc = 0
 pdf = 0
 img = 0
 mp4 = 0
 latest = 0
 other_site = ""
 recommend = ""
 page_limit = 20 # 加上？
 
 #if request.method == 'POST':
  #search_term = request.POST.get('keyword')
 
 #if request.GET.get('type2'):
  #type = request.GET['type2']
 #else:
  #type = request.GET['type1']
 if request.GET.get('history'):
  search_term = request.GET['history']
 elif request.GET.get('keyword'):
  search_term = request.GET['keyword']
  
  #多类搜索test
 if request.GET.get('cn'):
  chinese = 1
 if request.GET.get('qa'):
  qa = 1
 if request.GET.get('date'):
  date = 1
 if request.GET.get('news'):
  news = 1
 if request.GET.get('txt'):
  txt = 1
 if request.GET.get('doc'):
  doc = 1
 if request.GET.get('pdf'):
  pdf = 1
 if request.GET.get('img'):
  img = 1
 if request.GET.get('mp4'):
  mp4 = 1
 if request.GET.get('latest'):
  latest = 1
 if request.GET.get('recommend'):
  recommend = request.GET['recommend']
 settings = [chinese, qa, date, news, txt, doc, pdf, img, mp4, latest, recommend]
 

  
 #if type=="cn": # 前端选择“中文新闻”后，使type变为cn
  #chinese = 1
 #elif type=="qa": # use semantic search foe questions
  #qa = 1
 #elif type=="bing": # use bing for aggregation search
  #other_site = type
 #elif type!="news" and type!="":
  #bool_search = 1 # 若不搜索news，用bool搜索
 history_nodup = []
 if search_term != "":
  history.append(search_term)
 # remover duplicates:
 history1 = set(history)
 history_nodup = list(history1)
 temp = 0
 # 找出最大热搜：
 max_h = ""
 for h in history:
     if history.count(h) > temp:
         max_h = h
         temp = history.count(h)
 history_num = []
 for h in history_nodup:
     history_num.append(history.count(h))
 results = booksearch_core(index = "news", keyword = 
search_term, count = 10, settings=settings)
 print(results)
 black_word = 0 # indicate whether there are words in black list
 black_list = []
 with open('/root/Downloads/news/newsearch/blacklist.txt', 'r') as file:
  for line in file:
   black_list.append(line.strip())
 for r in results[2]:
  if r not in completion:
   completion.append(r)
 no_results = 0
 if results[0] == [[],[],[],[],[],[],[],[]]:
  no_results = 1
 if search_term in black_list:#若有black list词，则不显示结果
  black_word = 1 
  context = {'results': (),  'search_term': search_term, 'suggestion': [], 'completion': completion, 'recommendation': results[3], 'latest': results[4],'history_num': history_num, 'hot': max_h, 'black_word': black_word,  "other_site": other_site, "date": date, "settings":settings, "history":history_nodup, "no_results": no_results}
 else: #无black，正常（tuple不可修改）
  context = {'results': results[0],  'search_term': search_term, 'suggestion': results[1], 'completion': completion, 'recommendation': results[3], 'latest': results[4], 'history_num': history_num, 'hot': max_h , 'black_word': black_word,  "other_site": other_site, "date": date,"settings":settings, "history": history_nodup, "no_results": no_results}
 #return render(request, 'backend.html', {"history_num":json.dumps(context["history_num"]), "history":json.dumps(context["history"])})
 return render(request, 'backend.html', context)
