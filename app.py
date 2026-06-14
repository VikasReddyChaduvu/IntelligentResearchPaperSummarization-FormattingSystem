import streamlit as st
import google.generativeai as genai
from docx import Document
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pyttsx3
import pandas as pd
import numpy as np
# GEMINI API 
GENAI_API_KEY = "YOUR_API_KEY"
genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")
# PAGE 
st.set_page_config(
    page_title="INTELLIGENT RESEARCH PAPER SYSTEM",
    layout="wide"
)
# COLORFUL UI 
st.markdown("""
<style>
.main-title{
font-size:42px;
font-weight:bold;
-webkit-background-clip: text;
 color:#9B0047;
}
.section{
font-size:26px;
font-weight:bold;
color:#9B0047;
margin-top:20px;
}
.stButton>button{
background: linear-gradient(90deg,#ff7eb3,#65d6ce);
color:white;
border:none;
border-radius:10px;
padding:8px 16px;
font-weight:bold;
}
</style>
""", unsafe_allow_html=True)
st.markdown(
'<div class="main-title">INTELLIGENT RESEARCH PAPER SUMMARIZATION AND FORMATTING SYSTEM</div>',
unsafe_allow_html=True)
# INPUT 
st.markdown('<div class="section">Input</div>', unsafe_allow_html=True)
mode = st.radio("Choose Input", ["Topic", "Upload File"], horizontal=True)
user_text = ""
if mode == "Topic":
    user_text = st.text_input("Enter Research Topic")
else:
    file = st.file_uploader("Upload TXT file", type=["txt"])
    if file:
        user_text = file.read().decode()
#  FORMAT
st.markdown('<div class="section">Paper Type</div>', unsafe_allow_html=True)
paper_type = st.radio("Select Format", ["IEEE", "APA"], horizontal=True)
# OPTIONAL AUTHOR PANEL 
st.markdown('<div class="section">Author Panel (Optional)</div>', unsafe_allow_html=True)
show = st.toggle("Add Author Details")
author=""
affiliation=""
email=""
if show:
    c1,c2,c3 = st.columns(3)
    author = c1.text_input("Author")
    affiliation = c2.text_input("Affiliation")
    email = c3.text_input("Email")
# SESSION 
if "paper" not in st.session_state:
    st.session_state.paper = ""
# GENERATOR
def generate(prompt):
    r = model.generate_content(prompt)
    return r.text
# VISUAL DATA 
def generate_visuals(topic):
    prompt=f"""
Create dataset for research topic {topic}
Return CSV format
Year,Accuracy
2019,70
2020,75
"""
    try:
        res=model.generate_content(prompt).text
        lines=[l for l in res.split("\n") if "," in l]
        df=pd.DataFrame(
            [i.split(",") for i in lines[1:]],
            columns=lines[0].split(",")
        )
        for col in df.columns[1:]:
            df[col]=pd.to_numeric(df[col],errors="coerce")
        return df
    except:
        return None
# SECTION BUTTONS
st.markdown('<div class="section">Generate Sections</div>', unsafe_allow_html=True)
b1,b2,b3,b4,b5,b6,b7 = st.columns(7)
if b1.button("Abstract"):
    p=f"Write Abstract (200-250 words) for {paper_type} research paper on {user_text}"
    st.session_state.paper+="\nABSTRACT\n"+generate(p)
if b2.button("Introduction"):
    p=f"Write Introduction for {paper_type} research paper on {user_text}"
    st.session_state.paper+="\nINTRODUCTION\n"+generate(p)
if b3.button("Literature Review"):
    p=f"Literature Review for {paper_type} research paper on {user_text}"
    st.session_state.paper+="\nLITERATURE REVIEW\n"+generate(p)
if b4.button("Methodology"):
    p=f"Methodology for {paper_type} research paper on {user_text}"
    st.session_state.paper+="\nMETHODOLOGY\n"+generate(p)
if b5.button("Results"):
    p=f"Results and discussion for {paper_type} research paper on {user_text}"
    st.session_state.paper+="\nRESULTS\n"+generate(p)
if b6.button("Conclusion"):
    p=f"Conclusion for {paper_type} research paper on {user_text}"
    st.session_state.paper+="\nCONCLUSION\n"+generate(p)
