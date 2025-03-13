import json
import os
import subprocess
from typing import Dict

import requests
import yaml
from huggingface_hub import hf_hub_download
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from openai import OpenAI
from pydantic import Field

from hyperpocket.tool import function_tool
from hyperpocket_langchain import PocketLangchain
from util import vessl_configure
import vessl

# VESSL configuration
VESSL_CONFIG = {
    "organization_name": "Your Organization Name",
    "project_name": "Your Project Name", 
    "storage_name": "Your Storage Name",
    "volume_name": "Your Volume Name"
}

# GPU configuration
GPU_CONFIG = {
    "cluster_name": "Your gpu cluster name",
    "preset": "Your gpu preset name",
    "memory": 84557184, # Memory size in MB
    "number": 2 # Number of GPUs
}

access_token = vessl_configure(
    organization_name=VESSL_CONFIG["organization_name"],
    project_name=VESSL_CONFIG["project_name"],
    force_update_access_token=False
)

@function_tool
def get_model_config(
    base_model_id: str = Field(default="", description="The Hugging Face model ID to get configuration for")
) -> Dict:
    """Get the model configuration from Hugging Face."""
    model_safetensors_index_json = 'model.safetensors.index.json'
    model_config_json = 'config.json'

    config_path = hf_hub_download(repo_id=base_model_id, filename=model_config_json)
    with open(config_path, 'r', encoding='utf-8') as file:
        config_content = json.loads(file.read())
        
    model_safetensors_path = hf_hub_download(repo_id=base_model_id, filename=model_safetensors_index_json)
    with open(model_safetensors_path, 'r', encoding='utf-8') as file:
        model_safetensors_content = json.loads(file.read())
    
    config_content['total_model_size'] = model_safetensors_content['metadata']['total_size']
    
    os.remove(config_path)
    os.remove(model_safetensors_path)
    
    return config_content

@function_tool
def get_dataset_info(
    dataset_name: str = Field(default="", description="The Hugging Face dataset name to get information for")
) -> Dict:
    """Get dataset information from Hugging Face."""
    response = requests.get(
        "https://datasets-server.huggingface.co/rows",
        params={
            "dataset": dataset_name,
            "config": "default", 
            "split": "train",
            "offset": "0",
            "length": "1",
        },
        timeout=30
    )
    features = response.json()['features']
    
    api_url = f"https://datasets-server.huggingface.co/info?dataset={dataset_name}"
    response = requests.get(api_url, timeout=30)
    info = response.json()
    info['features'] = features
    
    return info

@function_tool
def construct_finetuning_yaml(
    training_yaml_file_name: str = Field(default="", description="Name of the YAML file to create"),
    dataset_name: str = Field(default="", description="Name of the dataset to use for training"),
    base_model_id: str = Field(default="", description="ID of the base model to fine-tune"),
    finetuning_output_dir: str = Field(default="", description="Directory to store fine-tuning outputs"),
    base_model_config: str = Field(default="", description="Base Model configuration as a string"),
    dataset_info: str = Field(default="", description="Dataset information as a string"),
    gpu_memory: int = Field(default=0, description="Available GPU memory in MB"),
    gpu_number: int = Field(default=1, description="Number of GPUs to use"),
) -> str:
    """Construct the fine-tuning YAML configuration file."""
    prompt = f"""
Generate a YAML file for fine-tuning an LLM using Hugging Face's Autotrain.
The YAML should be formatted correctly and contain only the YAML content without additional text.
Ensure the configuration follows the GPU memory optimization guidelines and dynamically adjusts parameters as needed:

[Guidelines for GPU memory optimization]
- block_size: Should be adjusted based on available GPU memory and model requirements
- model_max_length: Match max_position_embeddings (131072) to prevent truncation
- batch_size: Should be determined by available GPU memory and adjusted dynamically
- gradient_accumulation: Adjust to balance memory usage and training efficiency
- mixed_precision: Use bf16 for NVIDIA GPUs that support it, otherwise consider fp16
- deepspeed: Use stage2_offload or other optimizations to manage large model training

[GPU Memory]
- GPU Number: {gpu_number}
- GPU Memory Size: {gpu_memory}

[Dataset Info]
{dataset_info}

[Model Configuration]
{base_model_config}

[Autotrain Template]
task: vessl-llm-finetuning
base_model: {base_model_id}
project_name: {finetuning_output_dir}
log: tensorboard
backend: local

data:
  path: {dataset_name}
  train_split: train
  valid_split: null
  chat_template: chatml
  column_mapping:
    text_column: model_answer
    rejected_text_column: reference_answer
    prompt_text_column: question

params:
  block_size: 8192
  model_max_length: 131072
  epochs: 2
  batch_size: 4
  lr: 1e-5
  peft: true
  quantization: null
  target_modules: all-linear
  padding: right
  optimizer: paged_adamw_8bit
  scheduler: linear
  gradient_accumulation: 8
  mixed_precision: bf16
  deepspeed: stage2_offload
  fp16: false
  bf16: true
  seed: 42
  save_total_limit: 2
  save_steps: 1000
  eval_steps: 500
  logging_steps: 50
  warmup_ratio: 0.03
  weight_decay: 0.01
  max_grad_norm: 1.0

Only return valid YAML output, nothing else. 
Do not change fields of base_model, project_name and path in YAML.
Do not include any other fields in the YAML output.
"""
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY environment variable is not set")
        
    client = OpenAI()
    response = client.chat.completions.create(
        model="o3-mini",
        messages=[
            {"role": "system", "content": "You are an AI assistant that outputs only YAML files."},
            {"role": "user", "content": prompt},
        ],
    )
    
    yaml_output = response.choices[0].message.content.strip()
    
    try:
        yaml.safe_load(yaml_output)
        with open(training_yaml_file_name, "w", encoding='utf-8') as f:
            f.write(yaml_output)
    except yaml.YAMLError as e:
        print("Invalid YAML generated:", e)
    
    return yaml_output

