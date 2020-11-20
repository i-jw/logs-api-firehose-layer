import json
import os
import sys
from pathlib import Path
lib_folder = Path(__file__).parent / "lib"
sys.path.insert(0,str(lib_folder))
import boto3

class Producer():
    def __init__(self,delivery_stream):
        self.firehose_client = boto3.client('firehose')
        self.delivery_stream = delivery_stream

    def put_records(self,data):
        if isinstance(data, list):
            data_array = []
            for d in data:
                tmp = json.dumps(d, indent=2).encode('utf-8')
                data_array.append({'Data':tmp})
            response = self.firehose_client.put_record_batch(
                    DeliveryStreamName=self.delivery_stream,
                    Records=data_array
                )
        else:
            response = self.firehose_client.put_record(
                DeliveryStreamName=self.delivery_stream,
                Record={
                    'Data': data
                }
            )
