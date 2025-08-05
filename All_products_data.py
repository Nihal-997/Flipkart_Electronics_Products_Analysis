from playwright.sync_api import sync_playwright
import psycopg2
import image_download

flipkartUrl = "https://www.flipkart.com"
IMAGE_DIR = 'product_images'

# 🛡️ Database connection config
DB_CONFIG = {
    'dbname': 'Flipkart_Electronics',
    'user': 'postgres',
    'password': 'admin',
    'host': 'localhost',
    'port': '5432'
}

# 🧼 Safe float conversion
def safe_float(value):
    try:
        return float(value.replace(",", "").replace("₹", "").strip())
    except:
        return 0

# 💾 Insert data into PostgreSQL
def insert_into_db(data):
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    for item in data:
        cursor.execute("""
            INSERT INTO products (
                product_type, title, specifications, star_rating,
                rating_count, review_count, original_price,
                discounted_price, discount_percentage, image_url
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            item["Product Type"], item["Title"], item["Specifications"],
            item["Star Rating"], item["Rating Count"], item["Review Count"],
            item["Original Price"], item["Discounted Price"],
            item["Discount (%)"], item["Image URL"]
        ))

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Data inserted into PostgreSQL database.")

# 🔍 Scrape page data
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

            # ✅ Collect all specs as comma-separated string
            specs_list = []
            if specs_elem:
                spec_items = specs_elem.query_selector_all("li")
                for item in spec_items:
                    text = item.inner_text().strip()
                    if text:
                        specs_list.append(text)
            specifications = ", ".join(specs_list) if specs_list else 'N/A'

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
                "Title": title,
                "Specifications": specifications,
                "Star Rating": star_rating,
                "Rating Count": rating_count,
                "Review Count": review_count,
                "Original Price": original_price,
                "Discounted Price": discounted_price,
                "Discount (%)": discount,
                "Image URL": image_url
            })

            print('📦', title)
            print('📋', specifications)
            print('⭐', star_rating, '| Ratings:', rating_count, '| Reviews:', review_count)
            print('💰 MRP:', original_price, '| Offer:', discounted_price, '| Save %:', discount)
            print('🖼️ Image:', image_url)
            print('-'*60)

            image_download.download_image(image_url, IMAGE_DIR, title)

    return product_list

# 🔍 First load to search a product
def firstPageLoad(page, keyword):
    page.wait_for_timeout(4000)
    searchInput = page.query_selector('input.Pke_EE')
    searchInput.fill(keyword)
    page.wait_for_timeout(1000)
    searchBt = page.query_selector('button._2iLD__')
    searchBt.click()
    page.wait_for_load_state('domcontentloaded')
    page.wait_for_timeout(4000)

# 🔁 Loop over multiple categories
def scrapeFlipkart():
    categories = ["laptop", "smartphone", "tablet", "refrigerator", "television", "washing machine",
                  "air conditioner","fan","water purifier","air purifier","water geyser","chimney","juicer mixer grinder"]
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