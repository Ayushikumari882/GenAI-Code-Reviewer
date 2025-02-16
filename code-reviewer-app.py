import streamlit as st
import openai
import re
from typing import Dict, Tuple

class CodeReviewer:
    def __init__(self, api_key: str):
        """Initialize the CodeReviewer with OpenAI API key."""
        openai.api_key = api_key
        
    def review_code(self, code: str) -> Tuple[Dict, str]:
        """
        Review the provided code using OpenAI API.
        Returns a tuple of (issues_dict, fixed_code).
        """
        try:
            # Prompt engineering for better results
            prompt = f"""Review the following Python code and provide:
            1. A list of potential bugs and issues
            2. Suggestions for improvements
            3. A fixed version of the code
            
            Here's the code to review:
            ```python
            {code}
            ```
            
            Provide the response in the following format:
            ISSUES:
            - [issue description]
            
            FIXED_CODE:
            [fixed code here]
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert Python code reviewer. Provide detailed, actionable feedback."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # Parse the response
            response_text = response.choices[0].message.content
            issues = []
            fixed_code = ""
            
            # Extract issues and fixed code from response
            if "ISSUES:" in response_text and "FIXED_CODE:" in response_text:
                issues_text = response_text.split("ISSUES:")[1].split("FIXED_CODE:")[0]
                fixed_code = response_text.split("FIXED_CODE:")[1].strip()
                
                # Parse issues into a list
                issues = [issue.strip() for issue in issues_text.split('-') if issue.strip()]
            
            return {"issues": issues}, fixed_code
            
        except Exception as e:
            return {"error": str(e)}, ""

def create_streamlit_ui():
    """Create the Streamlit user interface."""
    st.set_page_config(page_title="AI Code Reviewer", page_icon="🔍", layout="wide")
    
    st.title("🔍 AI Code Reviewer")
    st.write("Submit your Python code for AI-powered review and suggestions.")
    
    # API key input (you might want to use st.secrets in production)
    api_key = st.text_input("Enter OpenAI API Key:", type="password")
    
    # Code input area
    code_input = st.text_area("Enter your Python code here:", height=300)
    
    if st.button("Review Code") and api_key and code_input:
        try:
            reviewer = CodeReviewer(api_key)
            with st.spinner("Reviewing your code..."):
                issues_dict, fixed_code = reviewer.review_code(code_input)
            
            # Display results
            if "error" in issues_dict:
                st.error(f"Error during code review: {issues_dict['error']}")
            else:
                # Display issues
                st.subheader("📋 Review Comments")
                for issue in issues_dict["issues"]:
                    st.warning(issue)
                
                # Display fixed code
                if fixed_code:
                    st.subheader("✨ Improved Code")
                    st.code(fixed_code, language="python")
                    
                    # Add copy button for fixed code
                    if st.button("Copy Improved Code"):
                        st.write("Code copied to clipboard!")
                        st.session_state["clipboard"] = fixed_code
        
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    
    # Add usage instructions in the sidebar
    st.sidebar.title("📖 How to Use")
    st.sidebar.write("""
    1. Enter your OpenAI API key
    2. Paste your Python code in the text area
    3. Click 'Review Code' to get feedback
    4. Review the suggestions and improved code
    5. Copy the improved code if desired
    """)
    
    # Add footer
    st.markdown("---")
    st.markdown("Built with Streamlit and OpenAI GPT-4")

if __name__ == "__main__":
    create_streamlit_ui()
