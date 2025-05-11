from playwright.async_api import async_playwright, Browser, BrowserContext, Page
import json
from typing import Dict, List, Any, Optional
import streamlit as st
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PlaywrightManager:
    """A manager class for handling Playwright browser automation.
    
    This class provides methods for browser initialization, navigation, and interaction
    with web elements using Playwright's async API.
    
    Attributes:
        headless (bool): Whether to run the browser in headless mode
        playwright: Playwright instance
        browser: Browser instance
        context: Browser context
        page: Page instance
        mmid_counter (int): Counter for generating unique mmid attributes
    """
    
    def __init__(self, headless: bool = False):
        """Initialize the PlaywrightManager.
        
        Args:
            headless (bool): Whether to run the browser in headless mode
        """
        self.headless = headless
        self.playwright: Optional[async_playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.mmid_counter = 1

    async def initialize(self) -> None:
        """Initialize the Playwright browser instance.
        
        Raises:
            Exception: If browser initialization fails
        """
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=self.headless)
            self.context = await self.browser.new_context()
            self.page = await self.context.new_page()
            logger.info("Browser initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize browser: {str(e)}")
            raise

    async def goto_url(self, url: str, timeout: int = 30000) -> Dict[str, Any]:
        """Navigate to a specified URL.
        
        Args:
            url (str): The URL to navigate to
            timeout (int): Navigation timeout in milliseconds
            
        Returns:
            Dict[str, Any]: Status and message of the navigation attempt
        """
        try:
            await self.page.goto(url, timeout=timeout)
            logger.info(f"Successfully navigated to {url}")
            return {"status": "success", "message": f"Successfully navigated to {url}", "url": url}
        except Exception as e:
            logger.error(f"Failed to navigate to {url}: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def get_current_url(self) -> str:
        """Get the current page URL.
        
        Returns:
            str: Current page URL
        """
        return self.page.url

    async def get_clean_dom_representation(self) -> Dict[str, Any]:
        """Get a clean DOM representation of the current page.
        
        Returns:
            Dict[str, Any]: DOM representation with status and message
        """
        try:
            url = self.page.url
            await self.page.wait_for_url(url=url)
            with open("playwright_helper/dom_parser.js", "r") as f:
                dom_script = f.read()
            dom = await self.page.evaluate(f"({dom_script})({self.mmid_counter})")
            
            self.mmid_counter = dom.get('mmid_counter', self.mmid_counter + 1000)
            
            return {
                "current_page_dom": dom,
                "status": "success",
                "message": "Current page dom retrieved successfully"
            }
             
        except Exception as e:
            logger.error(f"Failed to get DOM representation: {str(e)}")
            return {
                "current_page_dom": None,
                "status": "error",
                "message": str(e)
            }

    async def click(self, mmid: str, wait_before_execution: int = 0) -> Dict[str, Any]:
        """Click an element identified by its mmid attribute.
        
        Args:
            mmid (str): The mmid attribute of the element to click
            wait_before_execution (int): Milliseconds to wait before clicking
            
        Returns:
            Dict[str, Any]: Status and message of the click action
        """
        try:
            if wait_before_execution:
                await self.page.wait_for_timeout(wait_before_execution)
            await self.page.click(f'[mmid="{mmid}"]')
            logger.info(f"Successfully clicked element with mmid: {mmid}")
            return {"status": "success", "message": f"Successfully clicked element with mmid: {mmid}"}
        except Exception as e:
            logger.error(f"Failed to click element with mmid {mmid}: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def type(self, mmid: str, content: str) -> Dict[str, Any]:
        """Type content into an input field identified by mmid.
        
        Args:
            mmid (str): The mmid attribute of the input element
            content (str): The content to type
            
        Returns:
            Dict[str, Any]: Status and message of the type action
        """
        try:
            original_content = content
            if content == "!USERNAME!":
                content = st.session_state.credentials.get("username", "")
            elif content == "!PASSWORD!":
                content = st.session_state.credentials.get("password", "")
            await self.page.fill(f'[mmid="{mmid}"]', content)
            logger.info(f"Successfully typed {original_content} into element with mmid: {mmid}")
            return {"status": "success", "message": f"Successfully typed {original_content} into element with mmid: {mmid}"}
        except Exception as e:
            logger.error(f"Failed to type into element with mmid {mmid}: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def enter_text_and_click(self, text_element_mmid: str, text_to_enter: str, 
                           click_element_mmid: str, wait_before_click_execution: int = 0) -> Dict[str, Any]:
        """Enter text and click another element in sequence.
        
        Args:
            text_element_mmid (str): mmid of the text input element
            text_to_enter (str): Text to enter
            click_element_mmid (str): mmid of the element to click
            wait_before_click_execution (int): Milliseconds to wait before clicking
            
        Returns:
            Dict[str, Any]: Status and message of the combined action
        """
        try:
            await self.page.fill(f'[mmid="{text_element_mmid}"]', text_to_enter)
            if wait_before_click_execution:
                await self.page.wait_for_timeout(wait_before_click_execution)
            await self.page.click(f'[mmid="{click_element_mmid}"]')
            logger.info(f"Successfully entered text and clicked elements")
            return {"status": "success", "message": f"Successfully entered {text_to_enter} to mmid {text_element_mmid} and clicked element with mmid: {click_element_mmid}"}
        except Exception as e:
            logger.error(f"Failed to enter text and click: {str(e)}")
            return {"status": "error", "message": str(e)}
        
    async def enter(self) -> Dict[str, Any]:
        """Press the Enter key.
        
        Returns:
            Dict[str, Any]: Status and message of the Enter key press
        """
        try:
            await self.page.keyboard.press("Enter")
            logger.info("Enter key pressed successfully")
            return {"status": "success", "message": "Enter key pressed"}
        except Exception as e:
            logger.error(f"Failed to press Enter key: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def close(self) -> None:
        """Close the browser and cleanup resources."""
        try:
            await self.context.close()
            await self.browser.close()
            await self.playwright.stop()
            logger.info("Browser closed successfully")
        except Exception as e:
            logger.error(f"Error while closing browser: {str(e)}")
            raise
