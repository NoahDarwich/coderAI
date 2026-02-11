#!/usr/bin/env python
"""
Entry point for running the ARQ worker.

Usage:
    python run_worker.py
    # or
    arq src.workers.settings.WorkerSettings
"""
import asyncio
from arq import run_worker
from src.workers.settings import WorkerSettings

if __name__ == "__main__":
    run_worker(WorkerSettings)
