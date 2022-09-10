import re
from models import AmozeshyarSegment
from elasticsearch_dsl import connections
from config import ELASTIC_HOSTS_CONFIG
file = open('shit.txt','r',encoding='utf8')
file = file.read()
sdsa = file.split('\n')
connections.create_connection(hosts=ELASTIC_HOSTS_CONFIG, timeout=60)
for i in sdsa: 
    doc = AmozeshyarSegment(text=i)
    elastic_id = doc.save(refresh=True)
    print(str(elastic_id))
