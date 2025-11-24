from app.enums.snippet import SnippetEventEnum


def test_snippet_event_enum():
    assert SnippetEventEnum.CREATED.value == "snippet.created"
    assert SnippetEventEnum.UPDATED.value == "snippet.updated"
    assert SnippetEventEnum.DELETED.value == "snippet.deleted"
