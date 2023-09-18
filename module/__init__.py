from viam.components.generic import Generic
from viam.resource.registry import Registry, ResourceCreatorRegistration
from .chat-gpt import MyResource


Registry.register_resource_creator(Generic.SUBTYPE, MyResource.MODEL, ResourceCreatorRegistration(MyResource.new))