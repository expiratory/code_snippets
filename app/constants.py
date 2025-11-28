from app.enums.language import RunLanguage

AVAILABLE_IMAGES = {
    RunLanguage.PYTHON.value: [
        {"version": "3.9", "image": "python:3.9-slim"},
        {"version": "3.10", "image": "python:3.10-slim"},
        {"version": "3.11", "image": "python:3.11-slim"},
    ],
    RunLanguage.JAVASCRIPT.value: [
        {"version": "16", "image": "node:16-alpine"},
        {"version": "18", "image": "node:18-alpine"},
        {"version": "20", "image": "node:20-alpine"},
    ],
    RunLanguage.JAVA.value: [
        {"version": "17", "image": "eclipse-temurin:17-jdk-alpine"},
        {"version": "21", "image": "eclipse-temurin:21-jdk-alpine"},
    ],
    RunLanguage.GO.value: [
        {"version": "1.19", "image": "golang:1.19-alpine"},
        {"version": "1.20", "image": "golang:1.20-alpine"},
        {"version": "1.21", "image": "golang:1.21-alpine"},
    ],
}
