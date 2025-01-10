
import requests
import os


class LLAMAParseService:

    def __init__(self):
        self.llama_parse_key = os.getenv('LLAMA_CLOUD_API_KEY')
        return


    def parse_pdf(self, file_path):
        llamaparse_url = 'https://api.cloud.llamaindex.ai/api/parsing/upload'
        headers = {
            'accept': 'application/json',
            'Authorization': f'Bearer {self.llama_parse_key}'
        }
        files = {
            'file': (file_path, open(file_path, 'rb'), 'application/pdf')
        }
        response = requests.post(llamaparse_url, headers=headers, files=files)
        print(f"file passed to llamaparse for ocr :: {response.json()}") 

        job_id = response.json()["id"]
        result_type = "markdown"

        llamaparse_result_url = f"https://api.cloud.llamaindex.ai/api/parsing/job/{job_id}/result/{result_type}"

        # check for the result until its ready
        while True:
            response = requests.get(llamaparse_result_url, headers=headers)
            if response.status_code == 200:
                print("Llama parse response received")
                break


        return response.json()['markdown']
