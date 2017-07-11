from django.test import TestCase

# Create your tests here.



import json
import pickle

import requests


result = requests.get('http://wthrcdn.etouch.cn/weather_mini?city=呼和浩特')

result.encoding = 'utf-8'

#print(result.text)

dic = json.loads(result.text)

print(dic)