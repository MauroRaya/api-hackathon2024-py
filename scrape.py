import time
import re
from bs4 import BeautifulSoup
from models import Evento, initialize_database, save_events, get_events, delete_all_events


urls = [
    {'santos': 'https://www.bilheteriaexpress.com.br/agendas/santos.html'},
    {'praia-grande': 'https://www.bilheteriaexpress.com.br/agendas/praia-grande-sp.html'}
]
event_page_urls = []


def scroll_down_page(driver, waitContentLoad = 2):
    last_height = driver.execute_script('return document.body.scrollHeight')
    print(f'Altura da pagina: {last_height}')

    while True:
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        time.sleep(waitContentLoad)

        new_height = driver.execute_script('return document.body.scrollHeight')
        print(f'Nova altura da pagina: {new_height}')

        if (new_height == last_height):
            print('Scrollagem acabou')
            break

        last_height = new_height


def get_page_elements(driver, selector):
    scroll_down_page(driver)
    soup = BeautifulSoup(driver.page_source, features='lxml')

    elements = soup.select(selector)

    if not elements or len(elements) == 0:
        print(f'Não foi possivel encontrar elementos do seletor {selector}')
        return []
    
    return elements


def scrape_events_url(city_name, city_url, events_elements):
    print(f'Iniciando raspagem da cidade de {city_name}')

    for i, element in enumerate(events_elements):
        event_url = element.get('href')

        if not event_url:
            continue
            
        event_page_urls.append((event_url, city_url))
        print(f'URL EVENTO {i+1}: {event_url}')

    print(f'Raspagem finalizada da cidade de {city_name}')


def extract_city(localidade):
    match = re.search(r',\s*([A-Za-z\s]+)\s*-\s*[A-Z]{2}', localidade)
    return match.group(1).strip() if match else 'N/A'


def extract_prices(element):
    match = re.search(r'Ingressos a partir de R\$ ([\d,.]+)\s*à\s*([\d,.]+)', element)
    if match:
        preco_minimo = match.group(1).replace('.', '').replace(',', '.')
        preco_maximo = match.group(2).replace('.', '').replace(',', '.')
        return preco_minimo, preco_maximo
    return 'N/A', 'N/A'


def scrape_event_data(driver, url, link_origem):
    nome_element = driver.find_element("css selector", ".price-review > p:nth-child(1)")
    data_element = driver.find_element("css selector", "tr:nth-child(3) > td:nth-child(2)")
    localidade_element = driver.find_element("css selector", "td:nth-child(2) > p:nth-child(2)")
    precos_element = driver.find_element("css selector", "p:nth-child(1) > strong:nth-child(1)")
    descricao_element = driver.find_element("css selector", "tr:nth-child(1) > td:nth-child(2)")
    imagem_element = driver.find_element("css selector", "#image")

    nome = nome_element.text.strip() if nome_element else 'N/A'
    data = data_element.text.strip() if data_element else 'N/A'
    localidade = localidade_element.text.strip() if localidade_element else 'N/A'
    cidade = extract_city(localidade)

    precos_text = precos_element.text.strip() if precos_element else 'N/A'
    preco_minimo, preco_maximo = extract_prices(precos_text)

    descricao = descricao_element.text.strip() if descricao_element else 'N/A'
    imagem = imagem_element.get_attribute('src') if imagem_element else 'N/A'

    novoEvento = Evento(
        nome=nome,
        data=data,
        localidade=localidade,
        cidade=cidade,
        preco_minimo=preco_minimo,
        preco_maximo=preco_maximo,
        descricao=descricao,
        link_compra=url,
        link_origem=link_origem,
        imagem=imagem
    )

    save_events(novoEvento)


def scrape_all_events(driver):
    initialize_database()
    delete_all_events()

    # Iterar e pegar todas as URLs da pagina dos eventos de cada cidade
    for dic in urls:
        for city_name, city_url in dic.items():
            driver.get(city_url)
            events_elements = get_page_elements(driver, 'h2.product-name > a')
            scrape_events_url(city_name, city_url, events_elements)

    # Iterar as URLs coletadas, e raspar os dados de cada evento
    for event_url, city_url in event_page_urls:
        driver.get(event_url)
        scrape_event_data(driver, event_url, city_url)

    print('Raspagem dos eventos concluida com sucesso')