import openai
import json
import os

openai.api_key = "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"
model = "gpt-3.5-turbo"  # choosing gpt model


class ChatBot:
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


def show_roles(roles):
    print("Available bot roles:")
    for role in roles:
        print(role)


def get_roles():
    with open("roles.json") as f:
        return json.load(f)


def choose_bot(roles):
    while True:
        show_roles(roles)
        bot_name = input("Enter role for bot: ")
        try:
            role = roles[bot_name]
            return ChatBot(role)
        except KeyError:
            print("Role not found. Try again.")


def run_chat(bot):
    while True:
        msg = input("You say: ") + '\n\n{"objects": ["beer", "snapback hat"]}'
        response = bot.get_response(msg)
        print("GPT-Respond: ", response)


if __name__ == "__main__":
    roles = get_roles()
    bot = choose_bot(roles)
    run_chat(bot)
