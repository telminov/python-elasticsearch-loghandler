# coding: utf-8
import datetime
import logging
import elasticsearch
import pytz
import traceback


class ElasticHandler(logging.Handler):
    def __init__(self, hosts, *args, **kwargs):
        super(ElasticHandler, self).__init__(*args, **kwargs)
        self.hosts = hosts

    def emit(self, record):
        now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)

        log_data = record.__dict__.copy()
        log_data['message'] = log_data.pop('msg', '')
        log_data['@timestamp'] = now.isoformat()
        if log_data.get('exc_info'):
            log_data['exc_info'] = ''.join(traceback.format_exception(*record.exc_info))

        index = 'logstash-%s' % now.strftime('%Y.%m.%d')

        elastic = elasticsearch.Elasticsearch(self.hosts)
        elastic.index(index=index, doc_type='log', body=log_data)
