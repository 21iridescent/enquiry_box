import streamlit as st
import pandas as pd
from openai import OpenAI
import openpyxl
import re
#s
# Placeholder for a function to call the large model:q  s
def call_large_model(input_text, model, api_key):
    try:
        # Initialize OpenAI client
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        user_prompt = """# 你是一个专业的问卷表单设计者，根据我提供的文本，你需要根据文本中的标记符号设计对应的表单问题。## 标记符号的基本格式如下，{} : 代表此处是简单填空题，【】代表此处是选择题，（）代表此处是长文本填空题；## 你需要按照顺序，设计问题表单：包括 1. 问题序号，2. 问题题干，3. 问题选项（如有）。其中，问题题干需要你根据现在的文本内容理解后生成。要求：1. 输出格式整洁，问题题干简明合理，选项设计合理。2. 输出语言为中文。3. 只输出问卷，不要包含别的信息。4. 表单中的问题编号为文中的特殊符号编号，请严格对照！！！
        #输出举例：问题1. 您公司的名字是什么? 回答：您公司的名字 /n
        
        #文本："""
        combined_prompt = f"##{user_prompt}\n\n ## 待处理的文本: {input_text}"

        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": combined_prompt},
            ],
        )
        return completion.choices[0].message.content
    except Exception as e:
        return str(e)

# Function to replace special symbols with numbered symbols
def number_special_symbols(text):
    patterns = [r'\【.*?\】', r'\{.*?\}', r'\（.*?\）']
    index = 0

    for pattern in patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            original_text = match.group(0)
            numbered_text =  str(index) + '.' + original_text[:-1] + original_text[-1]
            text = text.replace(original_text, numbered_text, 1)
            index += 1

    return text


# Streamlit UI components
st.title("特殊符号文本处理及段落模型调用工具")

#api key输入框
api_key = st.text_input("输入API Key")

# 设置可用模型列表
available_models = [
    "mistralai/mistral-7b-instruct:free",
    "huggingfaceh4/zephyr-7b-beta:free",
    "anthropic/claude-3-haiku:beta",
    "openai/gpt-4-turbo",
    "anthropic/claude-3-sonnet:beta",
    "meta-llama/llama-3-70b-instruct"
]

model = st.selectbox("选择模型", available_models)

# Text area for user input
user_input = st.text_area("粘贴输入文本", height=300)

if user_input and st.button("生成问卷"):
    with st.spinner('处理中...'):
        processed_text = number_special_symbols(user_input)
        paragraphs = processed_text.split('\n')
        paragraphs = [paragraph for paragraph in paragraphs if paragraph.strip()]

        model_results = []
        for idx, paragraph in enumerate(paragraphs):
            result = call_large_model(paragraph, model, api_key)
            model_results.append(result)

        with st.container():
            st.subheader("处理后的文本:")
            st.text(processed_text)

            st.subheader("模型输出:")
            for idx, result in enumerate(model_results):
                st.expander(f"段落 {idx + 1} 的模型输出:", expanded=True).write(result)

        st.subheader("问卷草稿展示：")
        combined_results = "\n\n".join(model_results)
        st.text_area("合并结果", value=combined_results, height=300)