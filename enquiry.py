import streamlit as st
import pandas as pd
from openai import OpenAI
import openpyxl
import re
#s
# Placeholder for a function to call the large model:  s
def call_large_model(input_text, model, api_key):
    try:
        # Initialize OpenAI client
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        user_prompt = """#你是一个专业的问卷表单设计者，根据我提供的问卷文本，请根据文本中的标记符号设计对应的表单问题。## 标记符号的基本格式如下，{} : 代表此处是一道简单填空题，【】代表此处是一道选择题，（）代表此处是一道长文本填空题；##请需要按照顺序，设计问题表单：包括 1. 问题序号，2. 问题题干，3. 问题选项（如有）。其中，问题题干需要你根据现在的文本内容理解后生成。##要求：1. 输出格式整洁，问题题干简明合理，选项设计合理。输出为 Markdown 格式。并用'//'符号分隔开不同问题。2. 输出语言为中文。3. 只输出问卷，不要包含别的信息。4. 务必注意：生成问题表单中的问题起始编号与文本中的特殊符号的编号严格对应，请严格对照！！！
        #输出举例：问题-问题编号. 您公司的名字是什么? 回答：您公司的名字 /n
        
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
import re

combined_results = ""

def get_binary_file_downloader_html(bin_file, file_name):
    with open(bin_file, 'r', encoding='utf-8') as f:
        data = f.read()
    b64 = base64.b64encode(data.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="{file_name}.txt">点击下载问卷草稿</a>'
    return href

def number_special_symbols(text):
    patterns = [r'\【.*?\】', r'\{.*?\}', r'\（.*?\）']
    pattern = '|'.join(patterns)  # 合并所有的pattern
    matches = list(re.finditer(pattern, text))  # 找到所有符合pattern的子串
    matches.sort(key=lambda x: x.start())  # 按照子串在原文中出现的位置进行排序

    index = 0
    for match in matches:
        original_text = match.group(0)
        numbered_text = str(index) + '.' + original_text[:-1] + original_text[-1]
        text = text.replace(original_text, numbered_text, 1)
        index += 1

    return text


# Streamlit UI components
st.title("问卷自动生产工具")

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

#add a hint
st.info("请粘贴需要处理的文本，点击生成问卷按钮。挖空部分请用【】、{}、（）等符号标记。{} : 代表此处是一道简单填空题，【】代表此处是一道选择题，（）代表此处是一道长文本填空题；自然段之间用回车分隔！")

# Text area for user input
user_input = st.text_area("请粘贴输入文本，{} : 代表此处是一道简单填空题，【】代表此处是一道选择题，（）代表此处是一道长文本填空题；", height=300)

if user_input:
    if st.button("生成问卷"):
        with st.spinner('处理中...'):
            progress_bar = st.progress(0)

            processed_text = number_special_symbols(user_input)
            paragraphs = processed_text.split('\n')
            paragraphs = [paragraph for paragraph in paragraphs if paragraph.strip()]

            model_results = []
            for idx, paragraph in enumerate(paragraphs):
                result = call_large_model(paragraph, model, api_key)
                model_results.append(result)
                progress = (idx + 1) / len(paragraphs)
                progress_bar.progress(progress)

        with st.container():
            st.subheader("处理后的文本:")
            st.text_area("复制下方的处理后文本：", processed_text, height=150)

            st.subheader("模型输出:")
            for idx, result in enumerate(model_results):
                #st.expander(f"段落 {idx + 1} 的模型输出:", expanded=True).text_area("复制模型输出：", result, height=100)
                pass

        st.subheader("问卷草稿展示：")
        combined_results = "\t".join(model_results)
        st.text_area("复制问卷草稿展示：", combined_results, height=800)

        st.text(combined_results)

        # Re-display the download button enabled now that we have results to download
        st.download_button(
            label="下载问卷草稿为TXT文件",
            data=combined_results,
            file_name="问卷草稿.txt",
            mime="text/plain"
        )

