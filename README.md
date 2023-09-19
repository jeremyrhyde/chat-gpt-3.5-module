# chat-gpt-module

This Chat-GPT module is part of the Viam [Registry](https://app.viam.com/module/jeremyrhyde/chat-gpt-module). It can be added to a Viam robot as a generic component and used using the DoCommand to send a string to a given Chat GPT endpoint and get a response back. 

This module requires a user to have their own API key from Chat GPT and currently support Chat GPT-3.5 Turbo. 

This module has only been tested on a Mac with an M1 chip.

## Deploy to robot

These instructions assume you're targeting a Darwin operating system. To deploy this module to a robot you can either use the module registry or insert the module manually:

### Using the registry

Go to 'Config' tab, then select components. Once on that page, at the bottom select 'Create Component' and select a generic component. From here you should see a section called 'Registry' from which you can select the chat-gpt-module.

### Manually adding module

Go to 'Config' tab, then change the 'Mode:' selector from 'Builder' to 'Raw JSON', then paste in the following.


```json
{
  "components": [
    {
      "attributes": {
        "request_key": "request",
        "api_key": "< CHAT GPT API KEY >",
        "timeout": 60,
        "chat_gpt_version": "gpt-3.5-turbo"
      },
      "depends_on": [],
      "name": "chat-gpt",
      "type": "generic",
      "model": "jeremyrhyde:nlp:chatgpt"
    }
  ],
  "modules": [
    {
      "type": "registry",
      "name": "jeremyrhyde_chat-gpt-module",
      "module_id": "jeremyrhyde:chat-gpt-module",
      "version": "0.0.0"
    }
  ]
}
```

After your module has been added along with the related generic component. There are several attributes parameters that can be set to aid in the use of this module.

 - `chat_gpt_version` (required): Select your desired chat-gpt api to use, currently only gpt-3.5-turbo is available
 - `api_key` (required): Set your Chat GPT API key here. This can be found on [platform.openai.com/account/api-keys](platform.openai.com/account/api-keys)
 - `timeout` (optional): The timeout in seconds that will dictate how frequently your chat history with Chat-GPT will be reset. This is used to limit the number of messages being sent. If no included this will be set to `0` so that each request has no history of past messages.
 - `request_key` (optional): This key is used to find the message in the DoCommand's `command` input. If left blank this will default to `request`.

## Usage

As this is a Viam module and a generic component it has an associated DoCommand which can be accessed from the other components/service or directly through the CLI. And example of sending a request via the CLI can be seen below:

```sh
viam robot part run --robot JHLaptop --location "Jeremy" --organization Jeremy -part JHLaptop-main  -d '{"name": "chat-gpt", "command": {"request":"What does the company viam robotics do?"}}' viam.component.generic.v1.GenericService.DoCommand
```

This example assumes the name of the generic component is `chat-gpt` and the `request_key` is `request`.

### Request

The request that is sent to the module is in the form of a protobuf Struct. This struct should have one field that should match the `request_key` defined in the config with the value of this key being the string to be sent to the desired Chat GPT endpoint. If no `request_key` is given, this field will be `request`. If the field does not match the defined `request_key` then a response `no valid input` will be returned.

```json
{
  "request": "What does the company viam robotics do?"
}
```

### Response

The response will be returned as a protobuf Struct. It will have a field `reply` which contains the response information returned by the module. This information is in two parts: a `response` which consists of the reply gotten from Chat GPT and a `timestamp` of when the response was returned. See the example below for more details:

```json
{
  "result": {
      "response": "Viam Robotics, also known as Viam, is a company that specializes in the development of cutting-edge autonomous robotic systems for industrial applications. Their primary focus is on developing advanced robotic systems that can work in collaboration with humans, enhancing productivity and efficiency in various industries such as e-commerce, logistics, and manufacturing.\n\nViam Robotics aims to bridge the gap between humans and machines by creating intelligent robots that can perform repetitive and physically demanding tasks while ensuring safety and ease of use. These robots are designed to navigate dynamic environments, handle various objects and materials, and adapt to different work scenarios.\n\nThrough the use of advanced sensors, computer vision, artificial intelligence, and machine learning technologies, Viam's autonomous robots can perceive their surroundings, make intelligent decisions, and interact seamlessly with human workers. They are capable of tasks such as picking and placing items, sorting and packing, and transporting goods within a warehouse or production facility.\n\nBy implementing Viam Robotics' solutions, companies can streamline their operations, reduce manual labor costs, increase throughput, and improve overall operational efficiency.",
      "timestamp": "2023-09-19 18:17:12.680958"
    }
}
```

## Troubleshooting

Should you encounter issues using this module. You can run the underlying chat-gpt.py code separately from the rest of a Viam server by either running:


 - ```python3 module/chat-gpt.py ```
 - ```./exec.sh 0 ```

 This should allow better logging and a similar framework for debugging your connection to Chat-GPT or potential malformations in your requests and responses. 