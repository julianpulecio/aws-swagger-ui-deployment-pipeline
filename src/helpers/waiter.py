from botocore.client import BaseClient
from datetime import datetime,timedelta

def wait(client:object, func:function, status:str):
   if not any(isinstance(client, cls) for cls in BaseClient.__subclasses__()):
        raise ValueError('client object must be a instace of botocore.client.BaseClient subclasses')

