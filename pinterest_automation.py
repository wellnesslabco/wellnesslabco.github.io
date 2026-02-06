#!/usr/bin/env python3
"""
Pinterest Skincare Affiliate Automation Script
Automates daily Pinterest posts for trending skincare products with Amazon affiliate links
"""

import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont
import textwrap
import random
from datetime import datetime
import json
import os

# Configuration
AMAZON_AFFILIATE_TAG = "wellnesslabco-20"
PINTEREST_IMAGE_SIZE = (1000, 1500)  # 2:3 ratio optimal for Pinterest
OUTPUT_DIR = os.getcwd()  # FIXED: Use current directory instead of hardcoded path

class SkincareAffiliateBot:

    def __init__(self):
        self.trending_ingredients = [
            "PDRN", "bakuchiol", "peptides", "niacinamide",
            "kojic acid", "retinol", "vitamin C", "hyaluronic acid",
            "collagen", "ceramides", "snail mucin"
        ]

    def get_amazon_bestsellers(self, category_url="https://www.amazon.com/Best-Sellers-Beauty-Personal-Care-Facial-Skin-Care-Products/zgbs/beauty/11060711"):
        """
        Scrape Amazon bestsellers in skincare category
        Returns list of product ASINs and basic info
        """
        print("🔍 Fetching Amazon bestsellers...")

        # Note: In production, you'd want to use Amazon Product Advertising API
        # For now, returning example bestseller ASINs to demonstrate workflow

        bestsellers = [
            {"asin": "B0B2RM68G2", "name": "BIODANCE Bio-Collagen Mask", "trending": True},
            {"asin": "B07NCRQL81", "name": "The Ordinary Niacinamide Serum", "trending": True},
            {"asin": "B01LTH7GKK", "name": "CeraVe Moisturizing Cream", "trending": False},
            {"asin": "B00TTD9BRC", "name": "Cetaphil Gentle Skin Cleanser", "trending": False},
            {"asin": "B09JKHNFLW", "name": "medicube Age-R Toner Pads", "trending": True},
        ]

        return bestsellers

    def check_trending_match(self, product_name):
        """Check if product matches trending ingredients"""
        product_lower = product_name.lower()
        for ingredient in self.trending_ingredients:
            if ingredient.lower() in product_lower:
                return True, ingredient
        return False, None

    def select_daily_product(self):
        """Select the best product for today's post"""
        bestsellers = self.get_amazon_bestsellers()

        # Prioritize products that are both bestsellers AND match trending ingredients
        for product in bestsellers:
            is_trending, ingredient = self.check_trending_match(product['name'])
            if is_trending and product['trending']:
                print(f"✅ Selected: {product['name']} (Trending ingredient: {ingredient})")
                return product

        # Fallback to first bestseller
        return bestsellers[0]

    def generate_pinterest_image(self, product_info, output_path):
        """Create Pinterest-optimized product image"""
        print("🎨 Creating Pinterest-optimized image...")

        width, height = PINTEREST_IMAGE_SIZE

        # Create base image with aesthetic background
        colors = [
            '#FFE5E5',  # Soft pink
            '#E5F3FF',  # Soft blue
            '#FFF5E5',  # Soft peach
            '#F0E5FF',  # Soft purple
        ]
        bg_color = random.choice(colors)
        img = Image.new('RGB', (width, height), color=bg_color)
        draw = ImageDraw.Draw(img)

        # Load fonts
        try:
            title_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejavuSans-Bold.ttf', 60)
            subtitle_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejavuSans.ttf', 40)
            small_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejavuSans.ttf', 30)
        except:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            small_font = ImageFont.load_default()

        # Add product name
        product_name = product_info['name']
        wrapped_name = textwrap.fill(product_name, width=20)
        title_bbox = draw.multiline_textbbox((0, 0), wrapped_name, font=title_font, align='center')
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (width - title_width) // 2
        draw.multiline_text((title_x, 100), wrapped_name, fill='#2C2C2C', font=title_font, align='center')

        # Add benefits (would be customized per product in full version)
        benefits = [
            "✓ Science-Backed Formula",
            "✓ Visible Results",
            "✓ Trending in 2026",
            "✓ Highly Rated"
        ]

        y_position = 400
        for benefit in benefits:
            draw.text((100, y_position), benefit, fill='#4A4A4A', font=subtitle_font)
            y_position += 80

        # Add call to action
        cta = "Tap to Shop →"
        cta_bbox = draw.textbbox((0, 0), cta, font=subtitle_font)
        cta_width = cta_bbox[2] - cta_bbox[0]
        cta_x = (width - cta_width) // 2
        draw.rectangle([cta_x - 20, 1350, cta_x + cta_width + 20, 1420], fill='#FF6B9D')
        draw.text((cta_x, 1360), cta, fill='white', font=subtitle_font)

        # Save
        img.save(output_path, 'JPEG', quality=95)
        print(f"✅ Image saved: {output_path}")

        return output_path

    def generate_description(self, product_info):
        """Generate science-backed Pinterest description"""
        print("✍️ Generating optimized description...")

        description = f"""{product_info['name']} - Your New Skincare Essential

Transform your routine with this trending skincare product that's taking 2026 by storm.

✨ WHY SKINCARE LOVERS ARE OBSESSED:
• Science-backed formula with proven results
• Addresses multiple skin concerns
• Suitable for all skin types
• Visible improvement in just weeks

💡 TRENDING INGREDIENT SPOTLIGHT:
This product features cutting-edge actives that dermatologists are raving about in 2026.

👉 Tap the link to shop and transform your skincare routine!

#KBeauty #Skincare #SkincareRoutine #BeautyFinds #GlowySkin #SkincareAddict #HealthySkin #SkincareTips #AntiAging #BeautyDeals #SkincareObsessed #GlassKin #SkinGoals #BeautyMustHaves"""

        return description

    def generate_affiliate_link(self, asin):
        """Generate Amazon affiliate link"""
        return f"https://www.amazon.com/dp/{asin}/?tag={AMAZON_AFFILIATE_TAG}"

    def create_daily_post(self):
        """Main function to create complete daily post"""
        print("🚀 Starting daily Pinterest post creation...")
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}")

        # Select product
        product = self.select_daily_product()

        # Generate image
        timestamp = datetime.now().strftime('%Y%m%d')
        image_path = f"{OUTPUT_DIR}/pinterest_{timestamp}_{product['asin']}.jpg"
        self.generate_pinterest_image(product, image_path)

        # Generate description
        description = self.generate_description(product)
        desc_path = f"{OUTPUT_DIR}/description_{timestamp}.txt"
        with open(desc_path, 'w') as f:
            f.write(description)

        # Generate affiliate link
        affiliate_link = self.generate_affiliate_link(product['asin'])
        link_path = f"{OUTPUT_DIR}/link_{timestamp}.txt"
        with open(link_path, 'w') as f:
            f.write(f"Affiliate Link: {affiliate_link}\n")
            f.write(f"Product: {product['name']}\n")
            f.write(f"ASIN: {product['asin']}\n")

        # Save post info
        post_info = {
            "date": datetime.now().isoformat(),
            "product": product,
            "image_path": image_path,
            "description_path": desc_path,
            "link_path": link_path,
            "affiliate_link": affiliate_link
        }

        info_path = f"{OUTPUT_DIR}/post_info_{timestamp}.json"
        with open(info_path, 'w') as f:
            json.dump(post_info, f, indent=2)

        print("\n✅ DAILY POST READY!")
        print(f"📁 Image: {image_path}")
        print(f"📝 Description: {desc_path}")
        print(f"🔗 Link: {affiliate_link}")
        print(f"\n📋 Post info saved: {info_path}")

        return post_info


if __name__ == "__main__":
    bot = SkincareAffiliateBot()
    bot.create_daily_post()
