import streamlit as st
import os
import fal_client
import requests

# Set up API key from Streamlit secrets
if "FAL_KEY" not in st.secrets:
    st.error("API Key not found. Please add `FAL_KEY` to your Streamlit secrets.")
    st.stop()
else:
    os.environ["FAL_KEY"] = st.secrets["FAL_KEY"]

# App title
st.title("✨ Seedream 4.0 Text-to-Image Generator")
st.caption("Generate high-quality images from text prompts using ByteDance's latest model")

# Input section
with st.form("generation_form"):
    prompt = st.text_area(
        "📝 Enter your prompt",
        placeholder="A futuristic cityscape at sunset with neon lights and flying cars",
        help="Describe your image in detail. Max 500 characters",
        max_chars=500
    )
    
    # Image size options
    size_options = {
        "Square HD (1024x1024)": "square_hd",
        "Portrait (4:3)": "portrait_4_3",
        "Landscape (16:9)": "landscape_16_9",
        "Custom Dimensions": "custom"
    }
    selected_size = st.radio("📏 Image Size", list(size_options.keys()))
    
    if size_options[selected_size] == "custom":
        col1, col2 = st.columns(2)
        with col1:
            width = st.number_input("Width", min_value=1024, max_value=4096, value=1024, step=1)
        with col2:
            height = st.number_input("Height", min_value=1024, max_value=4096, value=1024, step=1)
        image_size = {"width": width, "height": height}
    else:
        image_size = size_options[selected_size]
    
    # Number of images
    num_images = st.slider("🖼️ Number of Images", 1, 4, 1)
    
    # Advanced options
    with st.expander("⚙️ Advanced Options"):
        seed = st.text_input("🎲 Seed (optional)", help="Leave blank for random seed")
        safety_enabled = st.checkbox("Enable Safety Checker", value=False, 
                                    help="Disable for unrestricted generation (required for most creative tasks)")
    
    # Generate button
    submitted = st.form_submit_button("✨ Generate Images", use_container_width=True)

# Handle generation
if submitted:
    if not prompt.strip():
        st.error("Please enter a prompt 🚫")
    else:
        with st.spinner("Generating images... 🌈 This may take 10-30 seconds"):
            try:
                # Configure parameters
                args = {
                    "prompt": prompt,
                    "image_size": image_size,
                    "num_images": num_images,
                    "max_images": 1,
                    "enable_safety_checker": safety_enabled,
                    "seed": int(seed) if seed else None,
                    "sync_mode": True
                }
                
                # Call API
                result = fal_client.subscribe(
                    "fal-ai/bytedance/seedream/v4/text-to-image",
                    arguments=args
                )
                
                # Display results
                st.subheader("🎨 Generated Images")
                if result.get('seed'):
                    st.info(f"🔑 Seed used: `{result['seed']}`")
                
                # Display images
                cols = st.columns(num_images)
                for idx, img_data in enumerate(result['images']):
                    with cols[idx]:
                        st.image(img_data['url'], use_container_width=True)
                        st.caption("Click to open full image")
                        # Download link
                        st.markdown(
                            f'[📥 Download Image]({img_data["url"]})',
                            unsafe_allow_html=True
                        )
                
                st.success("✅ Generation complete! 😊")
                
            except Exception as e:
                st.error(f"❌ API Error: {str(e)}")
                st.warning("Make sure your API key is valid and you've entered a valid prompt")

# Footer
st.markdown("---")
st.caption("Powered by [ByteDance Seedream 4.0](https://fal.ai/models/bytedance/seedream/v4/text-to-image) | © 2024 fal.ai")
