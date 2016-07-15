# -*- coding: utf-8 -*-
import asyncio
import json
import elasticsearch
import elasticsearch_dsl

from elasticsearch_dsl.aggs import A
from codetoname import github
from codetoname.features import from_repo


class Crawler:
    def __init__(self, index='codetoname', page_num=0, page_size=10,
                 language='python', account=None, password=None):
        assert account and password

        self._loop = asyncio.get_event_loop()
        self._github_client = github.Github(account, password)
        self._es = elasticsearch.Elasticsearch()
        self._es_index = index
        self._page_num = page_num
        self._page_size = page_size
        self._latest_repo_index = False

        self.create_index()
        self._language = language.strip()
        self._latest_pushed = None

    def close(self):
        self._github_client.close()

    def delete_index(self):
        if self._es.indices.exists(index=self._es_index):
            self._es.indices.delete(index=self._es_index)

    def create_index(self):
        if not self._es.indices.exists(index=self._es_index):
            self._es.indices.create(index=self._es_index)

    def fetch_github_repos(self, page_size=None):
        # update page size
        if page_size:
            self._page_size = page_size

        # calculate new start-end indices
        if self._latest_repo_index:
            start_index = self._latest_repo_index
        else:
            start_index = self._page_size * self._page_num
        end_index = start_index + self._page_size

        # update latest index, and page num
        self._latest_repo_index = end_index
        self._page_num += 1

        # fetch
        repos = self._github_response[start_index:end_index]
        return [{'url': r.clone_url, 'branch': r.default_branch, 'github_id': r.id, 'fork': r.fork} for r in repos]

    def next(self):
        response = self._loop.run_until_complete(
            self._github_client.search_repositories(
                language=self._language,
                pushed=self._latest_pushed,
                sort='updated',
                order='asc'
            )
        )

        repositories = [
            {
                'url': item['clone_url'],
                'branch': item['default_branch'],
                'github_id': item['id'],
                'fork': item['fork']
            } for item in response['items']
        ]

        for repository in repositories:
            if self.exists_repos_in_database(repository['github_id']):
                continue

            try:
                features = from_repo(repository, language=self._language)
                for f in features:
                    self._es.index(
                        index=self._es_index,
                        doc_type=self._language,
                        body={'repo': repository, 'feature': json.dumps(f)}
                    )
                if not features:
                    self._es.index(
                        index=self._es_index,
                        doc_type=self._language,
                        body={'repo': repository})
                self._es.indices.refresh(index=self._es_index)
            except Exception as e:
                print(repository)
                print(f) if f else None
                print(e)

    def exists_repos_in_database(self, github_id):
        if 0 != elasticsearch_dsl \
                .Search(using=self._es, index=self._es_index, doc_type=self._language) \
                .query('term', repo__github_id=github_id) \
                .count():
            return True
        return False

    def num_features(self):
        return self._es.count(index=self._es_index)['count']

    def num_repos(self):
        if self._es.indices.exists(index=self._es_index):
            s = elasticsearch_dsl.Search(using=self._es, index=self._es_index, doc_type=self._language)
            s.aggs.bucket('num_repos', A('cardinality', field='repo.github_id'))
            response = s.execute()
            return response.aggregations.num_repos.value
        return 0

    def get_features(self):
        if self._es.indices.exists(index=self._es_index):
            s = elasticsearch_dsl.Search(using=self._es, index=self._es_index, doc_type=self._language)
            response = s.execute()
            if 0 != len(response.hits):
                return response.hits
        return False
