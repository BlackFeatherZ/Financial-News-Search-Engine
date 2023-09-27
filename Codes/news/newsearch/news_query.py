from elasticsearch import Elasticsearch
import sys
import json
import re
import tensorflow_hub as hub
import numpy as np
from selenium import webdriver

def crawl(keyword):
 browser = webdriver.Firefox(executable_path='/bin/geckodriver')
 url = 'http://www.cninfo.com.cn/new/fulltextSearch?notautosubmit=&keyWord=' + keyword
 #url = 'https://www.business-standard.com/search?q=' + keyword
 browser.get(url)
 data = browser.page_source
 browser.quit()
 p_title = '(.*?)'
 p_href = '(.*?)'
 p_date = '<span class="time">(.*?)</span>'
 title = re.findall(p_title, data)
 href = re.findall(p_href, data)
 date = re.findall(p_date, data, re.S)
 results = []
 for i in range(len(title)):
  title[i] = re.sub(r'<.*?>', '', title[i])
  href[i] = 'http://www.cninfo.com.cn' + href[i]
  #href[i] = 'https://www.business-standard.com' + href[i]
  href[i] = re.sub('amp;', '', href[i])
  #date[i] = date[i] #.split(' ')[0]
  results.append([title[i], href[i]])
 return results

def qa_results(results, qa_array):
 for hit in results['hits']['hits']:
   title = hit['_source']['title']
   text = hit['_source']['body']
   lineNum = 0
   score = hit['_score']
   url = ""
   date = ""
   site = ""
   type = ""
   doc_id = re.sub(r'(.*) (.*)', r'\1', hit['_id'])
   result_tuple = (score, title, date, site, str(lineNum), text, url,type)
   qa_array.append(result_tuple)

def other_results(results, other_array, es, index):
  for hit in results['hits']['hits']:
   title = hit['_source']['title']
   text = hit['_source']['text']
   lineNum = hit['_source']['lineNum']
   score = hit['_score']
   url = hit['_source']['url']
   date = hit['_source']['date'][0:10]
   site = hit['_source']['site']
   type = hit['_source']['type']
   doc_id = re.sub(r'(.*) (.*)', r'\1', hit['_id'])
   if lineNum > 1:
    previousLine = es.get(index=index, id=doc_id+" "+str(lineNum-1))
   try:
    nextLine = es.get(index=index, id=doc_id+" "+str(lineNum+1))
    result_tuple = (score, title, date, site, str(lineNum), text + nextLine['_source']['text'], url,type)
   except:
    result_tuple = (score, title, date, site, str(lineNum), text, url,type)
   other_array.append(result_tuple)
   
def cn_results(results, cn_array, es, index):
  for hit in results['suggest']['chinese-news-suggest'][0]['options']:
   title = hit['_source']['title']
   text = hit['_source']['text']
   lineNum = hit['_source']['lineNum']
   score = hit['_score']
   url = hit['_source']['url']
   date = hit['_source']['date']
   site = hit['_source']['site']
   type = hit['_source']['type']
   doc_id = re.sub(r'(.*) (.*)', r'\1', hit['_id'])
   if lineNum > 1:
    previousLine = es.get(index=index, id=doc_id+" "+str(lineNum-1))
   try:
    nextLine = es.get(index=index, id=doc_id+" "+str(lineNum+1))
    result_tuple = (score, title, date, site, str(lineNum), text + nextLine['_source']['text'], url,type)
   except:
    result_tuple = (score, title, date, site, str(lineNum), text, url,type)
   cn_array.append(result_tuple)

