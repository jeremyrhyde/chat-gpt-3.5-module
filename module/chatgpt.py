import asyncio
from datetime import datetime, timedelta
import json
import sys
import openai
from typing import List, ClassVar, Mapping, Optional

from viam.components.generic import Generic
from viam.components.component_base import ValueTypes
from viam.proto.app.robot import ComponentConfig, RobotConfig
from viam.proto.common import ResourceName, Geometry
from viam.resource.base import ResourceBase
from viam.resource.types import Model, ModelFamily
from viam.logging import getLogger

from google.protobuf.json_format import ParseDict


class MyChatGPTInstance(Generic):
    MODEL: ClassVar[Model] = Model(ModelFamily("jeremyrhyde", "nlp"), "chatgpt")
    SUPPORTED_VERSIONS = ["gpt-3.5-turbo"]

    LOGGER = getLogger(__name__)

    request_key = ""
    messages = []

    # Constructor for chat-gpt model
    @classmethod
    def new(cls, config: ComponentConfig,
            dependencies: Mapping[ResourceName, ResourceBase]):
        chatGPTInstance = cls(config.name)
        chatGPTInstance.reconfigure(config, dependencies)

        return chatGPTInstance

    # Validates JSON Configuration
    @classmethod
    def validate(cls, config: ComponentConfig):
        # Require version to be one of the supported values
        version = config.attributes.fields["chat_gpt_version"].string_value
        if version not in cls.SUPPORTED_VERSIONS:
            raise Exception("{0} must be one of the follow: [{1}]".format(
                version, ", ".join(cls.SUPPORTED_VERSIONS)))

        return

    @classmethod
    # Reconfigure module by resetting chat gpt connection
    def reconfigure(self, config: ComponentConfig,
                    dependencies: Mapping[ResourceName, ResourceBase]):
        # Get API key
        self.api_key = config.attributes.fields["api_key"].string_value

        # Get chat gpt version
        self.chat_gpt_version = config.attributes.fields["chat_gpt_version"].string_value

        # Get request key
        if "request_key" in config.attributes.fields:
            self.request_key = config.attributes.fields["request_key"].string_value
        else:
            self.request_key = "request"

        # Get timeout
        if "timeout" in config.attributes.fields:
            self.timeoutSeconds = config.attributes.fields["timeout"].number_value
        else:
            self.timeoutSeconds = 0

        # Sets up message on reeconfigure or initialization
        self.setupMessage()

        return

    @classmethod
    # Implements the do_command which will respond to a map with key "request"
    async def do_command(self, input: Mapping[str, ValueTypes], *,
                         timeout: Optional[float] = None,
                         **kwargs) -> Mapping[str, ValueTypes]:
        # Check for valid request
        if self.request_key not in input.keys():
            print("not a valid request")
            return {"response": "invalid request, no 'input' given"}

        # Check if time has surpassed timeout
        if datetime.now() - self.lastTime > timedelta(seconds=self.timeoutSeconds):
            self.setupMessage()

        # Send request to chat gpt
        self.messages.append({"role": "user", "content": input[self.request_key]})

        # Call Chat GPT
        resp = {}
        try:
            openai.api_key = self.api_key
            chat = openai.ChatCompletion.create(
                model=self.chat_gpt_version,
                messages=self.messages
            )

            # Contruct response
            resp = {
                "response": chat.choices[0].message.content,
                "timestamp": self.lastTime
            }
        except Exception as e:
            self.LOGGER.warn("issue occured interfacing with chat-gpt: " + str(e) + "\n")
            resp = {
                "response": "Unable to reach ChatGPT. Request was " + input["request"],
                "timestamp": self.lastTime
            }

        self.lastTime = datetime.now()
        return resp

    @classmethod
    # Sets up the message sent to chat gpt to only include initial header message
    def setupMessage(self):
        self.messages = [{"role": "system", "content": "You are a intelligent assistant."}]
        self.lastTime = datetime.now()
        return
    
    @classmethod
    async def get_geometries(self) -> List[Geometry]:
        return 


async def main():
    chatgpt = MyChatGPTInstance(name="test")

    with open("example_config.json") as f:
        robotConfigJson = json.load(f)
        robotConfig = ParseDict(robotConfigJson, RobotConfig())
        chatGPTConfig = robotConfig.components[0]

        chatgpt.validate(chatGPTConfig)
        chatgpt.new(chatGPTConfig, {})

    i = 0
    user_input = input("Enter new do command to run (" + str(i) + "): ")
    while user_input != "Quit":
        test = {"request": user_input}
        resp = await chatgpt.do_command(test)

        print("-------------------------------------------------------------")
        print("RESPONSE : " + resp["response"])
        print("TIMESTAMP " + str(resp["timestamp"]))
        print("-------------------------------------------------------------")

        i = i + 1

        user_input = input("Enter new do command to run (" + str(i) + "): ")

    sys.exit()

if __name__ == '__main__':
    asyncio.run(main())
