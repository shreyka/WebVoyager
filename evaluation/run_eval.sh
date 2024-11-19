#!/bin/bash
# Load environment variables from .env file
source .env

nohup python -u auto_eval.py \
    --api_key ${OPENAI_API_KEY} \
    --process_dir ../results/comparisons \
    --max_attached_imgs 15 > evaluation.log &