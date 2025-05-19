import os
from dotenv import load_dotenv
import streamlit as st
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate

# -----------------
# Environment Setup
# ----------------- 

load_dotenv()
model = init_chat_model("llama3-8b-8192", model_provider="groq")

# ---------------
# LLM based tasks
# ---------------

def build_regex_from_nl(nl_text):
    with st.spinner("Building..."):
        system_template = """
        You are a highly accurate and concise regex generator. Your task is to convert natural language instructions into valid, efficient, and minimal regular expressions (regex). Follow these guidelines carefully:
        - Regex Output Only: Respond only with the regular expression pattern unless explicitly asked to explain. Do not include extra commentary, code blocks, or markdown formatting unless requested.
        - Correctness First: Ensure the regex pattern matches the described behavior exactly and completely. Avoid overgeneralization or underfitting.
        - Conciseness and Efficiency: Use the simplest regex possible to achieve the described goal. Avoid unnecessary capture groups or verbose constructs.
        - Common Standards:
            - Assume the flavor is ECMAScript (JavaScript) unless specified otherwise.
            - Do not anchor with ^ or $ unless clearly required.
            - Use non-capturing groups (?:...) when groups are needed but not referenced.
        - Character Classes & Quantifiers: Use shorthand character classes (\\d, \\w, \\s, etc.) when appropriate. Use greedy or lazy quantifiers as required by the instruction.
        - Escaping: Properly escape special characters to avoid unintended behavior.
        - Edge Cases: Handle edge cases if mentioned (e.g., case sensitivity, optional components, boundary conditions).
        - Do not add unnecessary backticks
        """

        prompt_template = ChatPromptTemplate.from_messages(
            [("system", system_template), ("user", "{query}")]
        )
        prompt = prompt_template.invoke({"query": nl_text})
        response = model.invoke(prompt)
        text = response.content

        if text.startswith("`") and text.endswith("`"):
            text = text[1:-1]
        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1]
        
        return text


def explain_regex(regex):
    with st.spinner("Thinking..."):
        system_template = """
        You are a precise and knowledgeable regular expression (regex) explainer. Your role is to convert regex patterns into clear, concise, and accurate natural language explanations. Follow these instructions:
        - Explain What the Regex Does: Describe the overall function of the pattern in plain language.
        - Break Down Components: Explain each part or section of the regex, especially if the pattern is complex.
        - Use Natural Language: Avoid technical jargon unless necessary. Favor readable descriptions over formal syntax.
        - Be Accurate and Thorough: Ensure every element of the pattern is accounted for and explained correctly.
        - Be Concise: Keep explanations clear and compact, especially for simple patterns.
        - No Execution: Do not test or validate regex against data.
        - Regex Flavor: Assume ECMAScript (JavaScript) flavor unless specified otherwise.
        - Avoid Over-Explanation: Don't repeat similar parts unnecessarily (e.g., identical groups or ranges).

        Output format:
        - For basic use, return a paragraph explanation.
        - If the pattern is complex, use bullet points or step-by-step breakdowns.
        """

        prompt_template = ChatPromptTemplate.from_messages(
            [("system", system_template), ("user", "{query}")]
        )
        prompt = prompt_template.invoke({"query": regex})
        response = model.invoke(prompt)
        return response.content
    
# ---------------------
# Streamlit application
# ---------------------

st.set_page_config(page_title="Regex AI")
st.title("Regex Builder and Explainer")
tab1, tab2 = st.tabs(["Build Regex from Natural Language", "Explain Regex"])

with tab1:
    st.header("Build Regex")
    nl_input = st.text_area("Enter natural language description of the pattern:", height=150)
    if st.button("Generate Regex"):
        if nl_input.strip():
            regex_result = build_regex_from_nl(nl_input)
            st.code(regex_result, language="regex")
        else:
            st.warning("Please enter a description.")

with tab2:
    st.header("Explain Regex")
    regex_input = st.text_input("Enter the regex pattern to explain:")
    if st.button("Explain Regex"):
        if regex_input.strip():
            explanation = explain_regex(regex_input.strip())
            st.markdown(explanation)
        else:
            st.warning("Please enter a regex pattern.")
