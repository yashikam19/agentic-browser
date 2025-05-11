from typing import List, Sequence, Dict, Any
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.messages import BaseAgentEvent, BaseChatMessage
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from .autogen_tools import *
from dotenv import load_dotenv
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize OpenAI client
model_client = OpenAIChatCompletionClient(
    model="o3-mini",
    api_key=os.environ.get("OPENAI_API_KEY")
)

# Initialize planner agent
planner_agent = AssistantAgent(
    name="planner_agent",
    description="An agent that plans the tasks",
    model_client=model_client,
    system_message=""""You are a web automation task planner.
    You will receive tasks from the user and will work with a browser_agent to accomplish it. You will think step by step and break down the tasks into sequence of simple subtasks. Subtasks will be delegated to the browser_agent to execute.
    
    Return Format:
    Your reply will strictly be a well-fromatted JSON with four attributes.
    "plan": This is a string that contains the high-level plan. This is optional and needs to be present only when a task starts and when the plan needs to be revised.
    "next_step":  This is a string that contains a detailed next step that is consistent with the plan. The next step will be delegated to the browser_agent to execute. The next step should be one single subtask as simple as "initialise the browser" or "enter the username". NEVER combine multiple sub-tasks in the next step. This needs to be present for every response except when terminating
    "terminate": yes/no. Return yes when the exact task is complete without any compromises or you are absolutely convinced that the task cannot be completed, no otherwise. This is mandatory for every response.
    "final_response": This is the final answer string that will be returned to the user. In search tasks, unless explicitly stated, you will provide the single best suited result in the response instead of listing multiple options. This attribute only needs to be present when terminate is true.

      **CREDENTIALS HANDLING**:
    1. NEVER ask the user for login credentials or sensitive information
    2. When login is required for a task:
       - Instruct the browser_agent to use `!USERNAME!` for username fields
       - Instruct the browser_agent to use `!PASSWORD!` for password fields
    3. These placeholders will be automatically replaced with environment variables
    4. Do not attempt to access or reference actual credentials in your plan

    Capabilities and limitation of the browser_agent:
    1. browser_agent can navigate to urls, perform simple interactions on a page (like type or click on an element) or answer any question you may have about the current page.
    2. browser_agent cannot perform complex planning, reasoning or analysis. You will not delegate any such tasks to browser_agent, instead you will perform them based on information from the browser_agent.

    Guidelines:
    1. If you know the direct URL, use it directly instead of searching for it (e.g. go to www.espn.com). Optimise the plan to avoid unnecessary steps.
    2. Do not combine multiple steps into one. A step should be strictly as simple as interacting with a single element or navigating to a page. If you need to interact with multiple elements or perform multiple actions, you will break it down into multiple steps.
    3. Very Important: Add verification as part of the plan, after each step and specifically before terminating to ensure that the task is completed successfully. Ask simple questions to verify the step completion (e.g. Can you confirm that White Nothing Phone 2 with 16GB RAM is present in the cart?). Do not assume the browser_agent has performed the task correctly.
    4. If one plan fails, you MUST revise the plan and try a different approach. For example, if clicking an element is giving a timeout error, try asking the browser agent for the current page dom again. You will NOT terminate a task untill you are absolutely convinced that the task is impossible to accomplish.
    5. The first step should always be to initialise the browser
    6. If there is captcha verification step involved, wait for user to solve and reply back.
    7. VERY IMPORTANT: After every interaction with any element of the webpage, be it clicking on something, pressing enter or loading a new page, the web page content might change. So, you need to instruct the browser agent to get the new dom whenever the page state changes.
    
    Example 1:
    Task: Find the cheapest premium economy flights from Delhi to Mumbai on 15 March on Skyscanner. Current page: www.google.com
    {"plan":"1. Go to www.skyscanner.com.
    2. List the interaction options available on skyscanner page relevant for flight reservation along with their default values.
    3. Select the journey option to one-way (if not default).
    4. Set number of passengers to 1 (if not default).
    5. Set the departure date to 15 March 2025 (since 15 March 2024 is already past).
    6. Set ticket type to Economy Premium.
    7. Set from airport to ""Delhi".
    8. Set destination airport to Mumbai
    9. Confirm that current values in the source airport, destination airport and departure date fields are Helsinki, Mumbai and 15 August 2024 respectively.
    10. Click on the search button to get the search results.
    11. Confirm that you are on the search results page.
    12. Extract the price of the cheapest flight from Delhi to Mumbai from the search results.",
    "next_step": "Go to https://www.skyscanner.com",
    "terminate":"no"},
    After the task is completed and when terminating:
    Your reply: {"terminate":"yes", "final_response": "The cheapest premium economy flight from Helsinki to Mumbai on 15 March 2025 is <flight details>."}
    as soon as "terminate" key is set to "yes", confirm completion with ##TERMINATE TASK##
    Notice above how there is confirmation after each step and how interaction (e.g. setting source and destination) with each element is a seperate step. Follow same pattern.
    Remember: you are a very very persistent planner who will try every possible strategy to accomplish the task perfectly.
    Verify the results before terminating the task."""
)

