from fastapi import (
    FastAPI,
    Depends,
    Request,
    BackgroundTasks
)
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import docker
import os
import logging
import sys
pth = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if pth not in sys.path:
    sys.path.insert(0, pth)
from rb_roads_api.config.db import pool
from rb_roads_api.config.utils import ComputeParams, RBEnviron, RBRoadsJob
import redis
import json
import uuid
from dataclasses import dataclass, asdict
from typing import (
    Any,
    Dict,
    List,
    Literal
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
defaultParams = ComputeParams().asdict()


def get_redis():
    # Here, we re-use our connection pool
    # not creating a new one
    return redis.Redis(connection_pool=pool)


app = FastAPI(debug=True, title="rb-roads API",
              version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)
static_files = StaticFiles(directory="./www/static")
templates = Jinja2Templates("./www/templates")


async def check_job_status(job: Dict | RBRoadsJob):
    # check for corresponding output, mark complete if done.
    if isinstance(job, dict):
        job = RBRoadsJob(**job)
    if job.status in ("failed", "complete"):
        return job
    if os.path.exists(job.poptable_output_file):
        job.status = "complete"
    return job


@app.get("/jobs")
async def list_jobs(db: Depends(get_redis)):
    jobs = await db.get("rb-roads-jobs")
    jobs_out = {}
    for job_id, job in jobs.items():
        job = check_job_status(job)
        if job.status == "failed":
            continue
        jobs_out[job_id] = job
    return jobs_out


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse('index.html', context=dict(request=request, defaultParams=defaultParams))


async def cache_job_info(container, job: RBRoadsJob, db: Depends(get_redis) = None):
    jobs = await db.get("rb-roads-jobs")
    jobs_dict = json.loads(jobs)
    jobs_dict[str(uuid.uuid4())] = {
        "job": job.asdict(),
        "container.attrs": container.attrs
    }
    await db.set('rb-roads-jobs', json.dumps(jobs_dict))
    yield


@app.post("/compute")
async def compute(params: ComputeParams, background_tasks: BackgroundTasks):
    os.environ["USER"] = "appuser"
    client = docker.from_env()
    command = params.command
    container = client.containers.list(filters={"name": "rb-roads"})[0]
    exit_code, output_stream = None, None
    try:
        exit_code, output_stream = container.exec_run(
            command, detach=True, stream=True)
    except Exception as e:
        logger.error(e)
        job = RBRoadsJob(**{
            "status": "failed",
            "message": "Compute job failed.",
            "params": params.formatted_dict,
            "command": params.command,
            "poptable_output_file": params.outfn,
            "exit_code": exit_code,
            "output_stream": output_stream
        })
    else:
        job = RBRoadsJob(**{
            "status": "started",
            "message": "Compute job started.",
            "params": params.formatted_dict,
            "command": params.command,
            "poptable_output_file": params.outfn,
            "exit_code": exit_code,
            "output_stream": output_stream
        })
    finally:
        background_tasks.add_task(cache_job_info, container, job)
    return job.asdict()
