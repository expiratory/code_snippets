import asyncio

import docker

from app.config import settings
from app.enums.language import RunLanguage


class CodeRunnerService:
    # Class-level semaphore to limit concurrent executions across all instances
    _semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_EXECUTIONS)

    def __init__(self):
        self.client = docker.from_env()

    async def run_code(self, code: str, language: str, timeout: int = 10):
        # Use semaphore to limit concurrent executions
        async with self._semaphore:
            return await self._execute_code(code, language, timeout)

    async def _execute_code(self, code: str, language: str, timeout: int = 10):
        container = None

        try:
            # Pull image if not present
            try:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    None, lambda: self.client.images.pull(self._get_image(language))
                )
            except Exception:
                pass  # Image might already exist

            # Run code in container - pass code via command
            container = self.client.containers.run(
                image=self._get_image(language),
                command=self._get_command(code, language),
                mem_limit="100m",
                cpu_period=100000,
                cpu_quota=10000,  # 10%
                network_mode="none",
                working_dir="/tmp",
                read_only=True,  # Read-only root filesystem
                tmpfs={"/tmp": "size=10m,mode=1777"},  # Writable /tmp with size limit
                cap_drop=["ALL"],  # Drop all capabilities
                security_opt=["no-new-privileges"],  # Prevent privilege escalation
                pids_limit=50,  # Limit number of processes
                stdout=True,
                stderr=True,
                detach=True,
            )

            # Wait for container to finish with timeout
            try:
                result = await asyncio.wait_for(
                    self._wait_for_container(container), timeout=timeout
                )
                return result
            except asyncio.TimeoutError:
                try:
                    container.kill()
                except Exception:
                    pass
                return {"stdout": "", "stderr": "Timeout exceeded", "exit_code": -1}

        except docker.errors.ImageNotFound:
            return {
                "stdout": "",
                "stderr": f"Image for {language} not found",
                "exit_code": -1,
            }
        except Exception as e:
            return {"stdout": "", "stderr": f"System error: {str(e)}", "exit_code": -1}
        finally:
            # Remove container if it's still running
            if container:
                try:
                    container.remove(force=True)
                except Exception:
                    pass

    def _get_image(self, language: str):
        images = {
            RunLanguage.PYTHON.value: "python:3.9-slim",
            RunLanguage.JAVASCRIPT.value: "node:16-alpine",
            RunLanguage.JAVA.value: "eclipse-temurin:17-jdk-alpine",
            RunLanguage.GO.value: "golang:1.19-alpine",
        }
        return images.get(language, "python:3.9-slim")

    def _get_command(self, code: str, language: str):
        # Escape code for shell - use base64 to avoid escaping issues
        import base64

        code_b64 = base64.b64encode(code.encode()).decode()

        commands = {
            RunLanguage.PYTHON.value: [
                "sh",
                "-c",
                f"echo '{code_b64}' | base64 -d > /tmp/code.py && python /tmp/code.py",
            ],
            RunLanguage.JAVASCRIPT.value: [
                "sh",
                "-c",
                f"echo '{code_b64}' | base64 -d > /tmp/code.js && node /tmp/code.js",
            ],
            RunLanguage.JAVA.value: [
                "sh",
                "-c",
                f"echo '{code_b64}' | base64 -d > /tmp/Main.java && javac /tmp/Main.java && java -cp /tmp Main",
            ],
            RunLanguage.GO.value: [
                "sh",
                "-c",
                f"echo '{code_b64}' | base64 -d > /tmp/code.go && go run /tmp/code.go",
            ],
        }

        return commands.get(language, ["sh", "-c", f"echo '{code_b64}' | base64 -d"])

    async def _wait_for_container(self, container):
        # Use run_in_executor to not block event loop
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, container.wait)

        # Splitting stdout and stderr in docker SDK is not always trivial through logs(),
        # if demux=True is not supported, we get a merged output

        logs = await loop.run_in_executor(
            None,
            lambda: container.logs(stdout=True, stderr=True, stream=False),
        )

        stdout = logs.decode("utf-8") if logs else ""
        stderr = ""  # We can't split without demux

        return {"stdout": stdout, "stderr": stderr, "exit_code": result["StatusCode"]}
