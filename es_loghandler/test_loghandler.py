import datetime
import elasticsearch
import pytz

from .handlers import ElasticHandler
from unittest.mock import patch
from unittest import TestCase


class Record:
    def __init__(self, data):
        for key, value in data.items():
            setattr(self, key, value)


class MockTraceback:
    def format_exception(self, etype, value, tb, limit=None, chain=True):
        return etype, value, tb, limit, chain


class TestLoghandler(TestCase):
    hosts = ['localhost']

    now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    handler = ElasticHandler(hosts=hosts)
    elastic = elasticsearch.Elasticsearch(hosts)

    def get_index(self):
        index = 'logstash-%s' % self.now.strftime('%Y.%m.%d')
        return index

    def get_log(self):
        index = self.get_index()
        response = self.elastic.search(index=index, doc_type="log", body={"query": {"match_all": {}}})

        assert len(response['hits']['hits']) == 1

        log = response['hits']['hits'][0]
        return log

    def setUp(self):
        index = self.get_index()

        if index in self.elastic.indices.get('*'):
            response = self.elastic.search(index=index, doc_type="log", body={"query": {"match_all": {}}})
            logs = response['hits']['hits']
            for log in logs:
                self.elastic.delete(index=index, doc_type="log", id=log['_id'])

    def test_without_exc_info(self):
        data = {
            'msg': '2356',
            'test_field': '2356',
            'status': 'ok',
            'field_1': 'field 1',
            'field_2': 'field 2',
            'field_3': 'field 3',
            'field_4': 'field 4',
            'field_5': 'field 5',
        }
        record = Record(data)
        self.handler.emit(record)

        log = self.get_log()

        results = dict(data)
        results['message'] = results.pop('msg')

        assert 'exc_info' not in log['_source'] or not log['_source']['exc_info']

        for key, value in log['_source'].items():
            val = results.get(key)
            if val:
                assert value == val

    @patch('es_loghandler.handlers.traceback.format_exception')
    def test_with_exc_info(self, mock_format_exception):
        data = {
            'exc_info': ['2', '4', 'foo'],
            'msg': 'test',
            'field_2': 'field 2',
            'field_3': 'field 3',
            'field_4': 'field 4',
            'field_5': 'field 5',
        }
        exc_info = ''.join(data['exc_info'])
        mock_format_exception.return_value = exc_info

        record = Record(data)
        self.handler.emit(record)
        log = self.get_log()

        results = dict(data)
        results['message'] = results.pop('msg')
        results['exc_info'] = exc_info

        assert 'exc_info' in log['_source']
        assert log['_source']['exc_info'] == exc_info

        for key, value in log['_source'].items():
            val = results.get(key)
            if val:
                assert value == val