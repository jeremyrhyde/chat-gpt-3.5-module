import asyncio
from typing import Any, ClassVar, Dict, Mapping, Optional
from viam.components.generic import Generic
from viam.components.component_base import ValueTypes
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName
from viam.resource.base import ResourceBase
from viam.resource.types import Model, ModelFamily

class MyChatGPTInstance(Generic):
    MODEL: ClassVar[Model] = Model(ModelFamily("jeremyrhyde", "generic"), "chatgpt")
    SUPPORTED_VERSIONS = ["gpt-3.5-turbo"]

    # Constructor
    @classmethod
    def new(self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]):
        chatGPTInstance = self(config.name)
        chatGPTInstance.reconfigure(config, dependencies)
        return chatGPTInstance
    
    # Validates JSON Configuration
    @classmethod
    def validate(self, config: ComponentConfig):
        version = config.attributes.fields["chat_gpt_version"].string_value
        if version not in self.SUPPORTED_VERSIONS:
            raise Exception("chat_gpt_version must be one of the follow: " + self.SUPPORTED_VERSIONS)
        return

    # Reconfigure module by resetting chat gpt connection
    def reconfigure(self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]):
        self.chat_gpt_version = config.attributes.fields["chat_gpt_version"].string_value
        # close chatgpt connection

        # Perform setup produced using yaml file should it be desired
        performSetup = config.attributes.fields["setup"].bool_value
        if performSetup:
            self.setup()

        return

    async def do_command(self, command: Mapping[str, ValueTypes], *, timeout: Optional[float] = None, **kwargs) -> Mapping[str, ValueTypes]:
        # Check for valid request
        if "input" not in command.keys():
            print("not a valid request")
            raise Exception("invalid request, no 'input' given") 
        
        cmd = command["input"]
        resp = {"response": cmd}
        return resp
    
    def setup():
        return
    
async def main():
    chatgpt=MyChatGPTInstance(name="chatgpt35")

    i = 0
    user_input = input("Enter new do command to run: ")
    while (user_input != "q"):
        test = {"input": user_input}
        response = await chatgpt.do_command(test)
        print(response)
        i = i + 1

        user_input = input("Enter new do command to run (" + str(i) + "): ")
    print("stopping run")
if __name__ == '__main__':
    asyncio.run(main())