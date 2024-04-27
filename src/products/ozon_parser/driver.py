from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class BypassingAntibotChallengeChrome(webdriver.Chrome):
    BYPASS_ANTIBOT_CHALLENGE_JS_SCRIPT = """
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_JSON;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Object;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Proxy;
            """

    def __init__(self, *args, **kwargs):
        kwargs.pop("options")
        super().__init__(*args, **kwargs)
        self.options = Options()
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option("useAutomationExtension", False)
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_argument("--headless")
        self.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {"source": self.BYPASS_ANTIBOT_CHALLENGE_JS_SCRIPT},
        )
