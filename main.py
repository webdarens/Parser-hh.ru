import requests
import csv
from bs4 import BeautifulSoup

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'priority': 'u=0, i',
    'referer': 'https://novosibirsk.hh.ru/search/vacancy?text=python&area=4&hhtmFrom=main&hhtmFromLabel=vacancy_search_line',
    'sec-ch-ua': '"Chromium";v="124", "Microsoft Edge";v="124", "Not-A.Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0',
}

params = {
    'ored_clusters': 'true',
    'hhtmFrom': 'vacancy_search_list',
    'hhtmFromLabel': 'vacancy_search_line',
    'search_field': [
        'name',
        'company_name',
        'description',
    ],
    'text': 'python стажер',
    'enable_snippets': 'false',
    'L_save_area': 'true',
}

lst = []

#реализация получения макс.количества страниц на сайте
hh_request = requests.get('https://novosibirsk.hh.ru/search/vacancy?L_save_area=true&text=python+%D1%81%D1%82%D0%B0%D0%B6%D0%B5%D1%80&excluded_text=&salary=&currency_code=RUR&experience=doesNotMatter&order_by=relevance&search_period=0&items_on_page=20', params=params, headers=headers)
hh_soup = BeautifulSoup(hh_request.text, 'html.parser')
hh_paginator = hh_soup.find_all('span', class_ = 'pager-item-not-in-short-range')
for page in hh_paginator:
    lst.append(int(page.find('a').text)) #lst[-1] max page
#--------------------

seen_companies = set() #hash-set чтобы компании не повторялись, в конце добавляются  вакансии с не указанной зп 

#url вакансий с указанной зп 
url = 'https://novosibirsk.hh.ru/search/vacancy?L_save_area=true&items_on_page=20&search_field=name&search_field=company_name&search_field=description&enable_snippets=false&experience=noExperience&text=python+%D1%81%D1%82%D0%B0%D0%B6%D0%B5%D1%80&only_with_salary=true'


#loop input 
ask = input('1 - Показать все вакансии со стажировкой c указанной и не указанной ЗП\nВаш выбор:')
while ask != '1':
    print("Некорректный выбор, пожалуйста, введите 1")
    ask = input('1 - Показать все вакансии со стажировкой, c указанной и не указанной ЗП\nВаш выбор:')
    
#запись данных в csv файл
with open('vacancies.csv', mode='w', encoding='utf-8', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Компания', 'Зарплата', 'Организация', 'Место', 'Ссылка'])

    if ask == '1':
        print('Процесс может занять немного времени...[+]')
        for page in range(lst[-1]): 
            #сбор вакансий с указанной зп 
            result = requests.get(f'{url}&page={page}',  headers=headers) 
            soup = BeautifulSoup(result.text, 'html.parser')
            #компания (results) 
            results = soup.find_all('span', class_='serp-item__title-link serp-item__title')
            #Организация
            ceos = soup.find_all('div', class_='vacancy-serp-item__meta-info-company')
            #Место
            place = soup.find_all('div', {'data-qa': 'vacancy-serp__vacancy-address', 'class': 'bloko-text'})
            #ссылки
            links = soup.find_all('a', {'class': 'bloko-button bloko-button_kind-success bloko-button_scale-small', 'data-qa': 'vacancy-serp__vacancy_response'})
            #ЗП
            cost = soup.find_all('span', {'class': 'bloko-header-section-2', 'data-qa': 'vacancy-serp__vacancy-compensation'})

            comp = []
            admin = []
            placesList = []
            linksList = []
            costList = []
            
            for c in cost:
                costList.append(c.text.strip())
            for link in links:
                href = link.get('href') #получение href ссылок в links
                modified_href = href.split('&hhtmFrom')[0]  # Remove the part after '&hhtmFrom'
                full_href = f'https://novosibirsk.hh.ru{modified_href}' #modifed url without HHtmFrom
                linksList.append(full_href) 

            for p in place:
                placesList.append(p.text.strip())

            for r in results:
                comp.append(r.text)

            for ceo in ceos:
                admin.append(ceo.text)

            for i in range(len(costList)): #реализация вакансий без дубликатов
                company = comp[i] 
                if company in seen_companies: 
                    continue 
                else:
                    seen_companies.add(company)
                    writer.writerow([company, costList[i], admin[i], placesList[i], linksList[i]]) #добавление в таблицу

            if not results:
                print('Идёт обработка второй части вакансий...[+]')
                break
                
        for page in range(lst[-1]):
            #все ссылки на вакансии без зп
            allurls = 'https://novosibirsk.hh.ru/search/vacancy?L_save_area=true&items_on_page=20&search_field=name&search_field=company_name&search_field=description&enable_snippets=false&experience=noExperience&text=python+%D1%81%D1%82%D0%B0%D0%B6%D0%B5%D1%80'
            result = requests.get(f'{allurls}&page={page}', headers=headers)
            soup = BeautifulSoup(result.text, 'html.parser')
            #results это имя компании
            results = soup.find_all('span', class_='serp-item__title-link serp-item__title')
            ceos = soup.find_all('div', class_='vacancy-serp-item__meta-info-company')
            place = soup.find_all('div', {'data-qa': 'vacancy-serp__vacancy-address', 'class': 'bloko-text'})
            links = soup.find_all('a', {'class': 'bloko-button bloko-button_kind-success bloko-button_scale-small', 'data-qa': 'vacancy-serp__vacancy_response'})

            comp = []
            admin = []
            placesList = []
            linksList = []

            for link in links:
                href = link.get('href') #получение href ссылок в links
                modified_href = href.split('&hhtmFrom')[0]  # Remove the part after '&hhtmFrom'
                full_href = f'https://novosibirsk.hh.ru{modified_href}' #modifed url without HHtmFrom
                linksList.append(full_href)

            for p in place:
                placesList.append(p.text.strip())

            for r in results:
                comp.append(r.text)

            for ceo in ceos:
                admin.append(ceo.text)

            for i in range(len(admin)): #Реализация добавления всех остальных ссылок без ЗП, всё в одном hash-set
                company = comp[i]
                if company in seen_companies: 
                    continue
                else:
                    seen_companies.add(company)
                    writer.writerow([company, 'Не указано', admin[i], placesList[i], linksList[i]]) #добавление в таблицу

            if not results:
                print('Загрузка в csv файл  заверешена! Посмотрите его в папке где и main.py')
                break
