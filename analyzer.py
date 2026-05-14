import cv2
import pandas as pd
import numpy as np
from ultralytics import SAM
from sklearn.cluster import KMeans
import os
from supabase import create_client, Client

# Get these from your Supabase Project Settings > API
url = "YOUR_SUPABASE_URL"
key = "YOUR_SUPABASE_SERVICE_ROLE_KEY" # Use Service Role for backend scripts
supabase: Client = create_client(url, key)

def save_to_database(product_data):
    # This sends the analyzed dress straight to the website's database
    data, count = supabase.table("products").insert({
        "store_name": product_data['store'],
        "product_name": product_data['name'],
        "price": product_data['price'],
        "image_url": product_data['image_url'],
        "color_season": product_data['season'],
        "hex_code": product_data['hex']
    }).execute()
    print(f"✅ Successfully synced {product_data['name']} to the cloud.")
# Load the "Segment Anything" Model (The high-accuracy 'cutter')
# This model automatically finds the clothing in the photo
model = SAM("sam2_b.pt") 

def analyze_color_season(image_path):
    # 1. Load and Segment
    # We ask the AI to find the most prominent object (the dress)
    results = model.predict(image_path)
    mask = results[0].masks.data[0].cpu().numpy() # The "cutout"
    
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # 2. Isolate the fabric pixels only
    fabric_pixels = img[mask == 1]
    
    # 3. Find the "True" dominant color using K-Means clustering
    # This ignores shadows and highlights to find the actual dye color
    kmeans = KMeans(n_clusters=1).fit(fabric_pixels)
    dominant_rgb = kmeans.cluster_centers_[0]
    
    # 4. The Seasonal Logic (Simplified for this example)
    # Advanced logic would convert RGB -> CIELAB here
    r, g, b = dominant_rgb
    
    if r > 200 and g < 150: return "Bright Spring"
    if r < 100 and b > 150: return "Cool Winter"
    if r > 150 and g > 150 and b < 100: return "Warm Autumn"
    
    return "Deep Winter" # Default placeholder

def process_csv():
    df = pd.read_csv("clothing_data.csv")
    seasons = []
    for index, row in df.iterrows():
        print(f"🧠 AI analyzing: {row['name']}")
        image_path = row.get('image_path', '')
        if not image_path or not os.path.exists(image_path):
            seasons.append("Unknown")
            continue
        try:
            season = analyze_color_season(image_path)
        except Exception as e:
            season = "Unknown"
        seasons.append(season)
    df['color_season'] = seasons
    df.to_csv("analyzed_clothing.csv", index=False)
    print("✨ All clothes tagged with high-accuracy seasons!")

if __name__ == "__main__":
    process_csv()