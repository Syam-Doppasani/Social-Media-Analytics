# generate_instagram_data.py
import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
import sys

# Initialize without uniqueness constraints
fake = Faker()

# Configuration
NUM_SAMPLES = 50000
NICHES = ['fitness', 'food', 'travel', 'fashion', 'tech', 'beauty', 'gaming', 'business']
MEDIA_TYPES = ['image', 'video', 'carousel']

PERFORMANCE_FACTORS = {
    'fitness': {'base_likes': 800, 'comment_ratio': 0.04, 'follower_ratio': 0.008},
    'food': {'base_likes': 1200, 'comment_ratio': 0.05, 'follower_ratio': 0.01},
    'travel': {'base_likes': 1500, 'comment_ratio': 0.06, 'follower_ratio': 0.015},
    'fashion': {'base_likes': 900, 'comment_ratio': 0.045, 'follower_ratio': 0.009},
    'tech': {'base_likes': 700, 'comment_ratio': 0.035, 'follower_ratio': 0.007},
    'beauty': {'base_likes': 850, 'comment_ratio': 0.042, 'follower_ratio': 0.0085},
    'gaming': {'base_likes': 950, 'comment_ratio': 0.048, 'follower_ratio': 0.0095},
    'business': {'base_likes': 650, 'comment_ratio': 0.032, 'follower_ratio': 0.006}
}

def generate_post():
    """Generate a single synthetic Instagram post"""
    niche = random.choice(NICHES)
    media = random.choices(MEDIA_TYPES, weights=[0.6, 0.3, 0.1], k=1)[0]
    hour = random.randint(7, 23)
    day = random.randint(0, 6)
    
    factors = PERFORMANCE_FACTORS[niche]
    video_boost = 1.3 if media == 'video' else 1.0
    likes = int(factors['base_likes'] * video_boost * np.random.lognormal(0, 0.2))
    
    comments = int(likes * factors['comment_ratio'] * (1 + np.random.uniform(-0.2, 0.2)))
    new_followers = int(likes * factors['follower_ratio'] * (1 + np.random.uniform(-0.15, 0.15)))
    
    # Modified hashtag generation - removed unique constraint
    base_tag = f"#{niche}"
    extra_tags = [f"#{fake.word()}" for _ in range(random.randint(2, 5))]
    hashtags = ' '.join([base_tag] + extra_tags)
    
    post_date = datetime.now() - timedelta(days=random.randint(0, 365))
    post_date = post_date.replace(hour=hour, minute=random.randint(0, 59))
    
    return {
        'timestamp': post_date.strftime('%Y-%m-%d %H:%M:%S'),
        'likes': max(100, likes),
        'comments': max(5, comments),
        'new_followers': max(1, new_followers),
        'media_type': media,
        'hashtags': hashtags,
        'caption': fake.sentence(nb_words=random.randint(5, 15)),
        'hour': hour,
        'day_of_week': day,
        'niche': niche,
        'caption_length': random.randint(50, 250),
        'hashtag_count': hashtags.count('#'),
        'is_weekend': int(day >= 5)
    }

def main():
    print("Generating optimized Instagram dataset...")
    print(f"Python {sys.version.split()[0]}, pandas {pd.__version__}, numpy {np.__version__}")
    
    posts = []
    for i in range(NUM_SAMPLES):
        if i % 5000 == 0:
            print(f"Progress: {i}/{NUM_SAMPLES}", end='\r')
        posts.append(generate_post())
    
    df = pd.DataFrame(posts)
    df.to_csv('instagram_training_dataset.csv', index=False)
    print(f"\nSuccessfully generated {len(df):,} posts")

if __name__ == "__main__":
    main()