from unittest.mock import MagicMock, patch

import docker
import pytest

from app.services.code_runner import CodeRunnerService


@pytest.fixture
def code_runner_service():
    with patch("docker.from_env") as mock_docker:
        service = CodeRunnerService()
        service.client = mock_docker.return_value
        yield service


@pytest.mark.asyncio
async def test_run_code_success(code_runner_service):
    mock_container = MagicMock()
    mock_container.wait.return_value = {"StatusCode": 0}
    # Mock logs to return bytes
    mock_container.logs.return_value = b"Hello World\n"

    code_runner_service.client.containers.run.return_value = mock_container

    result = await code_runner_service.run_code('print("Hello World")', "python")

    assert result["stdout"] == "Hello World\n"
    assert result["stderr"] == ""
    assert result["exit_code"] == 0
    code_runner_service.client.containers.run.assert_called_once()

    # Verify tmpfs config
    args, kwargs = code_runner_service.client.containers.run.call_args
    assert "exec" in kwargs["tmpfs"]["/tmp"]
    assert "exec" in kwargs["tmpfs"]["/root/.cache"]
    assert kwargs["read_only"] is True
    assert kwargs["pids_limit"] == 200
    assert kwargs["mem_limit"] == "200m"


@pytest.mark.asyncio
async def test_run_code_timeout(code_runner_service):
    mock_container = MagicMock()

    # Simulate timeout by making wait sleep longer than timeout
    async def delayed_wait(*args, **kwargs):
        import asyncio

        await asyncio.sleep(0.2)
        return {"StatusCode": 0}

    mock_container.wait.side_effect = lambda: __import__("time").sleep(0.2)
    code_runner_service.client.containers.run.return_value = mock_container

    result = await code_runner_service.run_code(
        "while True: pass", "python", timeout=0.1
    )

    assert result["exit_code"] == -1
    assert "Timeout exceeded" in result["stderr"]
    mock_container.kill.assert_called_once()


@pytest.mark.asyncio
async def test_run_code_docker_error(code_runner_service):
    code_runner_service.client.containers.run.side_effect = docker.errors.ImageNotFound(
        "Image not found"
    )

    result = await code_runner_service.run_code('print("Hello")', "python")

    assert result["exit_code"] == -1
    assert "Image for python not found" in result["stderr"]


def test_get_available_versions(code_runner_service):
    versions = code_runner_service.get_available_versions()
    assert "python" in versions
    assert "javascript" in versions
    assert "3.9" in versions["python"]
    assert "16" in versions["javascript"]


@pytest.mark.asyncio
async def test_run_code_with_version(code_runner_service):
    mock_container = MagicMock()
    mock_container.wait.return_value = {"StatusCode": 0}
    mock_container.logs.return_value = b"Hello World\n"

    code_runner_service.client.containers.run.return_value = mock_container

    await code_runner_service.run_code('print("Hello")', "python", version="3.11")

    # Verify that the correct image was used
    args, kwargs = code_runner_service.client.containers.run.call_args
    assert kwargs["image"] == "python:3.11-slim"


@pytest.mark.asyncio
async def test_run_code_with_invalid_version(code_runner_service):
    # Should fall back to default version if version not found in list
    mock_container = MagicMock()
    mock_container.wait.return_value = {"StatusCode": 0}
    mock_container.logs.return_value = b"Hello World\n"
    code_runner_service.client.containers.run.return_value = mock_container

    await code_runner_service.run_code('print("Hello")', "python", version="99.99")

    args, kwargs = code_runner_service.client.containers.run.call_args
    # Should use default python image
    assert kwargs["image"] == "python:3.9-slim"
