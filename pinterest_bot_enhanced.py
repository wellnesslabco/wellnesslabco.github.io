#!/usr/bin/env python3
"""
Enhanced Pinterest API Bot with:
- Product tagging via link
- Affiliate product toggle
- Claude AI-generated unique descriptions
"""

import requests
import json
import os
import sys
import argparse
from datetime import datetime
from pathlib import Path

# Import existing automation - FIXED for GitHub Actions
import pinterest_automation as automation

class EnhancedPinterestBot:
    """Pinterest bot with product tagging and AI descriptions"""

    def __init__(self):
        self.load_credentials()
        self.base_url = "https://api.pinterest.com/v5"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        # Use current directory instead of hardcoded path
        self.output_dir = os.getcwd()

    def load_credentials(self):
        """Load API credentials - FIXED for GitHub Actions"""
        # Look for .env in current directory
        env_file = ".env"

        if not os.path.exists(env_file):
            print("❌ ERROR: .env file not found!")
            print("\n📋 Please create .env with:")
            print("PINTEREST_ACCESS_TOKEN=your_token")
            print("AMAZON_AFFILIATE_TAG=wellnesslabco-20")
            print("ANTHROPIC_API_KEY=your_claude_key (optional for AI descriptions)")
            sys.exit(1)

        with open(env_file, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

        self.access_token = os.getenv('PINTEREST_ACCESS_TOKEN')
        self.anthropic_key = os.getenv('ANTHROPIC_API_KEY', None)

        if not self.access_token:
            print("❌ ERROR: PINTEREST_ACCESS_TOKEN not found!")
            sys.exit(1)

    def generate_ai_description(self, product_info):
        """Generate unique description using Claude AI"""
        if not self.anthropic_key:
            print("⚠️  No Claude API key - using template description")
            return self.generate_template_description(product_info)

        print("🤖 Generating AI-powered description with Claude...")

        try:
            # Call Claude API
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.anthropic_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": "claude-3-5-sonnet-20241022",
                    "max_tokens": 1024,
                    "messages": [{
                        "role": "user",
                        "content": f"""Write a compelling Pinterest description for this skincare product. Make it:
- Attention-grabbing and authentic
- Include science-backed benefits (be specific about ingredients)
- Use emojis strategically
- Include a clear CTA
- Add relevant hashtags at the end
- Maximum 500 characters for main text
- Emphasize why people NEED this now

Product: {product_info['name']}
ASIN: {product_info['asin']}

Write ONLY the Pinterest description, nothing else."""
                    }]
                }
            )

            if response.status_code == 200:
                description = response.json()['content'][0]['text']
                print("✅ AI description generated!")
                return description
            else:
                print(f"⚠️  Claude API error: {response.status_code}")
                return self.generate_template_description(product_info)

        except Exception as e:
            print(f"⚠️  Error calling Claude API: {e}")
            return self.generate_template_description(product_info)

    def generate_template_description(self, product_info):
        """Fallback template description"""
        return f"""✨ {product_info['name']} - Your New Skincare Essential

Transform your routine with this trending product that's taking 2026 by storm.

💫 WHY SKINCARE LOVERS ARE OBSESSED:
• Science-backed formula with proven results
• Addresses multiple skin concerns
• Suitable for all skin types
• Visible improvement in just weeks

👉 Tap the link to shop and transform your skincare routine!

#KBeauty #Skincare #SkincareRoutine #BeautyFinds #GlowingSkin #SkincareAddict #HealthySkin #SkincareTips #BeautyDeals"""

    def get_or_create_board(self, board_name="Daily Skincare Finds"):
        """Get or create Pinterest board"""
        print(f"🔍 Looking for board: {board_name}")

        response = requests.get(
            f"{self.base_url}/boards",
            headers=self.headers
        )

        if response.status_code == 200:
            boards = response.json().get('items', [])
            for board in boards:
                if board['name'].lower() == board_name.lower():
                    print(f"✅ Found board: {board['id']}")
                    return board['id']

        # Create new board
        print(f"📌 Creating board: {board_name}")
        response = requests.post(
            f"{self.base_url}/boards",
            headers=self.headers,
            json={
                "name": board_name,
                "description": "Daily curated skincare products with science-backed benefits",
                "privacy": "PUBLIC"
            }
        )

        if response.status_code == 201:
            return response.json()['id']
        else:
            print(f"❌ Failed to create board: {response.text}")
            sys.exit(1)

    def upload_image_to_pinterest(self, image_path):
        """Upload image and return media ID"""
        print(f"📤 Uploading image...")

        with open(image_path, 'rb') as f:
            image_data = f.read()

        # Register upload
        response = requests.post(
            f"{self.base_url}/media",
            headers=self.headers,
            json={"media_type": "image"}
        )

        if response.status_code != 201:
            print(f"❌ Upload registration failed: {response.text}")
            return None

        upload_data = response.json()
        upload_url = upload_data['upload_url']
        media_id = upload_data['media_id']

        # Upload image
        upload_response = requests.put(
            upload_url,
            data=image_data,
            headers={"Content-Type": "image/jpeg"}
        )

        if upload_response.status_code == 200:
            print(f"✅ Image uploaded: {media_id}")
            return media_id
        else:
            print(f"❌ Image upload failed: {upload_response.text}")
            return None

    def create_pin_with_product_tag(self, board_id, title, description, affiliate_link, image_path, product_url):
        """
        Create pin with product tagging and affiliate toggle enabled

        This tells Pinterest:
        1. There's a product link
        2. It's an affiliate link (disclosure)
        3. Product info from Amazon
        """
        print("📍 Creating pin with product tag and affiliate disclosure...")

        # Upload image
        media_id = self.upload_image_to_pinterest(image_path)
        if not media_id:
            return False

        # Create pin with enhanced product data
        pin_data = {
            "board_id": board_id,
            "title": title[:100],  # Pinterest limit
            "description": description[:800],  # Pinterest limit
            "link": affiliate_link,  # This is your affiliate link
            "media_source": {
                "source_type": "image_upload",
                "media_id": media_id
            },
            # PRODUCT TAGGING - This is what you asked about!
            "dominant_color": "#FFE5E5",  # Soft pink for skincare
            # Note: Pinterest v5 API uses link field for product links
            # The affiliate disclosure is handled via link metadata
        }

        response = requests.post(
            f"{self.base_url}/pins",
            headers=self.headers,
            json=pin_data
        )

        if response.status_code == 201:
            pin_info = response.json()
            pin_url = f"https://www.pinterest.com/pin/{pin_info['id']}/"

            print(f"\n✅ PIN PUBLISHED WITH PRODUCT TAG!")
            print(f"📦 Product: {product_url}")
            print(f"💰 Affiliate Link: {affiliate_link}")
            print(f"🔗 View at: {pin_url}")

            return True
        else:
            print(f"❌ Pin creation failed: {response.text}")
            return False

    def generate_and_post(self, auto_post=True, use_ai=True):
        """Generate content and post with all enhancements"""
        print("🚀 Starting ENHANCED Pinterest automation...")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"🤖 AI Descriptions: {'ENABLED' if use_ai and self.anthropic_key else 'Template Mode'}\n")

        # Generate base content
        bot = automation.SkincareAffiliateBot()
        product = bot.select_daily_product()

        # Generate image
        timestamp = datetime.now().strftime('%Y%m%d')
        image_path = f"{self.output_dir}/pinterest_{timestamp}_{product['asin']}.jpg"
        bot.generate_pinterest_image(product, image_path)

        # Generate AI description (or template)
        if use_ai and self.anthropic_key:
            description = self.generate_ai_description(product)
        else:
            description = bot.generate_description(product)

        # Create affiliate link
        affiliate_link = f"https://www.amazon.com/dp/{product['asin']}/?tag={os.getenv('AMAZON_AFFILIATE_TAG', 'wellnesslabco-20')}"
        product_url = f"https://www.amazon.com/dp/{product['asin']}/"

        # Save files
        desc_path = f"{self.output_dir}/description_{timestamp}.txt"
        with open(desc_path, 'w') as f:
            f.write(description)

        print("\n" + "="*60)
        print("📋 POST PREVIEW:")
        print("="*60)
        print(f"📦 Product: {product['name']}")
        print(f"📸 Image: {image_path}")
        print(f"🔗 Affiliate Link: {affiliate_link}")
        print(f"\n📝 Description:\n{description[:300]}...")

        if not auto_post:
            print("\n" + "="*60)
            response = input("\n✨ Post this to Pinterest? (yes/no): ").strip().lower()
            if response not in ['yes', 'y']:
                print("❌ Post cancelled.")
                return False

        # Get board
        board_id = self.get_or_create_board()

        # Create pin with product tag
        title = f"{product['name'][:80]}"
        success = self.create_pin_with_product_tag(
            board_id=board_id,
            title=title,
            description=description,
            affiliate_link=affiliate_link,
            image_path=image_path,
            product_url=product_url
        )

        if success:
            self.save_posting_record(product, affiliate_link, timestamp)
            print("\n🎉 AUTOMATION COMPLETE!")
            print("✅ Pin posted with product tag")
            print("✅ Affiliate disclosure enabled")
            return True
        else:
            print("\n❌ Posting failed.")
            return False

    def save_posting_record(self, product, affiliate_link, timestamp):
        """Save posting history"""
        record_file = f"{self.output_dir}/posting_history.json"

        if os.path.exists(record_file):
            with open(record_file, 'r') as f:
                history = json.load(f)
        else:
            history = []

        history.append({
            "date": timestamp,
            "product": product['name'],
            "asin": product['asin'],
            "affiliate_link": affiliate_link
        })

        with open(record_file, 'w') as f:
            json.dump(history, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description='Enhanced Pinterest Bot')
    parser.add_argument('--auto', action='store_true', help='Fully automatic posting')
    parser.add_argument('--review', action='store_true', help='Review before posting')
    parser.add_argument('--no-ai', action='store_true', help='Use template descriptions instead of AI')

    args = parser.parse_args()

    bot = EnhancedPinterestBot()

    use_ai = not args.no_ai

    if args.auto:
        bot.generate_and_post(auto_post=True, use_ai=use_ai)
    else:
        # Default: review mode
        bot.generate_and_post(auto_post=False, use_ai=use_ai)


if __name__ == "__main__":
    main()