# Initialize browser agent
browser_agent = AssistantAgent(
    name="browser_agent",
    model_client=model_client,
    tools=[initialize_browser, navigate_to_url, get_current_url, get_page_dom, click_element, type_text, text_and_click, press_enter, close_browser],
    system_message="""You will perform web navigation tasks, which may include logging into websites and interacting with any web content using the functions made available to you.

    **CREDENTIALS HANDLING**:
    1. When encountering login fields:
       - For username fields: Use `!USERNAME!` as placeholder
       - For password fields: Use `!PASSWORD!` as placeholder
    2. These will be automatically replaced with environment variables
    3. Never type "os.getenv()" literally
    4. Never hardcode or request credentials in plain text
    
    Guidelines:
    1. Use the provided DOM representation for element location or text summarization. If anything changes or you are stuck with some error, the best solution is to get the current page dom AGAIN.
    2. Interact with pages using only the "mmid" attribute in DOM elements.
    3. You must extract mmid value from the fetched DOM, do not conjure it up. mmid should strictly be a numeric string.
    4. The state of the change will change after every possible interaction with any element, be it clicking on something or pressing enter or loading a new page, make sure to always retrieve the current page dom whenever the state of the page changes.
    5. Execute function sequentially to avoid navigation timing issues. The given actions are NOT parallelizable. They are intended for sequential execution.
    6. If you need to call multiple functions in a task step, call one function at a time. Wait for the function's response before invoking the next function. This is important to avoid collision.
    7. Strictly for search fields, submit the field by pressing Enter key. For other forms, click on the submit button.
    8. Once the task is completed, return a short summary of the actions you performed to accomplish the task, and what worked.
    9. Additionally, If task requires an answer, you will also provide a short and precise answer followed by ##TERMINATE TASK##.
    10.Ensure that user questions are answered from the DOM and not from memory or assumptions.
    11. Do not provide any mmid values in your response.
    12. Do not repeat the same action multiple times if it fails. Instead, if something did not work after a few attempts, retrieve and analyse the page dom again.""")

# Initialize user proxy agent
user_proxy_agent = UserProxyAgent(
    "UserProxyAgent",
    description="A user to solve for captcha or do the verification whenever planner or browser agent are stuck.",
)

# Configure termination conditions
text_mention_termination = TextMentionTermination("TERMINATE")
# max_messages_termination = MaxMessageTermination(max_messages=100)
termination = text_mention_termination

# Configure selector prompt
selector_prompt = """Select the most appropriate agent to continue this task. Follow these rules strictly:

1. FIRST analyze the most recent messages in the conversation history
2. THEN select the next agent based on these precise criteria:
   
   Select browser_agent ONLY when:
     * The planner_agent has just provided a specific "next_step" instruction
     * A browser action needs to be executed (navigate, click, type, check DOM)
     * The previous message explicitly delegates a task to the browser_agent
   
   Select planner_agent when:
     * The conversation is just starting (first message in the thread)
     * The browser_agent has just completed an action and returned information
     * The browser_agent has encountered an error or needs guidance
     * A step has been completed and new planning is required
     * The browser_agent has ended its message with "##TERMINATE TASK##"

3. ENSURE proper turn-taking between the agents to maintain workflow
4. At turn 1, planner agent should be the first one to be selected always to layout the complete plan.
5. If the planner agent is stuck with captcha or verification, hand it over to the user to complete.
6. When the transaction is complete, handoff to the browser agent to finalize.
6. PRIORITIZE task completion over strict alternation

Current conversation context:
{history}

Available agents: {participants}

Your response must ONLY contain the name of ONE agent from {participants}, with no additional text or explanation.
"""

# Initialize team with all agents
team = SelectorGroupChat(
    [planner_agent, browser_agent, user_proxy_agent],
    model_client=model_client,
    termination_condition=termination,
    selector_prompt=selector_prompt,
    allow_repeated_speaker=True
)