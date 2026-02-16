import sys
from playwright.sync_api import sync_playwright

def open_whatsapp_web():
    print('WhatsApp Web is opening...')
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto('https://web.whatsapp.com')
            print('WhatsApp Web opened. Please scan the QR code with your phone.')
            input('Press Enter after scanning the QR code to close the browser...')
            browser.close()
            print('Browser closed successfully.')
    except Exception as e:
        print(f'Error: {e}')
        print('Trying alternative method...')
        # Alternative method
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto('https://web.whatsapp.com')
            print('WhatsApp Web opened. Please scan the QR code with your phone.')
            input('Press Enter after scanning the QR code to close the browser...')
            browser.close()
            print('Browser closed successfully.')

if __name__ == "__main__":
    open_whatsapp_web()