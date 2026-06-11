import boto3
import logging
from app.config import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_REGION,
    SNS_TOPIC_ARN,
)

logger = logging.getLogger(__name__)

sns_client = boto3.client(
    "sns",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)

def send_delay_alert(route_id: str, trip_id: str, delay_seconds: int) -> bool:
    """
    Publishes a delay alert to the SNS topic.
    SNS then fans out to all subscribed users (email/SMS).
    Returns True if successful, False if it fails.
    """
    delay_minutes = delay_seconds // 60
    message = (
        f"🚌 Transit Delay Alert\n"
        f"Route: {route_id}\n"
        f"Trip: {trip_id}\n"
        f"Delay: {delay_minutes} minutes ({delay_seconds} seconds)\n"
        f"Please check for alternate routes."
    )

    subject = f"Transit Alert: Route {route_id} delayed {delay_minutes} min"

    try:
        response = sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=message,
            Subject=subject,
        )
        message_id = response["MessageId"]
        logger.info(f"SNS alert sent for route {route_id}, MessageId={message_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to send SNS alert for route {route_id}: {e}")
        return False