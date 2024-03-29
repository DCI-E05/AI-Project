import openai
import os


role = """
Imagine you are my friend and we have online videocall,
and you see my camera. We will speak as a normal friends and 
in the end of each message I'll send you short json code with certain
objects(e.g. {"objects": ["laptop", "snapback hat"]}), that are persist in my video right now, and you will have to describe or
mention it somehow(e.g. cool cup! or take off your phone, while we on call!)
"""

openai.api_key = "your_api_key"

class ChatBot: # this class returns a chatbot object powered by openai
    def __init__(self, role):
        self.role = role
        self.messages = [{"role": "system", "content": self.role}]

    def set_role(self, new_role):
        self.role = new_role
        self.messages = [{"role": "system", "content": self.role}]

    def add_message(self, role, content):
        self.messages.append({"role": role, "content": content})

    def get_response(self, user_input):
        self.add_message("user", user_input)
        try:
            response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=self.messages)
        except Exception as e:
            print(f"Error occurred while getting response from OpenAI API: {e}")
            return None

        result = response.choices[0].message.content
        self.add_message("assistant", result)
        return result


if __name__ == "__main__":
    bot = ChatBot("You are Python programmer.")
    os.system('clear')
    msg = "I have this code and when I start it, my CPU becomes quite hot. Can you tell me why?\n\n"

    with open('msg.txt') as f:
        msg += f.read()
    response = bot.get_response(msg)
    print("\n", role+':' , response)


    
