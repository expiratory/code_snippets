from enum import Enum


class RunLanguage(Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    JAVA = "java"
    GO = "go"

    @classmethod
    def get_languages(cls):
        return [lang.value for lang in cls]
