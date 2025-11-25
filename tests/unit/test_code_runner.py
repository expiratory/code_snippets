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
