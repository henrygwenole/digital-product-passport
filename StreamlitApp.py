import streamlit as st
import json
import qrcode
from PIL import Image
import io
import os

# Page configuration
st.set_page_config(
    page_title="Digital Product Passport",
    page_icon="🥫",
    layout="wide"
)

# Load product data
@st.cache_data
def load_product_data():
    with open('data/products.json', 'r') as f:
        return json.load(f)

try:
    products = load_product_data()
except Exception as e:
    st.error(f"Error loading product data: {e}")
    st.stop()

# App title and description
st.title("🥫 Digital Product Passport")
st.subheader("Food Can Compliance Tracking System")

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Product Lookup", "Generate QR Codes", "About"])

if page == "Home":
    st.write("## Welcome to the Digital Product Passport System")
    st.write("""
    This application helps track compliance information for food can products on the production line.
    
    ### Features:
    - Scan QR codes to access product compliance information
    - Generate QR codes for new products
    - Check compliance against industry standards
    - Track sustainability metrics
    
    ### How to use:
    1. Navigate to the 'Product Lookup' page
    2. Enter a QR code ID or select a product from the dropdown
    3. View detailed compliance information
    """)
    
    # Display sample products
    st.write("## Sample Products")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### Lentil Soup Variants")
        for product in products[:6]:  # First 6 are lentil soup variants
            st.write(f"- {product['name']} - {product['variant']} (QR Code: {product['qr_code_id']})")
    
    with col2:
        st.write("### Baked Beans Variants")
        for product in products[6:]:  # Last 6 are baked beans variants
            st.write(f"- {product['name']} - {product['variant']} (QR Code: {product['qr_code_id']})")

elif page == "Product Lookup":
    st.write("## Product Lookup")
    
    # Create two columns for lookup methods
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### Lookup by QR Code ID")
        qr_code_id = st.text_input("Enter QR Code ID (e.g., LS001, BB003):")
    
    with col2:
        st.write("### Select from Product List")
        product_options = [f"{p['name']} - {p['variant']} ({p['qr_code_id']})" for p in products]
        selected_product = st.selectbox("Choose a product:", [""] + product_options)
        
        if selected_product:
            qr_code_id = selected_product.split("(")[1].split(")")[0]
    
    if qr_code_id:
        # Find the product that matches the QR code ID
        found_product = None
        for product in products:
            if product['qr_code_id'] == qr_code_id:
                found_product = product
                break
        
        if found_product:
            # Create two columns for layout
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Display product information
                st.subheader(f"{found_product['name']} - {found_product['variant']}")
                
                # Metadata section
                st.write("### Product Details")
                details_col1, details_col2 = st.columns(2)
                with details_col1:
                    st.write(f"**Product ID:** {found_product['product_id']}")
                    st.write(f"**QR Code ID:** {found_product['qr_code_id']}")
                    st.write(f"**Batch Number:** {found_product['batch_number']}")
                
                with details_col2:
                    st.write(f"**Manufacturing Date:** {found_product['manufacturing_date']}")
                    st.write(f"**Expiration Date:** {found_product['expiration_date']}")
                
                # Materials
                st.write("### Materials")
                for material, description in found_product['materials'].items():
                    st.write(f"**{material}:** {description}")
                
                # Two columns for compliance and sustainability
                comp_col, sust_col = st.columns(2)
                
                with comp_col:
                    # Compliance
                    st.write("### Compliance Standards")
                    for standard in found_product['compliance_standards']:
                        st.write(f"- {standard}")
                
                with sust_col:
                    # Sustainability
                    st.write("### Sustainability Metrics")
                    for metric, value in found_product['sustainability_metrics'].items():
                        st.write(f"**{metric}:** {value}")
                
                # Traceability
                st.write("### Traceability Information")
                for info, value in found_product['traceability'].items():
                    st.write(f"**{info}:** {value}")
            
            with col2:
                # Generate QR code for display
                qr = qrcode.QRCode(
                    version=1,
                    box_size=10,
                    border=5
                )
                qr.add_data(found_product['qr_code_id'])
                qr.make(fit=True)
                
                img = qr.make_image(fill_color="black", back_color="white")
                
                # Convert PIL image to bytes
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                
                # Display QR code
                st.image(buf.getvalue(), caption=f"QR Code for {found_product['product_id']}", width=200)
                
                # Create download button for QR code
                st.download_button(
                    label="Download QR Code",
                    data=buf.getvalue(),
                    file_name=f"{found_product['qr_code_id']}_QR.png",
                    mime="image/png"
                )
            
            # Compliance checklist
            st.write("### Compliance Checklist")
            
            # Use columns to display checklist in a more compact way
            checklist_cols = st.columns(2)
            
            for i, check in enumerate(found_product['compliance_checklist']):
                col_idx = i % 2
                with checklist_cols[col_idx]:
                    st.checkbox(check, key=f"{found_product['product_id']}_{i}")
        
        else:
            st.error('Product not found. Please enter a valid QR Code ID.')

