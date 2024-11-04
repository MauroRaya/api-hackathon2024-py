from flask import Flask, jsonify
from flask_cors import CORS
from scrape import scrape_all_events
from models import get_events, delete_all_events
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import threading


app = Flask(__name__)
CORS(app)


chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

is_fetching = False

@app.route("/api/eventos", methods=['POST'])
def scrape():
    global is_fetching
    if is_fetching:
        return jsonify({ 'message': 'Raspagem já esta em progresso' }), 409
    
    def run_scraping():
        global is_fetching
        is_fetching = True
        try:
           print('Iniciando rotina de raspagem')
           scrape_all_events(driver)
           print('Raspagem dos dados dos eventos finalizada')
        except Exception as e:
            print(f'Ocorreu um erro durante a raspagem: {e}')
        finally:
            is_fetching = False
            

    threading.Thread(target=run_scraping).start()
    return jsonify({'message': 'Iniciando rotina de raspagem'}), 202


@app.route("/api/eventos", methods=['GET'])
def response_get_events():
    eventos = get_events()
    return jsonify({ 'data': eventos, 'isFetching': is_fetching })


@app.route("/api/eventos", methods=['DELETE'])
def response_delete_all_events():
    delete_all_events()
    return jsonify({ 'message': 'Eventos deletados com sucesso' })


if __name__ == '__main__':
    app.run(debug=True)