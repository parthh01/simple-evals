import requests
from ..types import MessageList, SamplerBase
import os
import time
from typing import Any

API_BASE_URL ="https://api.critique-labs.ai" 

class CritiqueSampler(SamplerBase):

    def __init__(self,api_key=os.getenv('CRITIQUE_API_KEY')):
        self.api_key = api_key

    def _pack_message(self, role: str, content: Any):
        return {"role": str(role), "content": content}

    def __call__(self, message_list: MessageList) -> str:
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in message_list])
        url = f'{API_BASE_URL}/v1/search'
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': self.api_key
        }
        data = { 'prompt': prompt}
        trial = 0
        output = ""
        while True:
            try:
                response = requests.post(url, headers=headers, json=data)
                if response.status_code == 429:
                    exception_backoff = 1
                    print(f"Rate limit exception so wait and retry {trial} after {exception_backoff} sec")
                    time.sleep(exception_backoff)
                else:
                    output = response.json()
                    if 'error' in output:
                        print("Critique Query Error", output['error'])
                        return "unable to answer"
                    return output['response']
            except Exception as e:
                print("Critique Query Error", e)
                print(response.text)
                return "unable to answer"
            trial += 1
            time.sleep(1)

        return "unable to answer"
