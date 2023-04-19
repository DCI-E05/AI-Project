import openai
import os


role = """
Imagine you are my friend and we have online videocall,
and you see my camera. We will speak as a normal friends and 
in the end of each message I'll send you short json code with certain
objects(e.g. {"objects": ["cup", "snapback hat"]}), that are persist in my video right now, and you will have to describe or
mention it somehow(e.g. cool cup! or take off your phone, while we on call!)
"""

openai.api_key = "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"


class ChatBot: # this class returns a chatbot object powered by openai
    def __init__(self, role):
        self.role = role
        self.messages = [{"role": "system", "content": self.role}]

    def add_message(self, role, content):
        self.messages.append({"role": role, "content": content})

    def get_response(self, user_input):
        self.add_message("user", user_input)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.messages
        )
        result = response.choices[0].message.content
        self.add_message("assistant", result)
        return result
    

bot = ChatBot(role)
os.system('clear')
while True:
    msg = input("You say: ") + '\n\n{"objects": ["phone", "snapback hat"]}'
    print("\nGPT-Respond: ",bot.get_response(msg))
    