def copy_file(source: str, dest: str) -> None:
    """Copy a file between local and VESSL storage."""
    try:
        subprocess.run(["vessl", "storage", "copy-file", source, dest], check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to copy file: {e.stderr}")

@function_tool
def copy_file_local_to_storage(
    local_file_name: str = Field(default="", description="Local file path to copy from"),
    storage_name: str = Field(default="", description="Name of the storage to copy to"),
    volume_name: str = Field(default="", description="Name of the volume in storage")
) -> str:
    """Copy a file from local to VESSL storage."""
    if not os.path.exists(local_file_name):
        raise FileNotFoundError(f"Local file {local_file_name} does not exist")
        
    copy_file(local_file_name, f"volume://{storage_name}/{volume_name}")
    return "success copy file local to storage"

@function_tool
def create_run(
    cluster_name: str = Field(default="", description="Name of the cluster to run on"),
    preset: str = Field(default="", description="Preset configuration name"),
    training_yaml_file_name: str = Field(default="", description="Name of the training YAML file"),
    storage_name: str = Field(default="", description="Name of the storage"),
    volume_name: str = Field(default="", description="Name of the volume"),
    run_yaml_file_name: str = Field(default="", description="Name of the run YAML file")
) -> str:
    """Create and start a VESSL run."""
    if not os.path.exists(training_yaml_file_name):
        raise FileNotFoundError(f"Training YAML file {training_yaml_file_name} does not exist")
        
    run_yaml = f"""
name: vessl-llm-autotrain-finetuning
import:
  /root/: volume://{storage_name}/{volume_name}
export:
  /root/: volume://{storage_name}
resources:
  cluster: {cluster_name}
  preset: {preset}
image: quay.io/vessl-ai/torch:2.3.1-cuda12.1-r5
run:
  - |
    pip install autotrain-advanced
  - autotrain --config {training_yaml_file_name}
"""

    with open(run_yaml_file_name, "w", encoding='utf-8') as f:
        f.write(run_yaml)
    
    with open(run_yaml_file_name, "r", encoding='utf-8') as yaml_file:
        vessl.create_run(
            yaml_file=yaml_file,
            yaml_body="",
            yaml_file_name=run_yaml_file_name
        )
    
    return "success create run"

def agent(pocket: PocketLangchain) -> None:
    """Initialize and run the LangChain agent."""
    tools = pocket.get_tools()
    
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY environment variable is not set")
        
    llm = ChatOpenAI(model="gpt-4o")

    prompt = ChatPromptTemplate.from_messages([
        ("placeholder", "{chat_history}"),
        (
            "system",
            f"""
            You are a agent who automatically creates a vessl run for finetuning an LLM.
            GPU cluster name: {GPU_CONFIG["cluster_name"]}
            GPU preset: {GPU_CONFIG["preset"]}
            GPU memory: {GPU_CONFIG["memory"]}
            GPU number: {GPU_CONFIG["number"]}
            
            VESSL ORGANIZATION NAME: {VESSL_CONFIG["organization_name"]}
            VESSL PROJECT NAME: {VESSL_CONFIG["project_name"]}
            VESSL STORAGE NAME: {VESSL_CONFIG["storage_name"]}
            VESSL VOLUME NAME: {VESSL_CONFIG["volume_name"]}
            
            You will be given base_model_id and dataset_name.
            You will first get the base model config and dataset info.
            Then you will construct the finetuning yaml file.
            You will also copy the finetuning yaml file to the storage.
            After that, you will create a vessl run.
            """,
        ),
        ("placeholder", "{chat_history}"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,
    )

    print("\n\n\n")
    print("Hello, this is your VESSL agent.")
    while True:
        print("user(q to quit) : ", end="")
        user_input = input()
        if user_input == "q":
            print("Good bye!")
            break

        response = agent_executor.invoke({"input": user_input})
        print("vessl agent : ", response["output"])
        print()


if __name__ == "__main__":
    # model_repo_id = "HuggingFaceTB/SmolLM2-1.7B-Instruct"
    # dataset_name = "HuggingFaceH4/no_robots"
    with PocketLangchain(
        tools=[
            get_model_config,
            get_dataset_info,
            construct_finetuning_yaml,
            copy_file_local_to_storage,
            create_run,
        ],
    ) as pocket:
        agent(pocket)
