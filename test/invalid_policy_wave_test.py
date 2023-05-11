from concurrent.futures import ThreadPoolExecutor
import random
import sys
import requests
import traceback
import time

POLICY_POOL = {
    "207": True,
    "112": True,
    "113": True,
    "0": True,
    "annotateall": True,
    "aHR0cHM6Ly9pbnRlcm5hbC1ybS10aXAudXN3Mi5hbWUuYXBpLmNvZy50cmFmZmljbWFuYWdlci5uZXQ6NDQzL3N2Yy93ZWIvc3Vic2NyaXB0aW9ucy9hOTIxNmYzNy1iOTBlLTRkYjItYjg0NC1iMTcxZTUzOTRmYzEvcmVzb3VyY2VHcm91cHMvYnVnYmFzaC1kaXNjb3VudC9wcm92aWRlcnMvTWljcm9zb2Z0LkNvZ25pdGl2ZVNlcnZpY2VzL2FjY291bnRzL2FvYWktZGlzY291bnQteWRvdS9yYWlQb2xpY2llcy8xMTI=": False,
    "aHR0cHM6Ly93d3cuYmluZy5jb20=": False,
    "https://www.bing.com": False,
}

def random_annotate(seq, endpoint: str, token: str):
    print(f'seq start: {seq}')
    policy_id = random.choice(list(POLICY_POOL))
    exists = POLICY_POOL[policy_id]

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Policy-Id': policy_id,
        'Text-Type': random.choice(['USER_REQUEST', 'MODEL_GENERATED'])
    }
    data = {
       "text": [
            "You are an idiot."
        ]
    }
    start = time.perf_counter()
    resp = requests.post(endpoint, headers=headers, json=data)
    end = time.perf_counter()
    print(f'seq {seq} cost: {end-start}')
    
    if exists:
        assert resp.status_code == 200, f'error: {resp.status_code}, {resp.text}'
    else:
        assert resp.status_code == 424 and 'Policy id not found:' in resp.text, f'error: {resp.status_code}, {resp.text}'


def main():
    endpoint = sys.argv[1]
    token = sys.argv[2]
    
    pool = ThreadPoolExecutor(max_workers=16)
    futures = []
    for i in range(100):
        future = pool.submit(random_annotate, i, endpoint, token)
        futures.append(future)
        
    error_count = 0
    error_sample = None
    for future in futures:
        try:
            future.result()
        except Exception as ex:
            error_count += 1
            error_sample = ex

    if error_count > 0:
        print(f'finished, error count: {error_count}')
        traceback.print_exception(error_sample)
    else: 
        print('finished, all good')                



if __name__ == '__main__':
    main()