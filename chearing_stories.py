import streamlit as st
import requests
from datetime import datetime, timedelta

# YouTube API Key
API_KEY = "AIzaSyC5JIzTnofRHETIAbbyURhd6pX4meGcoKA"
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

# Streamlit App Title
st.title("🎯 YouTube Viral Topics Finder - Motivation & Life Advice")
st.markdown("*Find trending motivational content from rising channels (under 3K subscribers)*")

# Input Fields
days = st.number_input("Enter Days to Search (1-30):", min_value=1, max_value=30, value=7)

# Comprehensive list of motivation, consistency, and life advice keywords
keywords = [
    "Motivation for success", "Daily motivation", "Morning motivation", 
    "Consistency habits", "Build consistency", "Discipline and consistency",
    "Life advice for young adults", "Best life advice", "Real life lessons",
    "Self improvement tips", "Personal growth advice", "Change your life",
    "Overcome procrastination", "Stop being lazy", "Get disciplined",
    "Success mindset", "Growth mindset", "Winning mindset",
    "Productive morning routine", "Daily routine for success", "Habits of successful people",
    "Stay motivated everyday", "Never give up motivation", "Keep going motivation",
    "Life changing advice", "Advice that changed my life", "Best advice ever",
    "Stoic wisdom", "Stoicism for life", "Marcus Aurelius advice",
    "How to stay focused", "Focus and discipline", "Mental toughness",
    "Transform your life", "Level up your life", "Become your best self",
    "Hard work motivation", "Work hard in silence", "Grind motivation",
    "Overcome obstacles", "Face your fears", "Conquer challenges",
    "Goal setting motivation", "Achieve your goals", "Dream big work hard",
    "Inspirational speech", "Motivational speech", "Life lessons speech",
    "Stop wasting time", "Time management motivation", "Make every day count",
    "Believe in yourself", "Self confidence boost", "You can do it",
    "Success story motivation", "Rags to riches story", "Comeback story"
]

# Minimum views threshold for better results
min_views = st.number_input("Minimum Views Required:", min_value=100, max_value=100000, value=500)