elif page == "Generate QR Codes":
    st.write("## QR Code Generator")
    
    # Allow generating QR codes for all products or specific ones
    option = st.radio("Generate QR codes for:", ["All Products", "Specific Product"])
    
    if option == "All Products":
        if st.button("Generate All QR Codes"):
            # Create a directory for QR codes if it doesn't exist
            os.makedirs("qr_codes", exist_ok=True)
            
            # Create progress bar
            progress_bar = st.progress(0)
            
            # Display all QR codes in a grid
            cols = st.columns(3)
            
            for i, product in enumerate(products):
                qr = qrcode.QRCode(
                    version=1,
                    box_size=10,
                    border=5
                )
                qr.add_data(product['qr_code_id'])
                qr.make(fit=True)
                
                img = qr.make_image(fill_color="black", back_color="white")
                
                # Save to file
                img.save(f"qr_codes/{product['qr_code_id']}.png")
                
                # Display in the appropriate column
                col_idx = i % 3
                with cols[col_idx]:
                    # Convert PIL image to bytes for display
                    buf = io.BytesIO()
                    img.save(buf, format="PNG")
                    st.image(buf.getvalue(), caption=f"{product['name']} - {product['variant']}")
                    st.write(f"QR Code ID: {product['qr_code_id']}")
                
                # Update progress bar
                progress_bar.progress((i + 1) / len(products))
            
            st.success(f"Generated {len(products)} QR codes in the 'qr_codes' directory.")
    
    else:  # Specific Product
        # Create product selector
        product_options = [f"{p['name']} - {p['variant']} ({p['qr_code_id']})" for p in products]
        selected_product = st.selectbox("Choose a product to generate QR code:", product_options)
        
        if selected_product and st.button("Generate QR Code"):
            qr_code_id = selected_product.split("(")[1].split(")")[0]
            
            # Find product data
            found_product = None
            for product in products:
                if product['qr_code_id'] == qr_code_id:
                    found_product = product
                    break
            
            if found_product:
                # Generate QR code
                qr = qrcode.QRCode(
                    version=1,
                    box_size=10,
                    border=5
                )
                qr.add_data(found_product['qr_code_id'])
                qr.make(fit=True)
                
                img = qr.make_image(fill_color="black", back_color="white")
                
                # Create directory if needed
                os.makedirs("qr_codes", exist_ok=True)
                
                # Save to file
                img.save(f"qr_codes/{found_product['qr_code_id']}.png")
                
                # Convert PIL image to bytes for display
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                
                # Display QR code
                st.image(buf.getvalue(), caption=f"{found_product['name']} - {found_product['variant']}", width=300)
                
                # Create download button
                st.download_button(
                    label="Download QR Code",
                    data=buf.getvalue(),
                    file_name=f"{found_product['qr_code_id']}_QR.png",
                    mime="image/png"
                )
                
                st.success(f"QR code for {found_product['name']} - {found_product['variant']} generated successfully.")

else:  # About page
    st.write("## About Digital Product Passport")
    st.write("""
    ### Purpose
    The Digital Product Passport system is designed to track compliance information for food can products 
    throughout the production line. By scanning QR codes, production staff can quickly access detailed 
    information about materials, compliance standards, sustainability metrics, and traceability.
    
    ### Benefits
    - **Regulatory Compliance**: Easily verify that products meet FDA, EU, and other regulatory requirements
    - **Sustainability Tracking**: Monitor environmental impact metrics across product lines
    - **Quality Assurance**: Track batch information and inspection history
    - **Supply Chain Transparency**: Access detailed information about raw material suppliers
    
    ### Technology
    This application is built using:
    - Streamlit for the web interface
    - QR codes for product identification
    - JSON data structure for product information storage
    
    ### Deployment
    The system can be deployed on GitHub and accessed via Streamlit Cloud for easy access from any device 
    on the production floor.
    """)
    
    # Add contact information
    st.write("### Contact Information")
    st.write("For more information about the Digital Product Passport system, please contact:")
    st.write("Email: productpassport@example.com")
    st.write("Support: +1 (555) 123-4567")

# Add a footer
st.markdown("---")
st.markdown("© 2025 Digital Product Passport | Food Can Compliance System")