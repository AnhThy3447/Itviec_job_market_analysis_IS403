from typing import TypedDict, List
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime
import random

Entry = TypedDict('Entry', {
    'elem_id': str,
    'title': str,
    'url': str,
    'company_name': str,
    'company_type': str,
    'company_star': str,
    'company_industry': str,
    'company_size': str,
    'country': str,
    'location': str,
    'date_posted': str,
    'date_crawled': str,
    'job_expertise': str,
    'job_domain': list,
    'job_description': str,
    'job_requirements': str,
    'job_benefits': str,
    'working_model': str,
    'working_days': str,
    'overtime_policy': str,
    'salary': str,
    'skill_tags': list
})

JobDetail = TypedDict('JobDetail', {
    'company_star': str,
    'company_industry': str,
    'company_size': str,
    'country': str,
    'job_domain': list,
    'job_description': str,
    'job_requirements': str,
    'job_benefits': str,
    'working_days': str,
    'overtime_policy': str
})

def setup_driver():
    """Setup undetected-chromedriver với cấu hình tối ưu"""
    options = uc.ChromeOptions()
    
    # Các options cơ bản
    options.add_argument('--headless=new')  # Chạy ẩn, nhanh hơn
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-notifications')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-javascript')  # Tắt JS để tăng tốc, nếu trang không cần JS để hiển thị nội dung
    
    # Tắt load hình ảnh và các tài nguyên không cần
    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.default_content_setting_values.notifications": 2,
        "profile.managed_default_content_settings.stylesheets": 2,
        "profile.managed_default_content_settings.cookies": 2,
        "profile.managed_default_content_settings.javascript": 2,
        "profile.managed_default_content_settings.plugins": 2,
        "profile.managed_default_content_settings.popups": 2,
        "profile.managed_default_content_settings.geolocation": 2,
        "profile.managed_default_content_settings.media_stream": 2,
    }
    options.add_experimental_option("prefs", prefs)
    
    # User agent giả lập Chrome thật
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # Thêm ngôn ngữ
    options.add_argument('--lang=vi')
    
    # Khởi tạo driver với undetected_chromedriver
    driver = uc.Chrome(options=options, version_main=146)
    
    # Set page load timeout
    driver.set_page_load_timeout(20)
    
    return driver

def scrap_job_detail(driver, url):
    """Lấy chi tiết công việc - dùng Selenium nhưng parse bằng BS4 để tăng tốc"""
    job_data: JobDetail = {}
    
    try:
        driver.get(url)
        
        # Chờ một phần tử cụ thể xuất hiện
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".h4.ips-2.text-it-black"))
            )
        except:
            pass  # Nếu timeout thì vẫn tiếp tục với HTML hiện tại
        
        # Lấy HTML và parse bằng BS4
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Company star
        comp_star = soup.find(class_='h4 ips-2 text-it-black')
        job_data['company_star'] = comp_star.text.strip() if comp_star else "Không có company_star"
        
        # Company industry
        comp_industry = soup.find(class_='d-inline-flex text-wrap')
        job_data['company_industry'] = comp_industry.text.strip() if comp_industry else "Không có company_industry"
        
        # Các thông tin dạng hàng
        rows = soup.select("div.row.ipy-2")
        mapping = {
            "Company type": "company_type",
            "Company size": "company_size",
            "Working days": "working_days",
            "Overtime policy": "overtime_policy"
        }
        for row in rows:
            label_tag = row.select_one(".col.text-dark-grey")
            value_tag = row.select_one(".col.text-end.text-it-black")
            if label_tag and value_tag:
                label = label_tag.get_text(strip=True)
                value = value_tag.get_text(strip=True)
                if label in mapping:
                    job_data[mapping[label]] = value
        
        # Country
        country_row = None
        for row in rows:
            label_tag = row.select_one(".col.text-dark-grey")
            if label_tag and label_tag.get_text(strip=True) == "Country":
                country_row = row
                break
        
        if country_row:
            inline_block = country_row.select_one(".col.text-end.text-it-black .d-inline-block")
            if inline_block:
                country_span = inline_block.find("span", class_="align-middle")
                if country_span:
                    job_data['country'] = country_span.get_text(strip=True)
                else:
                    job_data['country'] = "Không tìm thấy tên quốc gia"
            else:
                # Fallback: lấy text từ value column
                country_value = country_row.select_one(".col.text-end.text-it-black")
                job_data['country'] = country_value.get_text(strip=True) if country_value else "Không có country"
        else:
            job_data['country'] = "Không tìm thấy country"
        
        # Job domain
        domain_elems = soup.find_all(class_='itag bg-light-grey itag-sm cursor-default')
        job_data['job_domain'] = [d.text.strip() for d in domain_elems] if domain_elems else []
        
        # Job description, requirement, benefits
        sections = soup.find_all("div", class_="imy-5 paragraph")
        for sec in sections:
            title_tag = sec.find("h2")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True).lower()
            title_tag.decompose()
            content = sec.get_text(separator="\n", strip=True)
            
            if "description" in title:
                job_data['job_description'] = content
            elif "skill" in title or "experience" in title:
                job_data['job_requirements'] = content
            elif "love working" in title or "benefit" in title:
                job_data['job_benefits'] = content
        
    except Exception as e:
        print(f"Lỗi khi lấy chi tiết: {e}")
    
    return job_data

