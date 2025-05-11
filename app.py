import streamlit as st
import asyncio
import json
from playwright_helper.playwright_manager import PlaywrightManager
from autogen_agentchat.messages import ToolCallExecutionEvent
from autogen_agentchat.base import TaskResult
from agents import team
from autogen_core.models import FunctionExecutionResult

# Initialize PlaywrightManager
playwright_manager = PlaywrightManager()

# Set up Streamlit page
st.set_page_config(
    page_title="Agent Task Processing",
    page_icon="🤖",
    layout="wide"
)

st.title("Browser Automation Agent")
st.markdown("""
This system coordinates specialized agents to complete complex web automation tasks.
The agents communicate with each other and report their progress in real-time.
""")

# In your Streamlit app initialization
if "credentials" not in st.session_state:
    st.session_state.credentials = {
        "username": "",
        "password": ""
    }

with st.sidebar:
    st.subheader("Login Credentials (only required for login related tasks)")
    username = st.text_input("Username", key="username_input")
    if username:
        st.session_state.credentials["username"] = username
    password = st.text_input("Password", type="password", key="password_input")
    if password:
        st.session_state.credentials["password"] = password

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if isinstance(message["content"], dict):
            st.json(message["content"])
        else:
            st.markdown(message["content"])

# Function to format agent messages
def format_message(message):
    try:
        if isinstance(message, TaskResult):
            return f"**Final Response: {message.messages[-1].content}**"

        elif isinstance(message, ToolCallExecutionEvent) and isinstance(message.content, list):
            for item in message.content:
                if isinstance(item, FunctionExecutionResult) and isinstance(item.content, str) and "'current_page_dom'" in item.content:
                    try:
                        content_data = json.loads(item.content.replace("'", "\""))
                        return content_data
                    except json.JSONDecodeError:
                        return "Dom content"
                            
        elif hasattr(message, 'content'):
            content = message.content
   
            if isinstance(content, str) and "'current_page_dom'" in content:
                try:
                    content_json = json.loads(content.replace("'", "\""))
                    return {
                        "status": content_json.get("status", ""),
                        "message": "Page content retrieved",
                        "element_count": len(content_json["current_page_dom"].get("children", []))
                    }
                except:
                    return "Dom content"

            try:
                if isinstance(content, str):
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError:
                        return content
                return content
            except Exception as e:
                return str(content)
        return str(message)
    except Exception as e:
        return f"Message processing error: {str(e)}"

async def process_task(task):
    st.session_state.messages.append({"role": "user", "content": task})

    with st.chat_message("user"):
        st.markdown(task)
    
    status_container = st.empty()
    status_container.info("Agents are processing your task...")
    
    stream = team.run_stream(task=task)
    
    try:
        async for message in stream:
            formatted_content = format_message(message)
            
            role = "assistant"
            if hasattr(message, 'source'):
                if message.source == "user":
                    role = "user"
                else:
                    role = message.source
            
            # Add to message history
            st.session_state.messages.append({
                "role": role,
                "content": formatted_content,
                "source": getattr(message, 'source', None)
            })
            
            # Display the message
            with st.chat_message(role):
                if isinstance(formatted_content, dict):
                    st.json(formatted_content)
                else:
                    st.markdown(formatted_content)
    
    except Exception as e:
        st.error(f"Error processing task: {str(e)}")
    finally:
        status_container.empty()

# Main chat interface
if prompt := st.chat_input("Enter your task here (e.g. 'search for Yashika Malhotra on LinkedIn')"):
    # Process the task
    with st.spinner("Coordinating agent team..."):
        asyncio.run(process_task(prompt))