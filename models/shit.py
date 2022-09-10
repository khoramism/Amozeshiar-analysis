from elasticsearch_dsl import Document, Date, Text, Keyword, Long, Object, InnerDoc, Float
from fnmatch import fnmatch
from datetime import datetime
import time

ALIAS = 'amooozeshyar'
PATTERN = ALIAS + '-*'

PERSIAN_ANALYZER = 'persian_grams_index_analyzer'
PERSIAN_SEARCH_ANALYZER = 'persian_grams_search_analyzer'


class AmozeshyarSegment(Document):
    created_at: Date()
    created_timestamp: Long()

    text  = Text(fields={'keyword': Keyword()}, analyzer=PERSIAN_ANALYZER,
                         search_analyzer=PERSIAN_SEARCH_ANALYZER)

    @classmethod
    def _matches(cls, hit):
        # override _matches to match indices in a pattern instead of just ALIAS
        # hit is the raw dict as returned by elasticsearch
        return fnmatch(hit['_index'], PATTERN)

    class Index:
        # we will use an alias instead of the index, script_id=elastic_id
        name = ALIAS
        # set settings and possibly other attributes of the index like analyzers
        settings = {
            'number_of_shards': 7,
            'number_of_replicas': 1,

            # Persian analyzer for fixing persian stop words indexing / searching problems
            # TODO: Update analyzer to match DSL paradigms
            "analysis": {
                "char_filter": {
                    "zero_width_spaces": {
                        "type": "mapping",
                        "mappings": ["\\u200C=> "]
                    }
                },
                "analyzer": {
                    PERSIAN_ANALYZER: {
                        "filter": [
                            "lowercase",
                            "arabic_normalization",
                            "persian_normalization",
                            "persian_grams"
                        ],
                        "char_filter": ["zero_width_spaces"],
                        "tokenizer": "standard"
                    },
                    PERSIAN_SEARCH_ANALYZER: {
                        "filter": [
                            "lowercase",
                            "arabic_normalization",
                            "persian_normalization",
                            "persian_grams_query"
                        ],
                        "char_filter": ["zero_width_spaces"],
                        "tokenizer": "standard"
                    }
                },
                "filter": {
                    "persian_grams": {
                        "type": "common_grams",
                        "stopwords": "_persian_",
                        "common_words": "_persian_"
                    },
                    "persian_grams_query": {
                        "type": "common_grams",
                        "query_mode": "true",
                        "stopwords": "_persian_",
                        "common_words": "_persian_"
                    }
                }
            }
        }

    def save(self, **kwargs):
        self.created_at = datetime.now()
        self.created_timestamp = int(time.time() * 1000)
        return super().save(**kwargs)
