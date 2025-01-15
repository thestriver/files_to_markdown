#!/usr/bin/env python
from dotenv import load_dotenv
import logging
from markitdown import MarkItDown
import os
from typing import Dict
from naptha_sdk.schemas import ToolDeployment, ToolRunInput
from naptha_sdk.user import sign_consumer_id
from files_to_markdown_tool.schemas import InputSchema

logger = logging.getLogger(__name__)

load_dotenv()


class FilesToMarkdownTool:
    def __init__(self, tool_deployment: ToolDeployment):
        self.tool_deployment = tool_deployment
        self.md = MarkItDown()

    def files_to_markdown(self, inputs: InputSchema):
        """
        Convert file to markdown using markitdown
        """
        logger.info(f"Converting file: {inputs.tool_input_data}")
        try:
            # Make sure file exists
            if not os.path.exists(inputs.tool_input_data):
                raise ValueError(f"Failed to find file: {inputs.tool_input_data}")

            # Convert file
            result = self.md.convert(inputs.tool_input_data)
            return {"text_content": result.text_content}

        except Exception as e:
            logger.error(f"Error converting file: {str(e)} to markdown")
            return {"error": str(e)}

def run(module_run: Dict, *args, **kwargs):
    """Run the module to convert file to markdown"""
    module_run = ToolRunInput(**module_run)
    module_run.inputs = InputSchema(**module_run.inputs)
    files_to_markdown_tool = FilesToMarkdownTool(module_run.deployment)

    method = getattr(files_to_markdown_tool, module_run.inputs.tool_name, None)

    if not method:
        raise ValueError(f"Method {module_run.inputs.tool_name} not found")

    result = method(module_run.inputs)

    return result


if __name__ == "__main__":
    import asyncio
    from naptha_sdk.client.naptha import Naptha
    from naptha_sdk.configs import setup_module_deployment

    naptha = Naptha()

    deployment = asyncio.run(setup_module_deployment("tool", "files_to_markdown_tool/configs/deployment.json", node_url = os.getenv("NODE_URL")))

    input_params = {
        "tool_name": "files_to_markdown",
        "tool_input_data": "files_to_markdown_tool/input_files/naptha.pptx"
    }

    module_run = {
        "inputs": input_params,
        "deployment": deployment,
        "consumer_id": naptha.user.id,
        "signature": sign_consumer_id(naptha.user.id, os.getenv("PRIVATE_KEY"))
    }

    response = run(module_run)
    text_content = response['text_content']
    print("Response: ", text_content)