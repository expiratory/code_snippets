from enum import Enum


class SnippetEventEnum(Enum):
    CREATED = "snippet.created"
    UPDATED = "snippet.updated"
    DELETED = "snippet.deleted"
