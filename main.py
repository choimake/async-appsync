import asyncio
from aws_iam_auth import AWSIamAuth
from appsync_client import AppSyncClient

ACCESS_KEY_ID = "<aws_access_key_id>"
APPSYNC_ENDPOINT = "<app_sync_endpoint>"
SECRET_ACCESS_KEY = "<aws_secret_access_key>"

REGION = "ap-northeast-1"
SERVICE = "appsync"


auth = AWSIamAuth(
    access_key=ACCESS_KEY_ID,
    secret_key=SECRET_ACCESS_KEY,
    endpoint=APPSYNC_ENDPOINT,
    region=REGION,
    service=SERVICE,
)

client = AppSyncClient(endpoint=APPSYNC_ENDPOINT, auth=auth)


query = """
<query>
"""

loop = asyncio.get_event_loop()
response = loop.run_until_complete(client.execute_async(query=query))

print(response)
