from cms_core import publish_website
from erp_core import ERPDatabase
import os

WEBSITEDIR = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(WEBSITEDIR, 'index.html')

db = ERPDatabase()
settings = db.get_website_settings()
products = db.get_all_products()

data = settings.copy()
data['products'] = products

# Ensure image paths are base64 if needed, but for static generation we usually keep paths relative?
# Wait, for static site (server.py), relative paths like 'uploads/xxx.jpg' are fine.
# But verify shop_admin.py logic.
# shop_admin.py uses base64 for PREVIEW (iframe), but relative paths for PUBLISH (index.html).

publish_website(data, INDEX_PATH)
print("Website force republished.")
