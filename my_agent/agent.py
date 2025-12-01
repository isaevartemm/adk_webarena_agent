from google.adk.agents.llm_agent import Agent
import asyncio
import logging
import markdownify
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Page, Browser, TimeoutError as PlaywrightTimeoutError


# ============================================================
# LOGGING SETUP
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


# ============================================================
# GLOBAL STATE HOLDER
# ============================================================
class WebAgentState:
    """
    Global state container for browser and page instances.

    This object allows persistent browsing sessions by storing
    the Playwright browser and active page. All high-level functions
    (`page_description`, `perform_action`) operate on this state.
    """

    browser: Optional[Browser] = None
    page: Optional[Page] = None
    initialized: bool = False


STATE = WebAgentState()


async def init_browser():
    """
    Initializes the global browser and page objects if not already active.

    Logs all important initialization steps.

    Returns:
        Page: The active browser page instance.
    """
    if STATE.initialized:
        logger.info("Browser already initialized; reusing existing page.")
        return STATE.page

    logger.info("Starting Playwright and launching browser...")
    p = await async_playwright().start()
    browser = await p.chromium.launch(headless=True)
    page = await browser.new_page()

    STATE.browser = browser
    STATE.page = page
    STATE.initialized = True

    logger.info("Browser initialized successfully.")
    return page


# ============================================================
# ACTION EXTRACTION
# ============================================================
def extract_actions(html: str) -> List[dict]:
    """
    Extracts actionable UI items from HTML.

    Logs count and types of extracted elements.

    Args:
        html (str): The raw HTML source of the page.

    Returns:
        List[dict]: A list of structured action descriptors.
    """
    logger.info("Extracting actionable items from HTML...")
    soup = BeautifulSoup(html, "html.parser")
    actions = []

    # Buttons
    buttons = soup.find_all("button")
    logger.info(f"Found {len(buttons)} <button> elements.")
    for b in buttons:
        actions.append({
            "type": "button",
            "text": b.get_text(strip=True),
            "id": b.get("id"),
            "class": " ".join(b.get("class", [])) if b.get("class") else None,
        })

    # Links
    links = soup.find_all("a")
    logger.info(f"Found {len(links)} <a> link elements.")
    for a in links:
        actions.append({
            "type": "link",
            "text": a.get_text(strip=True),
            "href": a.get("href"),
        })

    # role="button"
    role_buttons = soup.find_all(attrs={"role": "button"})
    logger.info(f"Found {len(role_buttons)} role=\"button\" elements.")
    for el in role_buttons:
        actions.append({
            "type": "role-button",
            "text": el.get_text(strip=True),
            "id": el.get("id"),
            "class": " ".join(el.get("class", [])) if el.get("class") else None,
        })

    logger.info(f"Total actionable items extracted: {len(actions)}")
    return actions


def render_actions_html(actions: List[dict]) -> str:
    """
    Converts extracted actions into a readable HTML list.

    Args:
        actions (List[dict]): The structured action descriptors.

    Returns:
        str: HTML snippet summarizing actionable elements.
    """
    logger.info(f"Rendering {len(actions)} actions into HTML summary.")

    if not actions:
        return "<h2>No actionable items detected.</h2>"

    html = ["<h2>Detected Actions</h2>", "<ul>"]

    for item in actions:
        if item["type"] == "link":
            html.append(
                f"<li><b>Link:</b> {item['text']} (href: {item.get('href','')})</li>"
            )
        else:
            html.append(
                f"<li><b>{item['type'].title()}:</b> {item['text']} "
                f"(id: {item.get('id')}, class: {item.get('class')})</li>"
            )

    html.append("</ul>")
    return "\n".join(html)


# ============================================================
# PAGE DESCRIPTION
# ============================================================
async def page_description(url: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieves the current page state, or navigates to a URL if provided.

    Logs navigation, scraping, markdown conversion, and action extraction.

    Args:
        url (str, optional): If provided, navigates to this URL before scraping.

    Returns:
        dict: Structured page description.
    """
    page = await init_browser()

    if url:
        logger.info(f"Navigating to URL: {url}")
        await page.goto(url, wait_until="networkidle")
        logger.info("Page load complete.")

    logger.info("Fetching page content...")
    html = await page.content()

    logger.info("Converting page HTML to markdown...")
    markdown_text = markdownify.markdownify(html, heading_style="ATX")

    actions = extract_actions(html)

    logger.info("Attaching rendered actions to HTML output.")
    enhanced_html = html + "\n\n<!-- ACTION LIST -->\n" + render_actions_html(actions)

    logger.info("Page description ready.")
    return {
        "url": page.url,
        "html": enhanced_html,
        "markdown": markdown_text,
        "actions": actions,
    }


# ============================================================
# ACTION EXECUTION
# ============================================================
async def perform_action(target: str) -> Dict[str, Any]:
    """
    Executes an action on the currently loaded page.

    Includes detailed logs about selection attempts and click success.

    Args:
        target (str): Identifier of the action to perform.

    Returns:
        dict: Updated page description.
    """
    page = await init_browser()

    logger.info(f"Attempting to perform action: '{target}'")

    clicked = False

    # CSS selectors
    try:
        if target.startswith("#") or target.startswith("."):
            logger.info(f"Trying CSS selector click: {target}")
            await page.click(target)
            clicked = True
    except PlaywrightTimeoutError:
        logger.warning("CSS selector click failed.")

    # ID
    if not clicked:
        try:
            logger.info(f"Trying ID click: #{target}")
            await page.click(f"#{target}")
            clicked = True
        except PlaywrightTimeoutError:
            logger.warning("ID click failed.")

    # Exact text
    if not clicked:
        try:
            logger.info(f"Trying exact text click: {target}")
            await page.get_by_text(target, exact=True).click()
            clicked = True
        except PlaywrightTimeoutError:
            logger.warning("Exact text click failed.")

    # Partial text
    if not clicked:
        try:
            logger.info(f"Trying partial text click: {target}")
            await page.get_by_text(target).click()
            clicked = True
        except PlaywrightTimeoutError:
            logger.warning("Partial text click failed.")

    # Href
    if not clicked:
        try:
            logger.info(f"Trying href click: a[href='{target}']")
            await page.click(f"a[href='{target}']")
            clicked = True
        except PlaywrightTimeoutError:
            logger.warning("Href click failed.")

    # role=button
    if not clicked:
        try:
            logger.info(f"Trying role='button' click: name={target}")
            await page.get_by_role("button", name=target).click()
            clicked = True
        except PlaywrightTimeoutError:
            logger.warning("Role-button click failed.")

    if not clicked:
        logger.error(f"ERROR: Could not perform action '{target}'.")
        return {
            "status": "error",
            "message": f"Could not execute action: {target}",
            "target": target
        }

    logger.info(f"Action '{target}' executed successfully.")
    try:
        await page.wait_for_load_state("networkidle", timeout=3000)
        logger.info("Page load/DOM update after action complete.")
    except Exception:
        logger.info("No page navigation occurred after action.")

    updated = await page_description()
    updated["status"] = "success"
    updated["action"] = target

    logger.info("Returning updated page state.")
    return updated


tools = [page_description, perform_action]

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='A helpful web-browsing assistant',
    instruction=(
        "Use page_description to inspect pages; "
        "choose an action from actionable items; "
        "use perform_action to interact with the page. "
        "The page state persists across calls."
    ),
    tools=tools
)
