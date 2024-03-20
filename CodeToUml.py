import httpx
import time
import openai
from pathlib import Path
from typing import Optional

class Test1:
    def __init__(self, filepath):
        self.filepath = filepath
        self.uml_dir = Path('output/')
        self.token_limit = 3500
        openai.api_key='5d57e861530c4f30b60dd25fae432f52'

    def _save_to_file(self, uml_code: str) -> Path:
        timestamp = str(int(time.time()))
        folder_name = 'uml_code_' + timestamp
        print(folder_name)
        self.uml_dir.joinpath(folder_name).mkdir(parents=True, exist_ok=True)
        filename = self.uml_dir.joinpath(folder_name, 'uml_code.puml')
        with open(filename, 'w') as f:
            f.write(uml_code)
        return filename

    def _extract_uml_code(self, message: str) -> Optional[str]:
        start = message.index('@startuml')
        end = message.index('@enduml') + len('@enduml')
        return message[start:end]

    def _generate_prompt(self, chunk: str) -> str:
        prompt = (chunk)
        return prompt

    def _convert_code_to_uml(self, python_code: str) -> Optional[str]:
        chunk_size = self.token_limit - 200  # Save some tokens for the prompt and API overhead
        chunks = [python_code[i:i + chunk_size] for i in range(0, len(python_code), chunk_size)]

        conversation = [
            {"role": "system",
             "content": "You are a helpful assistant and brilliant programmer. You are shown a programming project in sections"}
        ]

        # Add each chunk to the conversation
        for chunk in chunks:
            conversation.append({"role": "user", "content": self._generate_prompt(chunk)})

        # Add the instruction to generate a UML diagram
        conversation.append({"role": "user",
                             "content": "given all of that python code, generate a plantUML code for a UML class diagram for the whole coding project"})

        azure_configs = {
            "azure_endpoint": "https://dev-mgmt-infra.amaiz.corp.amdocs.azr/v1/hackathon/regions/canadaeast/",
            "api_key": "5d57e861530c4f30b60dd25fae432f52",
            "azure_deployment": "gpt-35-16k",
            "api_version": "2023-05-15",
            "http_client": httpx.Client(verify=False)  # SSL Disabled
        }
        response = openai.AzureOpenAI(**azure_configs).chat.completions.create(
            model="gpt-3.5-turbo-16k",
            messages=conversation,
            temperature=0.5,
            max_tokens=2000
        )
        #print(response)
        # Extract UML code from the response
        uml_code = self._extract_uml_code(response.choices[0].message.content)
        return uml_code if uml_code else None

    def convert(self):
        python_code = ""
        with open(self.filepath, 'r') as f:
            python_code += f.read() + '\n\n'

        uml_code = self._convert_code_to_uml(python_code)
        if uml_code is None:
            raise Exception("Failed to convert code to UML")

        uml_file = self._save_to_file(uml_code)

def main(filepath):
    converter=Test1(filepath)
    converter.convert()

if __name__ == "__main__":
    main('code/Sample.py')