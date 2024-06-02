from logging import config
from turtle import st
from config import Config
from openai import OpenAI
from typing_extensions import override
from openai import AssistantEventHandler
import tkinter as tk
from tkinter import scrolledtext

class EventHandler(AssistantEventHandler):    
    @override
    def on_text_created(self, text) -> None:
        self.update_output(f"Drexel Bot > ", end="")
      
    @override
    def on_text_delta(self, delta, snapshot):
        self.update_output(delta.value, end="")
      
    def on_tool_call_created(self, tool_call):
        self.update_output(f"Drexel Bot > {tool_call.type}\n")
    
    def on_end(self) -> None:
        return self.update_output("\n")
    def on_tool_call_delta(self, delta, snapshot):
        if delta.type == 'code_interpreter':
            if delta.code_interpreter.input:
                self.update_output(delta.code_interpreter.input, end="")
            if delta.code_interpreter.outputs:
                self.update_output(f"\n\noutput >")
                for output in delta.code_interpreter.outputs:
                    if output.type == "logs":
                        self.update_output(f"\n{output.logs}")

    def __init__(self, update_output_callback):
        super().__init__()
        self.update_output = update_output_callback

def main():
    config = Config("test.yaml").get_config()
    OPENAI_API_KEY = config.get("openai_api_key")
    client = OpenAI(api_key=OPENAI_API_KEY)
    thread = client.beta.threads.create()
    assistant = client.beta.assistants.retrieve("asst_0KNAdEm6MQaoi04hcfA4h54g")

    def update_output(text, end="\n"):
        output_text.insert(tk.END, text + end)
        output_text.see(tk.END)
        root.update()

    def ask_question(event=""):
        command = user_input.get()
        user_input.set("")
        output_text.insert(tk.END, f"You > {command}\n")
        root.after(1, start_stream, command)
    def start_stream(command):
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=command
        )
        with client.beta.threads.runs.stream(
            thread_id=thread.id,
            assistant_id=assistant.id,
            instructions="Help the student with their questions about Drexel University.",
            event_handler=EventHandler(update_output),
        ) as stream:
            stream.until_done()

    root = tk.Tk()
    root.title("Drexel Bot")
    root.minsize(300, 200)
    frame = tk.Frame(root)
    frame.pack(padx=10, pady=10,expand="yes", fill=tk.BOTH,)
    
    user_input = tk.StringVar()

    entry = tk.Entry(frame, textvariable=user_input)
    entry.pack(padx=5, pady=5, expand=True, fill=tk.BOTH)
    entry.bind("<Return>", ask_question)
     
    ask_button = tk.Button(frame, text="Ask", command=ask_question)
    ask_button.pack(padx=5, pady=5, expand=True, fill=tk.BOTH)

    output_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD)
    output_text.pack(padx=5, pady=5, expand=True, fill=tk.BOTH)

    root.mainloop()

if __name__ == "__main__":
    main()
