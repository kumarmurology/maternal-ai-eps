import streamlit as st
import pdfplumber
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="Maternal AI – EPS Module", layout="centered")

st.title("Maternal AI – EPS Module (Prototype)")
st.markdown("#### Early Pregnancy Scan Structured Summary")

uploaded_file = st.file_uploader("Upload EPS Report (PDF)", type="pdf")

if uploaded_file is not None:
    text = ""

    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted

    prompt = f"""
Extract the following parameters from this Early Pregnancy Scan report.

Return output strictly in this format:

Fetal Pole: <value>
Yolk Sac: <value>
CRL: <value>
Gestational Age: <value>
EDD: <value>

If any parameter is missing, write 'Not mentioned'.

REPORT:
{text}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    result = response.choices[0].message.content

    lines = result.split("\n")
    data = {}
    for line in lines:
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip()

    st.markdown("---")
    st.markdown("### Scan Findings")

    def display_field(label, value):
        if "not" in value.lower() or "absent" in value.lower():
            st.markdown(f"**{label}:** 🔴 Abnormal — {value}")
        else:
            st.markdown(f"**{label}:** 🟢 Normal — {value}")

    display_field("Fetal Pole", data.get("Fetal Pole", "Not mentioned"))
    display_field("Yolk Sac", data.get("Yolk Sac", "Not mentioned"))
    display_field("CRL", data.get("CRL", "Not mentioned"))

    st.markdown(f"**Gestational Age:** {data.get('Gestational Age', 'Not mentioned')}")
    st.markdown(f"**EDD:** {data.get('EDD', 'Not mentioned')}")

    st.markdown("---")
    st.caption("AI-generated structured summary. For clinical decision support only.")
