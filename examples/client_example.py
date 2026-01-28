#!/usr/bin/env python3
"""
Example client for the Audio Annotation Platform API.

This script demonstrates how to:
1. Request a task from the middleware
2. Download and process audio
3. Submit transcription results
4. Handle errors and skip functionality
"""

import requests
import os
from typing import Optional, Dict, Any

# Configuration
API_KEY = os.getenv("API_KEY", "your_api_key_here")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8010")
AGENT_ID = int(os.getenv("AGENT_ID", "123"))

class TranscriptionClient:
    """Client for interacting with the Audio Annotation Platform API."""

    def __init__(self, api_key: str, base_url: str, agent_id: int):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.agent_id = agent_id
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }

    def check_health(self) -> Dict[str, Any]:
        """Check API health status."""
        response = requests.get(f"{self.base_url}/api/health", headers=self.headers)
        response.raise_for_status()
        return response.json()

    def request_task(self) -> Optional[Dict[str, Any]]:
        """
        Request next available task.

        Returns:
            Task dictionary with task_id, audio_url, duration, file_name
            or None if no tasks available
        """
        response = requests.post(
            f"{self.base_url}/api/tasks/request",
            json={"agent_id": self.agent_id},
            headers=self.headers
        )
        response.raise_for_status()
        task = response.json()

        if task.get("task_id") is None:
            print("No tasks available")
            return None

        return task

    def download_audio(self, audio_url: str, output_path: str) -> None:
        """
        Download audio file from the provided URL.

        Args:
            audio_url: URL to download audio from
            output_path: Path to save the audio file
        """
        response = requests.get(audio_url, headers=self.headers, stream=True)
        response.raise_for_status()

        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

    def submit_transcription(self, task_id: int, transcription: str) -> Dict[str, Any]:
        """
        Submit transcription for a task.

        Args:
            task_id: The task ID
            transcription: The transcribed text

        Returns:
            Response dictionary with status and annotation_id
        """
        response = requests.post(
            f"{self.base_url}/api/tasks/{task_id}/submit",
            json={
                "agent_id": self.agent_id,
                "transcription": transcription
            },
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def skip_task(self, task_id: int, reason: str) -> Dict[str, Any]:
        """
        Skip a task with a reason.

        Args:
            task_id: The task ID to skip
            reason: Reason for skipping

        Returns:
            Response dictionary with status
        """
        response = requests.post(
            f"{self.base_url}/api/tasks/{task_id}/skip",
            json={
                "agent_id": self.agent_id,
                "reason": reason
            },
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def get_available_count(self) -> Dict[str, int]:
        """
        Get count of available tasks.

        Returns:
            Dictionary with available, total_unlabeled, total_locked counts
        """
        response = requests.get(
            f"{self.base_url}/api/tasks/available/count",
            params={"agent_id": self.agent_id},
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def get_agent_stats(self) -> Dict[str, Any]:
        """
        Get statistics for this agent.

        Returns:
            Dictionary with agent statistics
        """
        response = requests.get(
            f"{self.base_url}/api/agents/{self.agent_id}/stats",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()


def mock_transcribe_audio(audio_path: str) -> str:
    """
    Mock transcription function.
    Replace this with your actual ASR implementation.

    Args:
        audio_path: Path to audio file

    Returns:
        Transcribed text
    """
    # In a real implementation, you would:
    # 1. Load the audio file
    # 2. Run it through your ASR model
    # 3. Return the transcription
    #
    # For this example, we just return a placeholder
    return "This is a mock transcription. Replace with actual ASR."


def main():
    """Main processing loop."""
    client = TranscriptionClient(API_KEY, BASE_URL, AGENT_ID)

    # Check health
    try:
        health = client.check_health()
        print(f"✓ API health check: {health}")
    except Exception as e:
        print(f"✗ API health check failed: {e}")
        return

    # Get available task count
    try:
        counts = client.get_available_count()
        print(f"Available tasks: {counts['available']}")
    except Exception as e:
        print(f"Warning: Could not get task count: {e}")

    # Request a task
    try:
        task = client.request_task()
        if not task:
            print("No tasks available. Exiting.")
            return

        print(f"\n✓ Received task {task['task_id']}")
        print(f"  Duration: {task.get('duration', 'unknown')}s")
        print(f"  File: {task['file_name']}")

        # Download audio
        audio_path = f"/tmp/task_{task['task_id']}.wav"
        print(f"\n⬇ Downloading audio to {audio_path}...")
        client.download_audio(task['audio_url'], audio_path)
        print("✓ Audio downloaded")

        # Transcribe (replace with your actual ASR)
        print("\n🎙 Transcribing audio...")
        transcription = mock_transcribe_audio(audio_path)
        print(f"✓ Transcription: {transcription[:50]}...")

        # Check if we should skip (e.g., poor quality, silent audio)
        should_skip = False  # Replace with your quality check logic
        if should_skip:
            print("\n⏭ Skipping task due to quality issues...")
            result = client.skip_task(task['task_id'], "Poor audio quality")
            print(f"✓ {result['message']}")
        else:
            # Submit transcription
            print("\n⬆ Submitting transcription...")
            result = client.submit_transcription(task['task_id'], transcription)
            print(f"✓ Submitted successfully (annotation_id: {result['annotation_id']})")

        # Clean up
        if os.path.exists(audio_path):
            os.remove(audio_path)

        # Show agent stats
        stats = client.get_agent_stats()
        print(f"\n📊 Agent Statistics:")
        print(f"  Completed: {stats['total_tasks_completed']}")
        print(f"  Skipped: {stats['total_tasks_skipped']}")
        print(f"  Total duration: {stats['total_duration_seconds']:.1f}s")
        print(f"  Total earnings: ${stats['total_earnings']:.2f}")

    except requests.HTTPError as e:
        print(f"\n✗ HTTP error: {e}")
        if e.response is not None:
            print(f"  Response: {e.response.text}")
    except Exception as e:
        print(f"\n✗ Error: {e}")


if __name__ == "__main__":
    main()
