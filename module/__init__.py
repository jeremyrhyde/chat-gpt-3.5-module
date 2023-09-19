from viam.components.generic import Generic
from viam.resource.registry import Registry, ResourceCreatorRegistration
from .chatgpt import MyChatGPTInstance


Registry.register_resource_creator(Generic.SUBTYPE,
                                   MyChatGPTInstance.MODEL,
                                   ResourceCreatorRegistration(MyChatGPTInstance.new))
