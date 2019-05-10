#!/usr/bin/env python

SIMILARITY_PERCENTAGE = .75

TABLE_NAME = "`ninth-tensor-233119.blockchain.website_data`"
GET_ALL_DATA_QUERY = "" \
                     "SELECT * " \
                     "FROM {}"

GET_PUBLICATION_NUMBER_EMBEDDING = "" \
                                   "SELECT embedding_v1 " \
                                   "FROM {} " \
                                   "WHERE publication_number = '{}'"

GET_COUNT_TOP_TERMS_BY_TERMS = "" \
                               "SELECT terms , COUNT(terms) as count " \
                               "FROM {}, UNNEST(top_terms) as terms " \
                               "GROUP BY terms " \
                               "ORDER BY COUNT(terms) desc "

GET_PUBLICATION_WITH_TERM = "" \
                            "SELECT * " \
                            "FROM {} " \
                            "WHERE 1 = (SELECT 1 " \
                            "FROM UNNEST(top_terms) " \
                            "as t WHERE '{}' = t " \
                            ")"