#!/bin/bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
uvicorn src.main:app --host 0.0.0.0 --port 3001 --reload 