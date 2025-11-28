#!/usr/bin/env python3
"""
Initialization script for code-runner-worker.
Pre-pulls Docker images needed for code execution.
"""

import logging
import sys

import docker

from app.constants import AVAILABLE_IMAGES

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Images to pre-pull
IMAGES = [
    version["image"] for versions in AVAILABLE_IMAGES.values() for version in versions
]


def pull_images():
    """Pull all required Docker images."""
    try:
        client = docker.from_env()
        logger.info("Starting to pre-pull Docker images...")

        for image in IMAGES:
            try:
                try:
                    client.images.get(image)
                    logger.info(f"✓ Image {image} already exists locally")
                    continue
                except docker.errors.ImageNotFound:
                    logger.info(f"Image {image} not found locally, pulling...")

                logger.info(f"Pulling {image}...")
                client.images.pull(image)
                logger.info(f"✓ Successfully pulled {image}")
            except Exception as e:
                logger.warning(f"✗ Failed to pull {image}: {e}")
                # Continue with other images even if one fails

        logger.info("Finished pre-pulling Docker images")
        return True
    except Exception as e:
        logger.error(f"Error connecting to Docker: {e}")
        return False


if __name__ == "__main__":
    success = pull_images()
    sys.exit(0 if success else 1)
