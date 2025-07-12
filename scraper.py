import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options


def login_instagram(driver, username, password):
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(5)

    user_input = driver.find_element(By.NAME, "username")
    pass_input = driver.find_element(By.NAME, "password")

    user_input.send_keys(username)
    pass_input.send_keys(password)
    pass_input.send_keys(Keys.RETURN)

    time.sleep(7)  # aguarda login


def get_recent_post_urls(driver, username, count=3):
    driver.get(f"https://www.instagram.com/{username}/")
    time.sleep(5)

    post_links = driver.find_elements(By.XPATH, '//a[contains(@href, "/p/")]')
    urls = []
    for link in post_links:
        href = link.get_attribute("href")
        if href and href not in urls:
            urls.append(href)
        if len(urls) >= count:
            break
    return urls


def get_comments_from_post(driver, post_url, comment_count=16):
    driver.get(post_url)
    time.sleep(5)

    comments = []
    comment_elements = driver.find_elements(By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/section/main/div/div[1]/div/div[2]/div/div[2]/div/div/ul/li/div/button")

    for comment in comment_elements[:comment_count]:
        comments.append(comment.text)

    return comments


def main():
    INSTAGRAM_USER = ""
    INSTAGRAM_PASS = ""

    usernames_file = "usernames"
    visited_file = "visited_urls"
    output_file = "comments.json"

    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    login_instagram(driver, INSTAGRAM_USER, INSTAGRAM_PASS)

    with open(usernames_file, "r") as f:
        usernames = [line.strip() for line in f.readlines() if line.strip()]

    try:
        with open(visited_file, "r") as f:
            visited_urls = set(line.strip() for line in f.readlines())
    except FileNotFoundError:
        visited_urls = set()

    try:
        with open(output_file, "r", encoding="utf-8") as f:
            all_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        all_data = []

    for username in usernames:
        print(f"Acessando perfil: {username}")
        post_urls = get_recent_post_urls(driver, username)

        for url in post_urls:
            if url in visited_urls:
                continue

            print(f"Coletando comentários de: {url}")
            comments = get_comments_from_post(driver, url)

            all_data.append({
                "post_url": url,
                "comments": comments
            })

            with open(visited_file, "a", encoding="utf-8") as f:
                f.write(url + "\n")

            time.sleep(3)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    driver.quit()

    print("\nDados coletados:")
    print(json.dumps(all_data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