if b7.button("References"):
    p=f"Generate references for {paper_type} research paper on {user_text}"
    st.session_state.paper+="\nREFERENCES\n"+generate(p)
# FULL PAPER
st.markdown('<div class="section">Full Paper</div>', unsafe_allow_html=True)
if st.button("Generate Full Paper"):
    prompt=f"""
Write a full {paper_type} research paper.
Topic: {user_text}
Requirements
Abstract 200-250 words
Total words 3500-10000
Include tables and graphs if relevant
Sections
Abstract
Introduction
Literature Review
Methodology
Results
Conclusion
References
"""
    st.session_state.paper=generate(prompt)
#WORD ALERT
word_count=len(st.session_state.paper.split())
if word_count>0:
    if word_count<3500:
        st.warning("Paper below recommended length")
    if word_count>10000:
        st.error("Paper exceeds 10000 words")
#  PREVIEW 
st.markdown('<div class="section">Paper Preview</div>', unsafe_allow_html=True)
st.write(st.session_state.paper)
#  VISUALIZATION
st.markdown('<div class="section">Visualization</div>', unsafe_allow_html=True)
c1,c2,c3,c4 = st.columns(4)
# WORD CLOUD
if c1.button("Word Cloud"):
    wc=WordCloud(width=800,height=400).generate(st.session_state.paper)
    fig=plt.figure()
    plt.imshow(wc)
    plt.axis("off")
    st.pyplot(fig)
# AUDIO
if c2.button("Read Paper"):
    engine=pyttsx3.init()
    engine.say(st.session_state.paper[:2000])
    engine.runAndWait()
# AI CHAT
question = st.text_input("Ask about paper")
if c3.button("Ask AI"):
    ans=generate(question + st.session_state.paper)
    st.write(ans)
# TABLE + GRAPH
if c4.button("Generate Table / Graph"):
    df=generate_visuals(user_text)
    if df is not None:
        st.subheader("Generated Data")
        st.dataframe(df)
        fig=plt.figure()
        plt.plot(df.iloc[:,0],df.iloc[:,1],marker="o")
        plt.xlabel(df.columns[0])
        plt.ylabel(df.columns[1])
        plt.title("Research Trend")
        st.pyplot(fig)
# EXPORT
st.markdown('<div class="section">Export Options</div>', unsafe_allow_html=True)
styles=getSampleStyleSheet()
# IEEE PDF
def ieee_pdf(text):
    file="ieee_paper.pdf"
    frame1=Frame(40,40,250,750)
    frame2=Frame(300,40,250,750)
    template=PageTemplate(id="TwoCol",frames=[frame1,frame2])
    doc=BaseDocTemplate(file,pageTemplates=[template])
    story=[]
    for p in text.split("\n"):
        story.append(Paragraph(p, styles['Normal']))
        story.append(Spacer(1,6))
    doc.build(story)
    return file
# APA PDF
def apa_pdf(text):
    file="apa_paper.pdf"
    frame=Frame(40,40,520,750)
    template=PageTemplate(id="OneCol",frames=[frame])
    doc=BaseDocTemplate(file,pageTemplates=[template])
    story=[]
    for p in text.split("\n"):
        story.append(Paragraph(p, styles['Normal']))
        story.append(Spacer(1,6))
    doc.build(story)
    return file
# DOCX
def doc_export(text):
    name="paper.docx"
    d=Document()
    for p in text.split("\n"):
        d.add_paragraph(p)
    d.save(name)
    return name
e1,e2,e3 = st.columns(3)
# VIEW PDF
if e1.button("View PDF"):
    if paper_type=="IEEE":
        pdf=ieee_pdf(st.session_state.paper)
    else:
        pdf=apa_pdf(st.session_state.paper)
    st.success("PDF Generated")
# DOWNLOAD PDF
if e2.button("Download PDF"):
    if paper_type=="IEEE":
        pdf=ieee_pdf(st.session_state.paper)
    else:
        pdf=apa_pdf(st.session_state.paper)
    with open(pdf,"rb") as f:
        st.download_button("Download PDF",f,file_name=pdf)
# DOWNLOAD DOCX
if e3.button("Download DOCX"):
    doc=doc_export(st.session_state.paper)
    with open(doc,"rb") as f:
        st.download_button("Download DOCX",f,file_name=doc)
