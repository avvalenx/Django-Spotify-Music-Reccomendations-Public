from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time
import datetime

PATH = 'chromedriver.exe'
EMAIL = 'mkzazqevqowtxkdbsa@tpwlb.com'
PASSWORD = 'Musicrectesting'

class MusicRecTestCase(StaticLiveServerTestCase):
    port = 8000

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver()

    @classmethod
    def tearDownClass(cls):
            cls.selenium.quit()
            super().tearDownClass()

    def test_music_rec(self):
        # create website account
        self.selenium.get(self.live_server_url + '/signup')
        WebDriverWait(self.selenium, 5).until(EC.presence_of_element_located((By.NAME, 'email'))).send_keys(EMAIL)
        WebDriverWait(self.selenium, 5).until(EC.presence_of_element_located((By.NAME, 'password'))).send_keys(PASSWORD)
        WebDriverWait(self.selenium, 5).until(EC.presence_of_element_located((By.NAME, 'confirm_password'))).send_keys(PASSWORD)
        WebDriverWait(self.selenium, 5).until(EC.presence_of_element_located((By.ID, 'submit-button'))).click()
        #check that the spotify login page is returned
        self.assertEqual(self.selenium.title, 'Login - Spotify')

        # connect spotify account
        WebDriverWait(self.selenium, 5).until(EC.presence_of_element_located((By.ID, 'login-username'))).send_keys(EMAIL)
        WebDriverWait(self.selenium, 5).until(EC.presence_of_element_located((By.ID, 'login-password'))).send_keys(PASSWORD)
        WebDriverWait(self.selenium, 5).until(EC.presence_of_element_located((By.ID, 'login-button'))).click()
        #check that login is successful
        WebDriverWait(self.selenium, 5).until(lambda d: d.current_url[:37] == 'http://localhost:8000/spotify_success')
        self.assertEqual(self.selenium.current_url[:37], 'http://localhost:8000/spotify_success')
        WebDriverWait(self.selenium, 5).until(EC.presence_of_element_located((By.ID, 'back'))).click()

        # test that account created can be logged into
        WebDriverWait(self.selenium, 5).until(EC.presence_of_element_located((By.NAME, 'logout'))).click()
        WebDriverWait(self.selenium, 5).until(EC.presence_of_element_located((By.NAME, 'login'))).click()
        WebDriverWait(self.selenium, 5).until(EC.presence_of_element_located((By.NAME, 'email'))).send_keys(EMAIL)
        WebDriverWait(self.selenium, 5).until(EC.presence_of_element_located((By.NAME, 'password'))).send_keys(PASSWORD)
        WebDriverWait(self.selenium, 5).until(EC.presence_of_element_located((By.ID, 'submit-button'))).click()
        self.assertEqual(self.selenium.title, 'Success')
        WebDriverWait(self.selenium, 5).until(EC.presence_of_element_located((By.ID, 'back'))).click()
        WebDriverWait(self.selenium, 5).until(EC.presence_of_element_located((By.NAME, 'setup'))).click()

        # test that a song can be added
        WebDriverWait(self.selenium, 5).until(EC.presence_of_element_located((By.ID, 'songs'))).click()
        WebDriverWait(self.selenium, 5).until(EC.presence_of_element_located((By.ID, 'search'))).send_keys('test')
        WebDriverWait(self.selenium, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'search-button'))).click()
        WebDriverWait(self.selenium, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="songs"]/label[1]'))).click()
        WebDriverWait(self.selenium, 5).until(EC.presence_of_element_located((By.ID, 'submit-button'))).click()
        # check that the song was added to the ui
        self.assertIsNotNone(self.selenium.find_element(By.XPATH, '/html/body/div[1]/label'))

        # test that an artist can be added
        WebDriverWait(self.selenium, 5).until(EC.presence_of_element_located((By.ID, 'artists'))).click()
        WebDriverWait(self.selenium, 5).until(EC.presence_of_element_located((By.ID, 'search'))).send_keys('test')
        WebDriverWait(self.selenium, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'search-button'))).click()
        WebDriverWait(self.selenium, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="artists"]/label[1]'))).click()
        WebDriverWait(self.selenium, 5).until(EC.presence_of_element_located((By.ID, 'submit-button'))).click()
        # check that the artist was added to the ui
        self.assertIsNotNone(self.selenium.find_element(By.XPATH, '/html/body/div[2]/label'))

        # test that a genre can be added
        WebDriverWait(self.selenium, 5).until(EC.presence_of_element_located((By.ID, 'genres'))).click()
        WebDriverWait(self.selenium, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="genres"]/label[1]'))).click()
        WebDriverWait(self.selenium, 5).until(EC.presence_of_element_located((By.ID, 'submit-button'))).click()
        # check that the artist was added to the ui
        self.assertIsNotNone(self.selenium.find_element(By.XPATH, '/html/body/div[3]/label[1]'))
        
        # test adding to playlist
        WebDriverWait(self.selenium, 5).until(EC.presence_of_element_located((By.ID, 'submit'))).click()
        self.assertHTMLEqual(self.selenium.current_url, 'http://localhost:8000/parameters')
        WebDriverWait(self.selenium, 5).until(EC.presence_of_element_located((By.ID, 'submit-button'))).click()
        self.assertHTMLEqual(self.selenium.current_url, 'http://localhost:8000/submit')
        WebDriverWait(self.selenium, 5).until(EC.presence_of_element_located((By.NAME, 'playlist'))).send_keys(str(datetime.datetime.now()) + 'test_playlist')
        WebDriverWait(self.selenium, 5).until(EC.presence_of_element_located((By.ID, 'submit-button'))).click()
        self.assertEqual(self.selenium.current_url, 'http://localhost:8000/playlist')
        self.assertInHTML('<h1>Playlist created successfully!</h1>', self.selenium.page_source)