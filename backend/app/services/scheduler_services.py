from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from typing import Callable
import logging

logger = logging.getLogger(__name__)


class SchedulerService:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.jobs = {}

    def start(self):
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler started")

    def shutdown(self):
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler shutdown")

    def add_cron_job(self, func: Callable, job_id: str, **cron_args):
        """Add a cron-style job"""
        trigger = CronTrigger(**cron_args)
        job = self.scheduler.add_job(func=func, trigger=trigger, id=job_id)
        self.jobs[job_id] = {"type": "cron", "job": job}
        logger.info(f"Added cron job: {job_id}")
        return job

    def add_interval_job(self, func: Callable, job_id: str, **interval_args):
        """Add an interval-based job"""
        trigger = IntervalTrigger(**interval_args)
        job = self.scheduler.add_job(func=func, trigger=trigger, id=job_id)
        self.jobs[job_id] = {"type": "interval", "job": job}
        logger.info(f"Added interval job: {job_id}")
        return job


# Global scheduler instance
scheduler_service = SchedulerService()
