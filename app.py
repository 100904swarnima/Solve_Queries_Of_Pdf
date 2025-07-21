import streamlit as st
import google.generativeai as genai
import fitz  # PyMuPDF
import tempfile
import os

# 🔐 Configure your Gemini API key
genai.configure(api_key="Enter your gemini key")
model = genai.GenerativeModel("gemini-1.5-flash")

# ✅ Extract text from uploaded PDF files
def extract_text_from_pdfs(uploaded_files):
    full_text = ""
    for uploaded_file in uploaded_files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        doc = fitz.open(tmp_path)
        for page in doc:
            full_text += page.get_text()
        doc.close()
        os.unlink(tmp_path)
    return full_text

# ✅ Ask Gemini based on PDF + question
def ask_gemini(text, question):
    prompt = f"Based on the following PDF content:\n\n{text}\n\nAnswer this question: {question}"
    response = model.generate_content(prompt)
    return response.text

# 🌐 Streamlit UI
st.set_page_config(page_title="Queries solve of the Pdf", layout="centered")
st.title("📄 Queries solve from the pdf")

# 🗃️ Session State for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 📂 File uploader
uploaded_files = st.file_uploader("Upload one or more PDF files", type="pdf", accept_multiple_files=True)

# 💬 Input for user's question
question = st.text_input("Ask a question about the uploaded PDFs")

# ✅ Ask button
if st.button("Ask Gemini"):
    if not uploaded_files:
        st.warning("Please upload at least one PDF.")
    elif not question:
        st.warning("Please enter your question.")
    else:
        with st.spinner("Extracting content and querying Gemini..."):
            try:
                combined_text = extract_text_from_pdfs(uploaded_files)
                answer = ask_gemini(combined_text, question)
                st.session_state.chat_history.append((question, answer))  # ✅ Save to history
                st.success("✅ Answer from Gemini:")
                st.write(answer)
            except Exception as e:
                st.error(f"Something went wrong: {str(e)}")

# 📜 Sidebar for chat history
st.sidebar.title("🕒 Chat History")
if st.session_state.chat_history:
    for i, (q, a) in enumerate(st.session_state.chat_history, 1):
        st.sidebar.markdown(f"**Q{i}:** {q}")
        st.sidebar.markdown(f"🔹 *{a[:100]}...*")
else:
    st.sidebar.info("No questions asked yet.")

