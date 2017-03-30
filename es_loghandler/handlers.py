# coding: utf-8
import datetime
import logging
import elasticsearch
import pytz


class ElasticHandler(logging.Handler):
    def __init__(self, hosts, *args, **kwargs):
        super(ElasticHandler, self).__init__(*args, **kwargs)
        self.hosts = hosts

    def emit(self, record):
        now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        elastic = elasticsearch.Elasticsearch(self.hosts)
        log_data = record.__dict__.copy()
        log_data['message'] = log_data.pop('msg', '')
        log_data['@timestamp'] = now.isoformat()
        index = 'logstash-%s' % now.strftime('%Y.%m.%d')
        elastic.index(index=index, doc_type='log', body=log_data)
