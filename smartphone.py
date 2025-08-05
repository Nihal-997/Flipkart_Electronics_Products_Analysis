from playwright.sync_api import sync_playwright
import psycopg2
import image_download

flipkartUrl = "https://www.flipkart.com"
IMAGE_DIR = 'product_images'

DB_CONFIG = {
    'dbname': 'Flipkart_Electronics',
    'user': 'postgres',
    'password': 'admin',
    'host': 'localhost',
    'port': '5432'
}

def safe_float(value):
    try:
        return float(value.replace(",", "").replace("₹", "").strip())
    except:
        return 0

def parse_brand_model(title):
    words = title.split()
    brand = words[0] if words else "N/A"
    model = " ".join(words[1:]) if len(words) > 1 else "N/A"
    return brand, model

def categorize_specs(specs_elem, product_type):
    specs = {
        'RAM': 'N/A', 'Storage': 'N/A', 'Processor': 'N/A',
        'Battery': 'N/A', 'Display': 'N/A', 'Camera': 'N/A'
    }

    if specs_elem:
        for item in specs_elem.query_selector_all("li"):
            text = item.inner_text().strip().lower()
            if not text:
                continue

            # New logic: separate RAM + Storage if combined
            if "ram" in text and ("rom" in text or "storage" in text or "|" in text):
                parts = item.inner_text().strip().split('|')
                for part in parts:
                    part_lower = part.strip().lower()
                    if "ram" in part_lower:
                        specs['RAM'] = part.strip()
                    elif any(x in part_lower for x in ["rom", "storage", "ssd", "hdd"]):
                        specs['Storage'] = part.strip()
            elif "ram" in text:
                specs['RAM'] = item.inner_text().strip()
            elif any(x in text for x in ["rom", "storage", "ssd", "hdd"]):
                specs['Storage'] = item.inner_text().strip()
            elif any(x in text for x in ["intel", "amd", "ryzen", "core", "processor"]):
                specs['Processor'] = item.inner_text().strip()
            elif "battery" in text or "mah" in text:
                specs['Battery'] = item.inner_text().strip()
            elif any(x in text for x in ["display", "screen", "inch", "refresh"]):
                specs['Display'] = item.inner_text().strip()
            elif "camera" in text or "mp" in text:
                specs['Camera'] = item.inner_text().strip()

    return specs

def insert_into_db(data):
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    for item in data:
        cursor.execute("""
            INSERT INTO products_smartphone (
                product_type, brand, model, title,
                ram, storage, processor, battery,
                display, camera, star_rating, rating_count, review_count,
                original_price, discounted_price, discount_percentage, image_url
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            item["Product Type"], item["Brand"], item["Model"], item["Title"],
            item["RAM"], item["Storage"], item["Processor"], item["Battery"],
            item["Display"], item["Camera"], item["Star Rating"], item["Rating Count"], item["Review Count"],
            item["Original Price"], item["Discounted Price"], item["Discount (%)"], item["Image URL"]
        ))

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Data inserted into PostgreSQL database.")

def getProductData(page, product_type):
    allCards = page.query_selector_all('a.CGtC98')
    product_list = []

    for card in allCards:
        title_elem = card.query_selector('div.KzDlHZ')
        specs_elem = card.query_selector("ul.G4BRas")
        star_elem = card.query_selector("div.XQDdHH")
        rating_elem = card.query_selector("span.Wphh3N")
        orig_price_elem = card.query_selector("div.yRaY8j.ZYYwLA")
        disc_price_elem = card.query_selector("div.Nx9bqj._4b5DiR")
        discount_elem = card.query_selector("div.UkUFwK")
        image_url_elem = card.query_selector("div._4WELSP img")

        if title_elem and image_url_elem:
            title = title_elem.inner_text()
            brand, model = parse_brand_model(title)
            specs = categorize_specs(specs_elem, product_type)

            star_rating = safe_float(star_elem.inner_text()) if star_elem else 0
            rating_count = review_count = 0
            if rating_elem:
                rating_text = rating_elem.inner_text().split('&')
                rating_count = safe_float(rating_text[0].replace(" Ratings", "")) if len(rating_text) > 0 else 0
                review_count = safe_float(rating_text[1].replace(" Reviews", "")) if len(rating_text) > 1 else 0

            original_price = safe_float(orig_price_elem.inner_text()) if orig_price_elem else 0
            discounted_price = safe_float(disc_price_elem.inner_text()) if disc_price_elem else 0
            discount = safe_float(discount_elem.inner_text().split('%')[0]) if discount_elem else 0
            image_url = image_url_elem.get_attribute("src") if image_url_elem else 'N/A'

            product_list.append({
                "Product Type": product_type,
                "Brand": brand,
                "Model": model,
                "Title": title,
                "RAM": specs["RAM"],
                "Storage": specs["Storage"],
                "Processor": specs["Processor"],
                "Battery": specs["Battery"],
                "Display": specs["Display"],
                "Camera": specs["Camera"],
                "Star Rating": star_rating,
                "Rating Count": rating_count,
                "Review Count": review_count,
                "Original Price": original_price,
                "Discounted Price": discounted_price,
                "Discount (%)": discount,
                "Image URL": image_url
            })

            print('📦', title)
            print('🔖 Brand:', brand, '| Model:', model)
            print('📋 Specs:', specs)
            print('⭐', star_rating, '| Ratings:', rating_count, '| Reviews:', review_count)
            print('💰 MRP:', original_price, '| Offer:', discounted_price, '| Save %:', discount)
            print('🖼️ Image:', image_url)
            print('-'*60)

            image_download.download_image(image_url, IMAGE_DIR, title)

    return product_list

def firstPageLoad(page, keyword):
    page.wait_for_timeout(4000)
    searchInput = page.query_selector('input.Pke_EE')
    searchInput.fill(keyword)
    page.wait_for_timeout(1000)
    searchBt = page.query_selector('button._2iLD__')
    searchBt.click()
    page.wait_for_load_state('domcontentloaded')
    page.wait_for_timeout(4000)

def scrapeFlipkart():
    categories = ["smartphone"]
    all_data = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        for category in categories:
            try:
                print(f"\n🔎 Scraping category: {category.capitalize()}")

                page.goto(flipkartUrl)
                page.wait_for_load_state('domcontentloaded')
                page.wait_for_timeout(3000)

                firstPageLoad(page, category)

                page_count = 0
                
                   
                while page_count < 41:
                    print(f"📄 Page {page_count + 1}...")
                    page_data = getProductData(page, category.capitalize())
                    all_data.extend(page_data)
                    page_count += 1

                    next_button = page.query_selector('a._9QVEpD:has-text("Next")')
                    if not next_button or not next_button.is_visible():
                        print("🚫 No 'Next' button. Ending scrape for this category.")
                        break

                    next_button.click()
                    page.wait_for_timeout(4000)
                    page.wait_for_load_state('domcontentloaded')

            except Exception as e:
                print(f"⚠️ Error scraping category '{category}': {str(e)}\nSkipping to next...")

        browser.close()

    insert_into_db(all_data)

scrapeFlipkart()
               