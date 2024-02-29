from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


class RiskFreeRateDataSet:
    def __init__(self, rate: Optional[float] = None):
        self._rate = rate

    @property
    def rate(self):
        return self._get_rate()

    def _get_rate(self):
        if self._rate is None:
            self._rate = self.scrape_risk_free_rate()
        return self._rate

    @staticmethod
    def scrape_risk_free_rate():
        # Setup Chrome options
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")  # Runs Chrome in headless mode.
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Initialize the WebDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        try:
            URL = "https://ycharts.com/indicators/10_year_treasury_rate"
            XPATH = "/html/body/main/div/div[2]/div/div/div[2]"
            
            driver.get(URL)
            risk_free_rate_element = driver.find_element(By.XPATH, XPATH)
            risk_free_rate = risk_free_rate_element.text
            risk_free_rate = float(risk_free_rate.split()[0].rstrip("%")) / 100
            return risk_free_rate
        except Exception as e:
            print(f"Error scraping risk-free rate: {e}")
            return None
        finally:
            driver.quit()