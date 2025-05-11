from typing import Annotated, Dict, Optional, Any
from playwright_helper.playwright_manager import PlaywrightManager
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Playwright manager
playwright_manager = PlaywrightManager(headless=False)

async def initialize_browser(
    headless: Annotated[bool, "Whether to run browser in headless mode"] = False
) -> Annotated[Dict[str, str], "Initialization status"]:
    """Initialize the browser instance.
    
    Args:
        headless (bool): Whether to run the browser in headless mode
        
    Returns:
        Dict[str, str]: Dictionary containing status and message
    """
    try:
        await playwright_manager.initialize()
        logger.info("Browser initialized successfully")
        return {"status": "success", "message": "Browser initialized successfully"}
    except Exception as e:
        logger.error(f"Failed to initialize browser: {str(e)}")
        return {"status": "error", "message": str(e)}

async def navigate_to_url(
    url: Annotated[str, "The URL to navigate to"],
    timeout: Annotated[int, "Timeout in milliseconds"] = 5000
) -> Annotated[Dict[str, str], "Navigation status"]:
    """Navigate to the specified URL.
    
    Args:
        url (str): The URL to navigate to
        timeout (int): Timeout in milliseconds
        
    Returns:
        Dict[str, str]: Dictionary containing status and message/url
    """
    try:
        result = await playwright_manager.goto_url(url, timeout)
        logger.info(f"Navigation to {url} completed with status: {result['status']}")
        return result
    except Exception as e:
        logger.error(f"Failed to navigate to {url}: {str(e)}")
        return {"status": "error", "message": str(e)}

async def get_current_url() -> Annotated[Dict[str, str], "Current URL status"]:
    """Get the current URL of the page.
    
    Returns:
        Dict[str, str]: Dictionary containing status and current URL
    """
    try:
        current_url = playwright_manager.page.url
        logger.info(f"Retrieved current URL: {current_url}")
        return {"status": "success", "current_url": current_url}
    except Exception as e:
        logger.error(f"Failed to get current URL: {str(e)}")
        return {"status": "error", "message": str(e)}

async def get_page_dom() -> Annotated[Dict[str, Any], "Current page DOM representation"]:
    """Get the current page's DOM representation with mmid attributes.
    
    Returns:
        Dict[str, Any]: Dictionary containing status and DOM data
    """
    try:
        result = await playwright_manager.get_clean_dom_representation()
        logger.info("Successfully retrieved page DOM")
        return result
    except Exception as e:
        logger.error(f"Failed to get page DOM: {str(e)}")
        return {"status": "error", "message": str(e)}

async def click_element(
    mmid: Annotated[str, "The mmid attribute of element to click"],
    wait_before_execution: Annotated[int, "Milliseconds to wait before clicking"] = 0
) -> Annotated[Dict[str, str], "Click action status"]:
    """Click an element identified by its mmid attribute.
    
    Args:
        mmid (str): The mmid attribute of the element to click
        wait_before_execution (int): Milliseconds to wait before clicking
        
    Returns:
        Dict[str, str]: Dictionary containing status and message
    """
    try:
        result = await playwright_manager.click(mmid, wait_before_execution)
        logger.info(f"Click action completed for mmid {mmid}")
        return result
    except Exception as e:
        logger.error(f"Failed to click element with mmid {mmid}: {str(e)}")
        return {"status": "error", "message": str(e)}

async def type_text(
    mmid: Annotated[str, "The mmid attribute of input element"],
    content: Annotated[str, "Text content to type"]
) -> Annotated[Dict[str, str], "Type action status"]:
    """Type text into an input field identified by mmid.
    
    Args:
        mmid (str): The mmid attribute of the input element
        content (str): Text content to type
        
    Returns:
        Dict[str, str]: Dictionary containing status and message
    """
    try:
        result = await playwright_manager.type(mmid, content)
        logger.info(f"Text typing completed for mmid {mmid}")
        return result
    except Exception as e:
        logger.error(f"Failed to type text for mmid {mmid}: {str(e)}")
        return {"status": "error", "message": str(e)}

async def text_and_click(
    text_element_mmid: Annotated[str, "mmid of text input element"],
    text_to_enter: Annotated[str, "Text to enter"],
    click_element_mmid: Annotated[str, "mmid of element to click after typing"],
    wait_before_click: Annotated[int, "Milliseconds to wait before clicking"] = 0
) -> Annotated[Dict[str, str], "Action status"]:
    """Combined action: enter text and click another element.
    
    Args:
        text_element_mmid (str): mmid of the text input element
        text_to_enter (str): Text to enter
        click_element_mmid (str): mmid of the element to click
        wait_before_click (int): Milliseconds to wait before clicking
        
    Returns:
        Dict[str, str]: Dictionary containing status and message
    """
    try:
        result = await playwright_manager.enter_text_and_click(
            text_element_mmid, text_to_enter, click_element_mmid, wait_before_click
        )
        logger.info("Text and click action completed successfully")
        return result
    except Exception as e:
        logger.error(f"Failed to perform text and click action: {str(e)}")
        return {"status": "error", "message": str(e)}

async def close_browser() -> Annotated[Dict[str, str], "Shutdown status"]:
    """Close the browser and cleanup resources.
    
    Returns:
        Dict[str, str]: Dictionary containing status and message
    """
    try:
        await playwright_manager.close()
        logger.info("Browser closed successfully")
        return {"status": "success", "message": "Browser closed"}
    except Exception as e:
        logger.error(f"Failed to close browser: {str(e)}")
        return {"status": "error", "message": str(e)}

async def press_enter() -> Annotated[Dict[str, str], "Enter key press status"]:
    """Press the Enter key on the keyboard.
    
    Returns:
        Dict[str, str]: Dictionary containing status and message
    """
    try:
        result = await playwright_manager.enter()
        logger.info("Enter key pressed successfully")
        return result
    except Exception as e:
        logger.error(f"Failed to press Enter key: {str(e)}")
        return {"status": "error", "message": str(e)}