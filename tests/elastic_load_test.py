import sys
import logging
from elasticsearch import exceptions
import pytest
from billsim.elastic_load import es, indexBill
from tests import constants_test
from billsim.constants import SAMPLE_MATCH_ALL_QUERY
from billsim.bill_similarity import getSimilarSections
from billsim.utils_es import getHitsHits, moreLikeThis

logging.basicConfig(filename='elastic_load_test.log',
                    filemode='w',
                    level='INFO')
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))


def es_service_available() -> bool:
    service_available = es.ping()
    if not service_available:
        logger.error(msg='Elasticsearch service not available')
    return service_available


@pytest.mark.skipif(not es_service_available(),
                    reason="Elasticsearch service not available")
class TestElasticLoad:

    def test_createIndex(self):
        from billsim.elastic_load import createIndex
        createIndex(index=constants_test.TEST_INDEX_SECTIONS, delete=True)
        assert (es.indices.exists(index=constants_test.TEST_INDEX_SECTIONS))
        createIndex(index=constants_test.TEST_INDEX_BILL_FULL, delete=True)
        assert (es.indices.exists(index=constants_test.TEST_INDEX_BILL_FULL))

    def test_indexBill(self):
        from billsim.elastic_load import indexBill
        billPath = constants_test.SAMPLE_BILL_PATH
        r = indexBill(billPath=billPath,
                      index_types={
                          'sections': constants_test.TEST_INDEX_SECTIONS,
                          'bill_full': constants_test.TEST_INDEX_BILL_FULL
                      })
        assert r is not None
        assert r.success


#def indexSampleBills():
#    from billsim.elastic_load import indexBill
#    billPath = constants_test.SAMPLE_BILL_PATH_117HR2001
#    r = indexBill(billPath=billPath,
#                  index_types={
#                      'sections': constants_test.TEST_INDEX_SECTIONS,
#                      'bill_full': constants_test.TEST_INDEX_BILL_FULL
#                  })


@pytest.mark.skipif(not es_service_available(),
                    reason="Elasticsearch service not available")
class TestBillSimilarity:

    @classmethod
    def setup_class(cls):
        logger.debug('elastic_load test setup_class')
        billPath = constants_test.SAMPLE_BILL_PATH_117HR2001
        r = indexBill(billPath=billPath,
                      index_types={
                          'sections': constants_test.TEST_INDEX_SECTIONS,
                      })

    @classmethod
    def teardown_class(cls):
        pass
        #logger.debug('elastic_load test teardown class')
        #for index in [
        #        constants_test.TEST_INDEX_SECTIONS,
        #        constants_test.TEST_INDEX_BILL_FULL
        #]:
        #    try:
        #        es.indices.delete(index=index)
        #    except exceptions.NotFoundError:
        #        logger.warn('No index to delete: {0}'.format(index))

    @pytest.mark.skip(
        reason="Es query coming up empty when the first test deletes the index")
    def test_matchAllQuery(self):
        from billsim.utils_es import runQuery
        matchall_query = SAMPLE_MATCH_ALL_QUERY
        matchall_query["size"] = 2
        r = runQuery(index=constants_test.TEST_INDEX_SECTIONS,
                     query=matchall_query)

        assert r is not None
        assert len(getHitsHits(r)) == 1

    @pytest.mark.skip(
        reason="Es query coming up empty when the first test deletes the index")
    def test_moreLikeThis(self):
        """
        Test moreLikeThis() function. Depends on runQuery() function. 
        """
        r = moreLikeThis(
            queryText=constants_test.SAMPLE_QUERY_TEXT,
            index=constants_test.TEST_INDEX_SECTIONS,
            min_score=constants_test.TEST_MIN_SCORE,
        )
        assert r is not None
        print(r)
        hits = r['hits']['hits']
        assert hits is not None
        assert len(hits) > 0

    @pytest.mark.skip(
        reason="Es query coming up empty when the first test deletes the index")
    def test_getSimilarSections(self):
        r = getSimilarSections(
            queryText=constants_test.SAMPLE_QUERY_TEXT,
            index=constants_test.TEST_INDEX_SECTIONS,
            min_score=constants_test.TEST_MIN_SCORE,
        )
        assert r is not None
        assert len(r) > 0