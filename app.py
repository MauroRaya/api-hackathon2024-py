from flask import Flask, jsonify
from flask_cors import CORS
from scrape import scrape_all_events
from models import get_events, delete_all_events
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


app = Flask(__name__)
CORS(app)


chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)


@app.route("/api/eventos", methods=['POST'])
def scrape():
    scrape_all_events(driver)
    return jsonify('Eventos raspados com sucesso')


@app.route("/api/eventos", methods=['GET'])
def response_get_events():
    eventos = get_events()
    return jsonify(eventos)


@app.route("/api/eventos", methods=['DELETE'])
def response_delete_all_events():
    delete_all_events()
    return jsonify('Eventos deletados com sucesso')


if __name__ == '__main__':
    app.run(debug=True)