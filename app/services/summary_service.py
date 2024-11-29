import re
import json
from ruamel.yaml import YAML
from pydantic import Field, create_model
from jinja2 import Template
import pdfkit
import tempfile
from dropbox_helper import upload_files_to_drop_box
from datetime import datetime
from pydantic import SecretStr
from common.decorators import async_retry

from langchain_openai import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from openai import OpenAI
ruyaml = YAML()

api_key = "sample_api_key" #to store in env variable
wrapped_key = SecretStr(api_key)
llm_model = ChatOpenAI(
    api_key=wrapped_key,
    temperature=0,
    model="gpt-4o-mini",
)

# llm_model = None
@async_retry(max_retries=5, delay=5.0, backoff=2.0)
async def generate_summary_from_llm(input_dict: dict, generate_pdf: bool=False):
    summary_model = get_summary_model()
    summary_response_schema = summary_model.schema_json(indent=4)
    if '_id' in input_dict:
        input_dict.pop('_id')
    system_prompt = f"""
*Task Description*:
You are tasked with generating summary for the given product information.
You are tasked with generating one page summary for the given publicly available information on Artificial
Intelligence/Machine Learning enterprise software platforms with the following details:
- Products and/or features that make the platform
- Key differentiators of the product (say opensource, SOC 2 compliant, on prem deployments etc.)
- Details on current clients and industries that the platforms are serving
- Pricing information (where available)
- Feel free to add any other information that is relevant to the user while judging the quality of the product

*Follow this JSON schema and provide the responses in YAML format (Strictly adhere to this schema):*
{summary_response_schema}
"""
    prompt = f"""
Publically available information:
{json.dumps(input_dict)}

Response(in YAML structure):
"""

    template = ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate.from_template(system_prompt),
            HumanMessagePromptTemplate.from_template(prompt),
        ]
    )
    # formatted_template = template.format_messages(
    #     summary_response_schema=summary_response_schema,
    #     input_text=json.dumps(input_dict, indent=4),
    # )
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
    #NOTE: I HAVE TESTED THIS WITH AN API KEY, SINCE I DO NOT HAVE THE ACCESS TO PAID VERSION, I GOT AN 429. BUT THAT CONFIRMS THAT THE CODE IS WORKING
    # try:
        # response = await llm_model.ainvoke(messages)
        # response_dict = await post_process_response(
        #     response.content
        # )
    # except Exception as e:
    #     raise Exception("Open AI could not process the request") #TODO: ADD exponential back offs here as well
    response_dict = {"summary": "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book"}
    if not generate_pdf:
        return response_dict
    await create_pdf_and_upload_to_dropbox(response_dict, input_dict)

async def create_pdf_and_upload_to_dropbox(response_dict: dict, input_dict: dict):
    input_dict.update(response_dict)
    # Configuration or pdf
    options = {
        "enable-local-file-access": None,
        "margin-top": "0.75in",
        "margin-right": "0.75in",
        "margin-bottom": "0.75in",
        "margin-left": "0.75in",
    }
    with open("pdf_template.html") as f:
        template = Template(f.read())
    # with tempfile.NamedTemporaryFile(prefix='summary_pdf', delete=True) as temp_file:
    #     file_path = f'{temp_file.name}.pdf'
    file_path = f"{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}_summary_pdf.pdf"
    html = template.render(data=input_dict)
    pdfkit.from_string(html, file_path, options=options)
    await upload_files_to_drop_box(file_name=file_path)

async def post_process_response(resp: str):
    response_dict = yaml_to_dict(resp)
    return response_dict


def yaml_to_dict(yaml_text: str):
    pattern = r"```yaml\s*(.*?)\s*```"
    match = re.search(pattern, yaml_text, re.DOTALL)
    yaml_content = ""
    if match:
        yaml_content = match.group(1)
    yaml_text = yaml_content
    yaml_dict = dict()
    try:
        yaml_dict = ruyaml.load(yaml_text)
    except Exception as e:
        raise Exception("Could not post process the llm response")
    return yaml_dict

def get_summary_model():
    summary_response_model = create_model(
        "Summary Response Model",
        summary=(
            str,
            Field(
                ...,
                title="summary",
                description="A paragraph containing summary of the given product.",
            ),
        ),
    )

    return summary_response_model

