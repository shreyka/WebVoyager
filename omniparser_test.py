import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from OmniParser.utils import get_element_rect_from_image
from PIL import Image, ImageDraw
def test_element_detection(url: str, headless: bool = False):
    """
    Test the element detection function in a scenario similar to run.py
    
    Args:
        url: Website URL to test
        headless: Whether to run browser in headless mode
    """
    print(f"\nTesting element detection on {url}")
    
    # Setup Chrome options (similar to run.py's driver_config)
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless")
        options.add_argument(
            "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/119.0.0.0 Safari/537.36"
        )
    
    # Initialize driver
    print("Initializing Chrome driver...")
    driver = webdriver.Chrome(options=options)
    
    try:
        # Set window size (same as run.py)
        driver.set_window_size(1024, 768)
        
        # Navigate to URL
        print(f"Navigating to {url}")
        driver.get(url)
        time.sleep(5)  # Wait for page load
        
        try:
            driver.find_element(By.TAG_NAME, 'body').click()
        except:
            print("Could not click body - continuing...")
            pass
            
        # Create results directory with timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        results_dir = os.path.join("omniparser_test_results", timestamp)
        os.makedirs(results_dir, exist_ok=True)
        
        # Take screenshot and process
        print("Taking screenshot and detecting elements...")
        before_screenshot_path = os.path.join(results_dir, "before_test_screenshot.png")
        driver.save_screenshot(before_screenshot_path)
        
        # Process with OmniParser
        print("Processing with OmniParser...")
        rects, elements, elements_text = get_element_rect_from_image(
            before_screenshot_path,
            fix_color=True
        )
        # Apply rects to image then save to after_screenshot_path
        from PIL import ImageDraw

        # Open the screenshot image
        image = Image.open(before_screenshot_path)
        draw = ImageDraw.Draw(image)

        # Draw rectangles on the image
        for rect in rects:
            draw.rectangle(rect, outline="red", width=2)

        # Save after processing screenshot
        after_screenshot_path = os.path.join(results_dir, "after_test_screenshot.png")
        image.save(after_screenshot_path)
        
        # Print results
        print("\nDetection Results:")
        print(f"Number of interactive elements detected: {len(elements)}")
        print("\nElement Descriptions:")
        for element_text in elements_text.split('\t'):
            print(element_text)

        return rects, elements, elements_text
        
    finally:
        print("\nClosing browser...")
        driver.quit()

if __name__ == "__main__":
    # Example usage
    test_urls = [
        "https://arxiv.org",
        # "https://github.com",
        # "https://www.google.com"
    ]
    
    for url in test_urls:
        try:
            rects, elements, text = test_element_detection(url)
            print(f"\nSuccessfully tested {url}")
        except Exception as e:
            print(f"\nError testing {url}: {e}")
        print("-" * 80)
