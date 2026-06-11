import os
from dotenv import load_dotenv

load_dotenv()

GTFS_RT_URL = os.getenv("GTFS_RT_URL")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
SNS_TOPIC_ARN = os.getenv("SNS_TOPIC_ARN")

DELAY_THRESHOLD_SECONDS = int(os.getenv("DELAY_THRESHOLD_SECONDS", 120))
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", 30))