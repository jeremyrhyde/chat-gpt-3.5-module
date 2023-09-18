import asyncio
from typing import Any, ClassVar, Dict, Mapping, Optional
from viam.components.generic import Generic
from viam.components.component_base import ValueTypes
from viam.proto.app.robot import ComponentConfig, RobotConfig
from viam.proto.common import ResourceName
from viam.resource.base import ResourceBase
from viam.resource.types import Model, ModelFamily
import yaml
from viam.logging import getLogger
from google.protobuf.struct_pb2 import Struct
import google.protobuf.struct_pb2
import json

from google.protobuf.json_format import Parse, ParseDict

class MyChatGPTInstance(Generic):
    MODEL: ClassVar[Model] = Model(ModelFamily("jeremyrhyde", "generic"), "chatgpt")
    SUPPORTED_VERSIONS = ["gpt-3.5-turbo"]
    LOGGER = getLogger(__name__)

    # Constructor for chat-gpt model
    @classmethod
    def new(self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]):
        chatGPTInstance = self(config.name)

        with open('api_keys.yml', 'r') as file:
            api_keys = yaml.safe_load(file)

        self.chat_gpt_api_key = api_keys["chat-gpt"]
        self.LOGGER.info("Chat GPT API KEY: " + self.chat_gpt_api_key["api_key"])
        
        chatGPTInstance.reconfigure(config, dependencies)

        self.LOGGER.info("new complete")
        return chatGPTInstance
    
    # Validates JSON Configuration
    @classmethod
    def validate(self, config: ComponentConfig):
        version = config.attributes.fields["chat_gpt_version"].string_value
        if version not in self.SUPPORTED_VERSIONS:
            raise Exception("{0} must be one of the follow: [{1}]".format(version, ", ".join(self.SUPPORTED_VERSIONS)))
        
        self.LOGGER.info("validation complete")
        return

    # Reconfigure module by resetting chat gpt connection
    def reconfigure(self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]):
        self.chat_gpt_version = config.attributes.fields["chat_gpt_version"].string_value
        self.LOGGER.info("Chat GPT Version: " + self.chat_gpt_version)
        # close chatgpt connection

        # Perform setup produced using yaml file should it be desired
        performSetup = config.attributes.fields["setup"].bool_value
        if performSetup:
            self.setup()

        self.LOGGER.info("reconfigure complete")
        return

    # Implements the do_command which will respond to a map with key "request"
    async def do_command(self, command: Mapping[str, ValueTypes], *, timeout: Optional[float] = None, **kwargs) -> Mapping[str, ValueTypes]:
        self.LOGGER.info(command)
        
        # Check for valid request
        if "request" not in command.keys():
            print("not a valid request")
            raise Exception("invalid request, no 'input' given") 
        
        cmd = command["request"]
        resp = {"response": cmd}

        self.LOGGER.info(resp)
        return resp
    
    def setup(self):
        return
    

    
async def main():
    chatgpt=MyChatGPTInstance(name="test")

    with open("example_config.json") as f:
        robotConfigJson = json.load(f)
        robotConfig = ParseDict(robotConfigJson, RobotConfig())
        chatGPTConfig = robotConfig.components[0]

        chatgpt.validate(chatGPTConfig)
        chatgpt.new(chatGPTConfig, {})

    i = 0
    user_input = input("Enter new do command to run (" + str(i) + "): ")
    while (user_input != "q"):
        test = {"request": user_input}
        response = await chatgpt.do_command(test)
        i = i + 1

        user_input = input("Enter new do command to run (" + str(i) + "): ")
    print("stopping run")
if __name__ == '__main__':
    asyncio.run(main())