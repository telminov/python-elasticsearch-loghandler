# coding: utf-8
import elasticsearch

import datetime
from logging import Handler


class ElasticHandler(Handler):
    def __init__(self, hosts, *args, **kwargs):
        super(ElasticHandler, self).__init__(*args, **kwargs)
        self.hosts = hosts

    def emit(self, record):
        now = datetime.datetime.now(datetime.timezone.utc)
        elastic = elasticsearch.Elasticsearch(self.hosts)
        log_data = record.__dict__.copy()
        log_data['pathname'] = record.pathname
        log_data['@timestamp'] = now.isoformat()
        index = 'logstash-%s' % now.strftime('%Y.%m.%d')
        elastic.index(index=index, doc_type='log', body=log_data)