def booksearch_core(index="", keyword="", count="", settings=[0,0,0,0,0,0,0,0,0,0]):
 es = Elasticsearch(hosts="http://elastic:changeme@localhost:9200")
 cn_array = []
 qa_array = []
 news_array = []
 txt_array = []
 doc_array = []
 pdf_array = []
 img_array = []
 mp4_array = []
 
 if settings[1] == 1: # qa search
  #model = hub.KerasLayer('/root/Downloads/news/newsearch/universal-sentence-encoder_4')
  model = hub.KerasLayer('/root/Downloads/A11/nnlm-en-dim50_2')
  query_vector = np.asarray(model([keyword])[0]).tolist()
  script_query = {"script_score": {"query": {"match_all": {}},"script": {"source": "cosineSimilarity(params.query_vector, 'title_vector') + 1.0","params": {"query_vector": query_vector}}}}
  results = es.search(index='qa',body={"size": 5,"query": script_query,"_source": {"includes": ["title", "body"]}})
  qa_results(results, qa_array)
 else:
  if settings[0] == 1: # 用中文或拼音搜索
   results = es.search(index="newscn",body={"size": count, "suggest": {"chinese-news-suggest": {"text":keyword, "completion": {"field": "title", "size": 10, "skip_duplicates": "true"}}}})
   cn_results(results, cn_array, es, index)
  if settings[3] == 1: # news类型不用bool搜索
   if settings[2] == 1: # 按日期排序
    results = es.search(index=index,body={"size": count,"query": {"match": {"text": {"query": keyword}}}, "sort":{"date":{"order":"desc"}}})
   else:
    results = es.search(index=index,body={"size": count,"query": {"match": {"text": {"query": keyword}}}})
   other_results(results, news_array, es, index)
  if settings[4] == 1: # 其他类型用bool搜索
   if settings[2] == 1: # 按日期排序 
    results = es.search(index=index,body={"size": count,"query": {"bool": {"should": [{"term":{"text": keyword}},{"term":{"type":"txt"}}]}},"sort":{"date":{"order":"desc"}}})
   else:
    results = es.search(index=index,body={"size": count,"query": {"bool": {"should": [{"term":{"text": keyword}},{"term":{"type":"txt"}}]}}})
   other_results(results, txt_array, es, index)
  if settings[5] == 1: # 其他类型用bool搜索
   if settings[2] == 1: # 按日期排序 
    results = es.search(index=index,body={"size": count,"query": {"bool": {"should": [{"term":{"text": keyword}},{"term":{"type":"doc"}}]}},"sort":{"date":{"order":"desc"}}})
   else:
    results = es.search(index=index,body={"size": count,"query": {"bool": {"should": [{"term":{"text": keyword}},{"term":{"type":"doc"}}]}}})
   other_results(results, doc_array, es, index)
  if settings[6] == 1: # 其他类型用bool搜索
   if settings[2] == 1: # 按日期排序 
    results = es.search(index=index,body={"size": count,"query": {"bool": {"should": [{"term":{"text": keyword}},{"term":{"type":"pdf"}}]}},"sort":{"date":{"order":"desc"}}})
   else:
    results = es.search(index=index,body={"size": count,"query": {"bool": {"should": [{"term":{"text": keyword}},{"term":{"type":"pdf"}}]}}})
   other_results(results, pdf_array, es, index)
  if settings[7] == 1: # 其他类型用bool搜索
   if settings[2] == 1: # 按日期排序 
    results = es.search(index=index,body={"size": count,"query": {"bool": {"should": [{"term":{"text": keyword}},{"term":{"type":"img"}}]}},"sort":{"date":{"order":"desc"}}})
   else:
    results = es.search(index=index,body={"size": count,"query": {"bool": {"should": [{"term":{"text": keyword}},{"term":{"type":"img"}}]}}})
   other_results(results, img_array, es, index)
  if settings[8] == 1: # 其他类型用bool搜索
   if settings[2] == 1: # 按日期排序 
    results = es.search(index=index,body={"size": count,"query": {"bool": {"should": [{"term":{"text": keyword}},{"term":{"type":"mp4"}}]}},"sort":{"date":{"order":"desc"}}})
   else:
    results = es.search(index=index,body={"size": 4,"query": {"bool": {"should": [{"term":{"text": keyword}},{"term":{"type":"mp4"}}]}}})
   other_results(results, mp4_array, es, index)
 suggestion = es.search(index = index, body={"suggest":{"my-suggestion":{"text":keyword,"term":{"field":"text"}}}})
 completion = es.search(index = "completion", body={"suggest":{"completion-suggestion": {"prefix": keyword, "completion": {"field": "suggest","size": 5}}}})
 latest_array = []
 if settings[9] == 1: #latest
  latest_array = crawl(keyword)
  #results = results = es.search(index=index,body={"size": count,"query": {"bool": {"should": [{"term":{"text": keyword}},{"term":{"type":"latest"}}]}},"sort":{"date":{"order":"desc"}}})
  #other_results(results, latest_array, es, index)
 if settings[10] != "":
  recommendation = es.search({ "suggest": { "MY_SUGGESTION": { "prefix": keyword, "completion":{"field":"input_completion", "contexts":{ "news_category":settings[10]}}}}})
 #print(json.dumps(results, sort_keys=False, indent=2, separators=(',', ': ')))
 #hitCount = results['hits']['total']['value']
 #print('Total ' + str(hitCount) + ' results found.')
 results_array = []
 results_array.append(cn_array)
 results_array.append(qa_array)
 results_array.append(news_array)
 results_array.append(txt_array)
 results_array.append(doc_array)
 results_array.append(pdf_array)
 results_array.append(img_array)
 results_array.append(mp4_array)

  #print(title + ': ' + str(lineNum) + ' (' + str(score) + '): ')
  #print(previousLine['_source']['text'] + text + nextLine['_source']['text'])
 suggestion_array = []
 if bool(suggestion['suggest']['my-suggestion']): #判断是否为空，为空则不需要
  for i in suggestion['suggest']['my-suggestion'][0]['options']:
   suggest = i['text']
   suggestion_array.append(suggest)
   
 completion_array = []
 if bool(completion['suggest']['completion-suggestion']): #判断是否为空，为空则不需要
  for i in completion['suggest']['completion-suggestion'][0]['options']:
   complete = i['text']
   completion_array.append(complete)
 
 recommendation_array = []
 if settings[10] != "":
  for i in recommendation['suggest']['MY_SUGGESTION'][0]['options']:
   comment = i['_source']['comment']
   url = i['_source']['url']
   category = i['_source']['input_completion']['contexts']['news_category']
   temp = []
   temp.append(comment)
   temp.append(url)
   temp.append(category)
   recommendation_array.append(temp)
 return results_array, suggestion_array, completion_array, recommendation_array, latest_array
 
if __name__ == '__main__':
 print("Search results for index:", sys.argv[1], ", keyword:", sys.argv[2], ", count:", sys.argv[3], "\n", booksearch_core(sys.argv[1], sys.argv[2], sys.argv[3]))
