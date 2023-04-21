import openai
import sys
import json
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "modules"))

# role = """
# Imagine you are my friend and we have online videocall,
# and you see my camera. We will speak as a normal friends and
# in the end of each message I'll send you short json code with certain
# objects(e.g. {"objects": ["cup", "snapback hat"]}), that are persist in my video right now, and you will have to describe or
# mention it somehow(e.g. cool cup! or take off your phone, while we on call!)
# """

openai.api_key = "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"
model = "gpt-3.5-turbo"  # choosing gpt model


class ChatBot:  # this class returns a chatbot object powered by openai
    def __init__(self, role):
        self.role = role
        self.messages = [{"role": "system", "content": self.role}]

    def add_message(self, role, content):
        self.messages.append({"role": role, "content": content})

    def get_response(self, user_input):
        self.add_message("user", user_input)
        response = openai.ChatCompletion.create(
            model=model,
            messages=self.messages
        )
        result = response.choices[0].message.content
        self.add_message("assistant", result)
        return result


script_path = os.path.dirname(
    os.path.realpath(__file__))  # path of this script
# path of the json file, containing the roles
roles_file = os.path.join(
    script_path, '/home/dci-student/projects/AI-GroupProject/AI-Project/', 'roles.json')
with open(roles_file, 'r') as file:
    # roles_data is now a list, containing the roles
    roles_data = json.load(file)

for roles in roles_data:  # printing out all available roles
    print(roles)

while True:  # choose bot1 role
    bot_name = input("Enter role for bot:")
    try:
        role = roles_data[bot_name]
        bot = ChatBot(role)
        break
    except:
        print("Role not found. Try again")
        # play(bad)

# bot = ChatBot(role)
os.system('clear')
while True:
    msg = input("You say: ") + '\n\n{"objects": ["beer", "snapback hat"]}'
    print("\nGPT-Respond: ", bot.get_response(msg))
