from os import getenv
import chromedriver_binary
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException


def main():
    driver = init_driver()
    print('Chrome driver is initialized.')

    login(driver)
    print('Login succeeded.')

    results = fetch_problem_list(driver)
    print('All problems are fetched.')

    fetch_scores(results, driver)
    print('All scores are fetched')

    print('###########################################')
    print('############  START OUTPUT  ###############')
    print('###########################################')
    print_solved(results)
    print_unsolved(results)


def init_driver():
    options = webdriver.chrome.options.Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1200,800')
    return webdriver.Chrome(options=options)


def login(driver):
    email = getenv('PAIZA_EMAIL')
    password = getenv('PAIZA_PASSWORD')
    driver.get('https://paiza.jp/sign_in')
    mail_form = driver.find_element(by=By.ID, value='email')
    mail_form.send_keys(email)
    password_form = driver.find_element(by=By.ID, value='password')
    password_form.send_keys(password)
    password_form.submit()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'o-pc-header__icon'))
    )


def fetch_problem_list(driver):
    results = {}
    for target_rank in 'sabcd':
        driver.get('https://paiza.jp/challenges/ranks/' + target_rank)
        results[target_rank] = {}
        for i in driver.find_elements(by=By.CLASS_NAME, value='clearfix'):
            title_with_no = i.find_element(
                by=By.CLASS_NAME, value='problem-box__header__title'
            ).text
            no = title_with_no.split(':')[0]
            title = title_with_no.split(':')[1]
            try:
                rank = (
                    i.find_element(by=By.CLASS_NAME, value='problem-box__rank')
                    .text.replace('第', '')
                    .replace('位', '')
                )
            except NoSuchElementException:
                rank = '-'
            if (
                '再チャレンジする'
                not in i.find_element(
                    by=By.CLASS_NAME, value='problem-box__header__note'
                ).text
            ):
                rank = '未'
            results[target_rank][no] = [title, rank]
        print(f'Rank {target_rank.upper()} problems are fetched.')
    return results


def fetch_scores(results, driver):
    driver.get('https://paiza.jp/career/mypage/results')
    print('Start fetching...')
    for i in driver.find_elements(by=By.CLASS_NAME, value='basicBox'):
        problem_no = i.find_element(by=By.CLASS_NAME, value='boxT').text.split(':')[0]
        if len(problem_no) == 4:
            submit_datetime = (
                i.find_element(by=By.CLASS_NAME, value='boxTR')
                .text.split('：')[1]
                .split()[0]
            )
            props = i.find_element(by=By.CLASS_NAME, value='boxM')
            props = props.find_element(by=By.CLASS_NAME, value='inrTxt')
            props = props.find_elements(by=By.TAG_NAME, value='span')
            ans_lang = props[2].text
            ans_time = props[4].text
            ans_rank = props[6].text.replace('ランク', '')
            ans_score = props[8].text.replace('点', '')
            # print(problem_no, submit_datetime, ans_lang, ans_time, ans_rank, ans_score)
            for k in [submit_datetime, ans_lang, ans_time, ans_rank, ans_score]:
                try:
                    results[problem_no[0].lower()][problem_no].append(k)
                except KeyError:
                    print(f'!!! {problem_no} is deleted.')

    for i in results.values():
        for j in i.items():
            j[1][0] = j[1][0].split('】')[-1]

    return results


def print_solved(results):
    tmp = 'X'
    for i in results.values():
        for j in i.items():
            if j[1][-1] != '未':
                if j[0][0] != tmp:
                    print()
                    print(f'</div></details>')
                    print()
                    print(f'<details><summary>{j[0][0]}問題</summary><div>')
                    print()
                    print(f'|問題|タイトル|順位|提出日|言語|回答時間|ランク|点数|')
                    print(f'|-|-|-|-|-|-|-|-|')
                    tmp = j[0][0]
                print(f'|{j[0]}|{"|".join(j[1])}|')


def print_unsolved(results):
    tmp = 'X'
    for i in results.values():
        for j in i.items():
            if j[1][-1] == '未':
                if j[0][0] != tmp:
                    print()
                    print(f'</div></details>')
                    print()
                    print(f'<details><summary>{j[0][0]}問題</summary><div>')
                    print()
                    print(f'|問題|タイトル|')
                    print(f'|-|-|')
                    tmp = j[0][0]
                print(f'|{j[0]}|{"|".join(j[1][:1])}|')


if __name__ == '__main__':
    main()