# Fetch Data Button
if st.button("🚀 Find Trending Topics"):
    try:
        # Calculate date range
        start_date = (datetime.utcnow() - timedelta(days=int(days))).isoformat("T") + "Z"
        all_results = []
        
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Iterate over the list of keywords
        for idx, keyword in enumerate(keywords):
            status_text.text(f"Searching: {keyword} ({idx + 1}/{len(keywords)})")
            progress_bar.progress((idx + 1) / len(keywords))

            # Define search parameters
            search_params = {
                "part": "snippet",
                "q": keyword,
                "type": "video",
                "order": "viewCount",
                "publishedAfter": start_date,
                "maxResults": 10,  # Increased to find more videos
                "key": API_KEY,
                "relevanceLanguage": "en",
                "videoDuration": "medium"  # Filter for medium length videos (4-20 min)
            }

            # Fetch video data
            response = requests.get(YOUTUBE_SEARCH_URL, params=search_params)
            data = response.json()

            # Check if "items" key exists
            if "items" not in data or not data["items"]:
                continue

            videos = data["items"]
            video_ids = [video["id"]["videoId"] for video in videos if "id" in video and "videoId" in video["id"]]
            channel_ids = [video["snippet"]["channelId"] for video in videos if "snippet" in video and "channelId" in video["snippet"]]

            if not video_ids or not channel_ids:
                continue

            # Fetch video statistics
            stats_params = {"part": "statistics,contentDetails", "id": ",".join(video_ids), "key": API_KEY}
            stats_response = requests.get(YOUTUBE_VIDEO_URL, params=stats_params)
            stats_data = stats_response.json()

            if "items" not in stats_data or not stats_data["items"]:
                continue

            # Fetch channel statistics
            channel_params = {"part": "statistics,snippet", "id": ",".join(channel_ids), "key": API_KEY}
            channel_response = requests.get(YOUTUBE_CHANNEL_URL, params=channel_params)
            channel_data = channel_response.json()

            if "items" not in channel_data or not channel_data["items"]:
                continue

            stats = stats_data["items"]
            channels = channel_data["items"]

            # Create channel lookup dictionary
            channel_dict = {ch["id"]: ch for ch in channels}

            # Collect results
            for video, stat in zip(videos, stats):
                channel_id = video["snippet"]["channelId"]
                channel = channel_dict.get(channel_id)
                
                if not channel:
                    continue
                
                title = video["snippet"].get("title", "N/A")
                description = video["snippet"].get("description", "")[:250]
                video_url = f"https://www.youtube.com/watch?v={video['id']['videoId']}"
                channel_name = video["snippet"].get("channelTitle", "N/A")
                published_at = video["snippet"].get("publishedAt", "")
                
                views = int(stat["statistics"].get("viewCount", 0))
                likes = int(stat["statistics"].get("likeCount", 0))
                comments = int(stat["statistics"].get("commentCount", 0))
                subs = int(channel["statistics"].get("subscriberCount", 0))
                
                # Calculate engagement rate
                engagement_rate = ((likes + comments) / views * 100) if views > 0 else 0

                # Filter: channels with < 3000 subs and minimum views threshold
                if subs < 3000 and views >= min_views:
                    all_results.append({
                        "Title": title,
                        "Description": description,
                        "URL": video_url,
                        "Channel": channel_name,
                        "Views": views,
                        "Likes": likes,
                        "Comments": comments,
                        "Subscribers": subs,
                        "Engagement": round(engagement_rate, 2),
                        "Published": published_at[:10],
                        "Keyword": keyword
                    })

        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()

        # Sort results by views (descending)
        all_results = sorted(all_results, key=lambda x: x["Views"], reverse=True)

        # Display results
        if all_results:
            st.success(f"🎉 Found {len(all_results)} trending videos from rising channels!")
            
            # Display top performing keywords
            st.subheader("📊 Summary Statistics")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Videos Found", len(all_results))
            with col2:
                avg_views = sum(r["Views"] for r in all_results) // len(all_results)
                st.metric("Average Views", f"{avg_views:,}")
            with col3:
                avg_engagement = sum(r["Engagement"] for r in all_results) / len(all_results)
                st.metric("Avg Engagement", f"{avg_engagement:.2f}%")
            
            st.markdown("---")
            st.subheader("🏆 Top Trending Videos")
            
            # Display each result
            for idx, result in enumerate(all_results[:50], 1):  # Show top 50
                with st.expander(f"#{idx} - {result['Title']} ({result['Views']:,} views)"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"**📺 Channel:** {result['Channel']}")
                        st.markdown(f"**📝 Description:** {result['Description']}")
                        st.markdown(f"**🔗 URL:** [Watch Video]({result['URL']})")
                        st.markdown(f"**🔑 Keyword:** {result['Keyword']}")
                    
                    with col2:
                        st.markdown(f"**👁️ Views:** {result['Views']:,}")
                        st.markdown(f"**👍 Likes:** {result['Likes']:,}")
                        st.markdown(f"**💬 Comments:** {result['Comments']:,}")
                        st.markdown(f"**👥 Subscribers:** {result['Subscribers']:,}")
                        st.markdown(f"**📈 Engagement:** {result['Engagement']}%")
                        st.markdown(f"**📅 Published:** {result['Published']}")
                    
                    st.markdown("---")
        else:
            st.warning("⚠️ No results found matching your criteria. Try:")
            st.markdown("- Increasing the number of days")
            st.markdown("- Lowering the minimum views threshold")
            st.markdown("- The keywords might need adjustment for current trends")

    except Exception as e:
        st.error(f"❌ An error occurred: {e}")
        st.info("💡 Tip: Check your API key and ensure you haven't exceeded the daily quota.")
