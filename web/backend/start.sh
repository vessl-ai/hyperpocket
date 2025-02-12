#!/bin/bash
export USE_UVICORN=1
uvicorn src.main:app --host 0.0.0.0 --port 3001 --reload 