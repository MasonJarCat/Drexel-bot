from logging import config
import requests
from config import Config
from openai import OpenAI
from typing_extensions import override
from openai import AssistantEventHandler

class EventHandler(AssistantEventHandler):    
  @override
  def on_text_created(self, text) -> None:
    print(f"\Drexel Bot > ", end="", flush=True)
      
  @override
  def on_text_delta(self, delta, snapshot):
    print(delta.value, end="", flush=True)
      
  def on_tool_call_created(self, tool_call):
    print(f"\Drexel Bot > {tool_call.type}\n", flush=True)
  
  def on_tool_call_delta(self, delta, snapshot):
    if delta.type == 'code_interpreter':
      if delta.code_interpreter.input:
        print(delta.code_interpreter.input, end="", flush=True)
      if delta.code_interpreter.outputs:
        print(f"\n\noutput >", flush=True)
        for output in delta.code_interpreter.outputs:
          if output.type == "logs":
            print(f"\n{output.logs}", flush=True)
 
# Then, we use the `stream` SDK helper 
# with the `EventHandler` class to create the Run 
# and stream the response.
def main():
    
   
    config = Config("test.yaml").get_config()
    OPENAI_API_KEY = config.get("openai_api_key")
    client = OpenAI(api_key=OPENAI_API_KEY)
    thread = client.beta.threads.create()
    assistant = client.beta.assistants.retrieve("asst_0KNAdEm6MQaoi04hcfA4h54g")

    while True:
        # Get user input
        command = input("Enter a command: ")
        message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=command
        )
        with client.beta.threads.runs.stream(
        thread_id=thread.id,
        assistant_id=assistant.id,
        instructions="Help the student with their questions about drexel university.",
        event_handler=EventHandler(),
        ) as stream:
            stream.until_done()
        # Ask user if they want to continue
        choice = input("\nDo you want to continue? (y/n): ")
        if choice.lower() != "y":
            break

 
# First, we create a EventHandler class to define
# how we want to handle the events in the response stream.
 

 

  
if __name__ == "__main__":
    main()