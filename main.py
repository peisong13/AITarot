import streamlit as st
from openai import OpenAI
import time
import json
import random
from dotenv import load_dotenv
import os

load_dotenv('.env', override=True)

# 设置 OpenAI GPT API 密钥
openai_api_key = os.getenv("OPENAI_API_KEY")


deck = json.load(open('Cards.json', 'r', encoding='utf-8'))

# Streamlit 应用程序的标题
st.title("🔮Tarot Card Game")

if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": [{"type": "text", "content": "告诉我你心中的疑问吧 ❤️"}]
    }]
    # print('messege initialized')
if "disable_input" not in st.session_state:
    st.session_state.disable_input = False

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        for content in message["content"]:
            if content["type"] == "text":
                st.markdown(content["content"])
            elif content["type"] == "image":
                st.image(content["content"])
            elif content["type"] == "video":
                st.video(content["content"])

def add_message(role, content, delay=0.05):
     with st.chat_message(role):
        message_placeholder = st.empty()
        full_response = ""

        for chunk in list(content):
            full_response += chunk + ""
            time.sleep(delay)
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)

def disable():
    st.session_state["disable_input"] = True

if question := st.chat_input(placeholder="输入你内心的疑问", key='input', disabled=st.session_state.disable_input, on_submit=disable):
    add_message("user", question)

    chosen_cards = random.sample(deck, 5)
    chosen_status = random.choices(["正位", "逆位"], k=5)

    card_prompt = ""
    for i in range(5):
        card = chosen_cards[i]
        status = chosen_status[i]
        meaning = card["upright"] if status == "正位" else card["reverse"]

        add_message("assistant", f"第 {i+1} 张牌：" + card["name"] + "（" + status + "）")

        card_prompt += f"第 {i+1} 张牌：" + card["name"] + "（" + status + f"）, 寓意：{meaning}\n"
        time.sleep(0.5)
    print(card_prompt)
    with st.spinner("正在解读中..."):
        client = OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[{'role':'system','content':'你是一个经验丰富的塔罗牌占卜师，你的任务是根据客户的问题和抽取的牌面为他们的问题提供解答，同时要尽可能展现出积极的态度，引导客户朝着积极的方向发展。'},
                      {'role':'user','content':f"""问题是: {question},
                        抽取的牌面是:{card_prompt}"""}],
            temperature=0.7,
            # max_tokens=500,
            top_p=0.96,
            presence_penalty=0.1,
            stop=None)
    add_message("assistant", response.choices[0].message.content)
    time.sleep(0.1)

    add_message("assistant", "感谢你的提问，祝你好运！")
