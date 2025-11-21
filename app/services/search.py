from elasticsearch import AsyncElasticsearch
from app.config import settings

ES_URL = settings.ES_URL


class SearchService:
    def __init__(self):
        self.client = AsyncElasticsearch(ES_URL)
        self.index_name = "snippets"

    async def create_index(self):
        if not await self.client.indices.exists(index=self.index_name):
            await self.client.indices.create(
                index=self.index_name,
                body={
                    "mappings": {
                        "properties": {
                            "title": {"type": "text"},
                            "code": {"type": "text"},
                            "language": {"type": "keyword"},
                            "id": {"type": "integer"},
                        }
                    }
                },
            )

    async def index_snippet(
        self, snippet_id: int, title: str, code: str, language: str
    ):
        await self.client.index(
            index=self.index_name,
            id=str(snippet_id),
            document={
                "id": snippet_id,
                "title": title,
                "code": code,
                "language": language,
            },
        )

    async def delete_snippet(self, snippet_id: int):
        await self.client.delete(
            index=self.index_name, id=str(snippet_id), ignore=[404]
        )

    async def search_snippets(self, query: str) -> list[int]:
        response = await self.client.search(
            index=self.index_name,
            body={
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["title", "code"],
                        "fuzziness": "AUTO",
                    }
                }
            },
        )
        return [int(hit["_id"]) for hit in response["hits"]["hits"]]

    async def close(self):
        await self.client.close()
