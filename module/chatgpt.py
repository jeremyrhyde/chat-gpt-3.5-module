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
import openai
from datetime import datetime, timedelta

from google.protobuf.json_format import Parse, ParseDict

class MyChatGPTInstance(Generic):
    MODEL: ClassVar[Model] = Model(ModelFamily("jeremyrhyde", "generic"), "chatgpt")
    SUPPORTED_VERSIONS = ["gpt-3.5-turbo"]
    LOGGER = getLogger(__name__)
    
    timeoutSeconds = 0
    resetMessageEveryLoop = False
    messages = []

    # Constructor for chat-gpt model
    @classmethod
    def new(cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]):
        chatGPTInstance = cls(config.name)
        chatGPTInstance.reconfigure(config, dependencies)

        cls.LOGGER.info("new complete")
        cls.LOGGER.info("api key: " + cls.api_key)
        return chatGPTInstance
    
    # Validates JSON Configuration
    @classmethod
    def validate(cls, config: ComponentConfig):
        version = config.attributes.fields["chat_gpt_version"].string_value
        if version not in cls.SUPPORTED_VERSIONS:
            raise Exception("{0} must be one of the follow: [{1}]".format(version, ", ".join(cls.SUPPORTED_VERSIONS)))
        
        cls.LOGGER.info("validation complete")
        return

    @classmethod
    # Reconfigure module by resetting chat gpt connection
    def reconfigure(self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]):
        # Get API key
        self.api_key = config.attributes.fields["api_key"].string_value
        #openai.my_api_key = self.api_key

        # Get chat gpt version
        self.chat_gpt_version = config.attributes.fields["chat_gpt_version"].string_value

        # Get timeout
        self.timeoutSeconds = config.attributes.fields["timeout"].number_value
        if self.timeoutSeconds == 0:
            self.resetMessageEveryLoop = True

        # Setup message on reeconfigure/initialization
        self.resetMessage()

        # Log input vars
        self.LOGGER.info("Chat GPT API KEY: " + self.api_key)
        self.LOGGER.info("Chat GPT VERSION: " + self.chat_gpt_version)
        self.LOGGER.info("Timeout (seconds): " + str(self.timeoutSeconds) + "s")
        self.LOGGER.info("Reset every loop: " + str(self.resetMessageEveryLoop))

        self.LOGGER.info("reconfigure complete")
        self.LOGGER.info("api key: " + self.api_key)
        return

    @classmethod
    # Implements the do_command which will respond to a map with key "request"
    async def do_command(self, input: Mapping[str, ValueTypes], *, timeout: Optional[float] = None, **kwargs) -> Mapping[str, ValueTypes]:
        # Check for valid request
        if "request" not in input.keys():
            print("not a valid request")
            return {"response": "invalid request, no 'input' given"}
        
        # Check if time has surpassed timeout
        if self.resetMessageEveryLoop or datetime.now() - self.lastTime > timedelta(seconds=self.timeoutSeconds):
            self.resetMessage()
        else :
            self.lastTime = datetime.now()

        # Send request to chat gpt  
        self.messages.append({"role": "user", "content": input["request"]})
        self.LOGGER.info("REQUEST")
        for message in self.messages:
            self.LOGGER.info(" - (message) | role: " + message["role"] + ", content: " + message["content"])

        # Call Chat GPT
        #chat = openai.ChatCompletion.create(model=self.chat_gpt_version, messages=self.messages)
       
        # Contruct response
        # resp = {"response": chat.choices[0].message.content, "timestamp": self.lastTime}
        resp = {
            "response": input["request"], 
            "timestamp": self.lastTime
        }

        self.LOGGER.info("RESPONSE")
        self.LOGGER.info(" - " + self.printMap(resp))
        return resp
    
    @classmethod
    # Reset the message sent to chat gpt to only include initial header
    def resetMessage(self):
        self.LOGGER.info("resetting")
        self.messages = [{"role": "system", "content": "You are a intelligent assistant."}]
        self.lastTime = datetime.now()
        return
    
    @staticmethod
    def printMap(m: Mapping[str, ValueTypes]):
        s = ""
        for key, value in m.items():
            s = s + ("{" + key + ": " + str(value) + "}, ")
        return s
            
    
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