def scrap_itviec(driver, place: str, page_num: int, limit: int) -> List[Entry]:
    results = []
    
    try:
        list_url = f'https://itviec.com/it-jobs/{place}?page={page_num}'
        print(f"Đang tải trang danh sách: {list_url}\n")
        
        driver.get(list_url)
        time.sleep(random.uniform(2, 4))
        
        # Tìm job cards
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        job_cards = soup.find_all(class_='job-card', limit=limit)
        if not job_cards:
            job_cards = soup.find_all('div', {'data-search--job-selection-job-url-value': True}, limit=limit)
        
        print(f"Tìm thấy {len(job_cards)} job cards")
        
        for idx, card in enumerate(job_cards, 1):
            print(f"--- Job #{idx} ---")
            data: Entry = {}
            
            # Title
            title_elem = card.find('h3') or card.find(class_='title')
            data['title'] = title_elem.text.strip() if title_elem else "Không có title"
            
            # Company name
            comp_name_elem = card.find(class_='text-rich-grey')
            data['company_name'] = comp_name_elem.text.strip() if comp_name_elem else "Không có company_name"
            
            # Location
            location_elem = card.find(class_='text-rich-grey text-truncate text-nowrap stretched-link position-relative')
            data['location'] = location_elem.text.strip() if location_elem else "Không có location"
            
            # Job expertise
            expertise_elem = card.find(class_='position-relative stretched-link text-rich-grey text-hover-red ips-2 text-truncate text-decoration-dot-underline small-text')
            data['job_expertise'] = expertise_elem.text.strip() if expertise_elem else "Không có job expertise"
            
            # Working model
            work_model_elem = card.find(class_='text-rich-grey flex-shrink-0')
            data['working_model'] = work_model_elem.text.strip() if work_model_elem else "Không có working model"
            
            # URL & element ID
            url_value = card.get('data-search--job-selection-job-url-value') or \
                        card.get('data-url') or \
                        (card.find('a', href=True)['href'] if card.find('a', href=True) else None)
            
            if url_value:
                if url_value.startswith('/'):
                    full_url = f"https://itviec.com{url_value}"
                else:
                    full_url = f"https://itviec.com/{url_value}"
            else:
                full_url = ""
            
            if '/it-jobs/' in full_url:
                elem_id = full_url.split("/it-jobs/")[1].split("/")[0]
                data['elem_id'] = elem_id
                data['url'] = f"https://itviec.com/it-jobs/{elem_id}"
            else:
                data['elem_id'] = ""
                data['url'] = full_url
            
            # Skill tags
            skill_tags = card.find_all(class_='itag') or card.find_all(class_='skill-tag')
            data['skill_tags'] = [s.text.strip() for s in skill_tags] if skill_tags else []
            
            # Date posted
            date_posted_elem = card.find(class_='small-text text-dark-grey')
            data['date_posted'] = date_posted_elem.text.strip() if date_posted_elem else "Không có date posted"
            
            # Date crawled
            data['date_crawled'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Lấy chi tiết (nếu có URL)
            if data['url']:
                time.sleep(random.uniform(2, 4))
                job_detail = scrap_job_detail(driver, data['url'])
                data.update(job_detail)
            
            results.append(data)
            
            time.sleep(random.uniform(2, 4))
    
    except Exception as e:
        print(f"Lỗi: {e}")
    
    return results

def main():
    try:
        print("Bắt đầu scrape ITViec bằng undetected-chromedriver...\n")
        columns = [
            "elem_id", "title", "company_name", "company_type", "company_star", "company_industry",
            "company_size", "country", "location", "date_posted", "job_expertise",
            "job_domain", "skill_tags", "job_description", "job_requirements", "job_benefits",
            "working_model", "working_days", "overtime_policy", "date_crawled", "url"
        ]  

        places = ["ha-noi", "ho-chi-minh-hcm"]
        codes = ["HN", "HCM"]
        max_pages = [24, 40]
        
        for place, code, max_page in zip(places, codes, max_pages):
            all_data = []
            filename = f"itviec_jobs_{datetime.now().strftime('%d_%m_%Y')}_{code}.csv"
            print("*"*10, f" KHU VỰC: {place.upper()} ", "*"*10)
            
            driver = setup_driver()
            
            for page in range(1, max_page + 1):
                print(f"\n=== ĐANG SCRAPE TRANG {page} ===")
                data = scrap_itviec(driver, place, page, 20)
                
                if not data:
                    print(f"Trang {page} không có dữ liệu.")
                    break
                
                all_data.extend(data)
                df = pd.DataFrame(all_data)
                
                # Sắp xếp lại cột và lưu file
                df = df[columns]
                df.to_csv(filename, index=False, encoding='utf-8-sig')
                print(f"Đã lưu dữ liệu trang số {page} vào '{filename}'")

                if len(data) < 20:
                    print(f"--> Trang {page} chỉ có {len(data)} job.")
                    break
                
                time.sleep(random.uniform(3, 5))

            driver.quit()
    
    except Exception as e:
        print(f"Lỗi hệ thống: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()