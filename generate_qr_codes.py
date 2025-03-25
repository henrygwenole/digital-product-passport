import json
import qrcode
import os
from PIL import Image, ImageDraw, ImageFont

def generate_standalone_qr_codes():
    """
    Generate QR codes that contain only the product identifier.
    These QR codes don't need internet access or a web app to be useful.
    """
    # Create output directory if it doesn't exist
    os.makedirs("qr_codes", exist_ok=True)
    
    # Load product data
    with open('data/products.json', 'r') as f:
        products = json.load(f)
    
    print(f"Generating QR codes for {len(products)} products...")
    
    # Generate QR code for each product
    for product in products:
        # Get product info
        qr_code_id = product['qr_code_id']
        product_name = product['name']
        variant = product['variant']
        
        # Create QR code with just the product ID
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_code_id)
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to RGB mode for adding text
        qr_img = qr_img.convert('RGB')
        
        # Create a larger image with space for text
        width, height = qr_img.size
        new_img = Image.new('RGB', (width, height + 80), color='white')
        new_img.paste(qr_img, (0, 0))
        
        # Add text below QR code
        draw = ImageDraw.Draw(new_img)
        
        # Try to use a nice font, fall back to default if not available
        try:
            font = ImageFont.truetype("arial.ttf", 18)
        except IOError:
            font = ImageFont.load_default()
            
        # Add product info text
        draw.text((10, height + 10), f"ID: {qr_code_id}", fill="black", font=font)
        draw.text((10, height + 35), f"{product_name} - {variant}", fill="black", font=font)
        
        # Save QR code
        filename = f"qr_codes/{qr_code_id}.png"
        new_img.save(filename)
        print(f"Created QR code: {filename}")
    
    print("All QR codes generated successfully!")


def generate_offline_reference_guide():
    """
    Generate a printable reference guide with all product information
    that can be used alongside the QR codes.
    """
    # Load product data
    with open('data/products.json', 'r') as f:
        products = json.load(f)
    
    # Create reference guide file
    with open("product_reference_guide.md", "w") as f:
        f.write("# Product Reference Guide\n\n")
        f.write("This document contains all product information referenced by QR codes.\n\n")
        
        # Group products by type
        lentil_soups = [p for p in products if p['qr_code_id'].startswith('LS')]
        baked_beans = [p for p in products if p['qr_code_id'].startswith('BB')]
        
        # Write each product group
        f.write("## Lentil Soup Products\n\n")
        for product in lentil_soups:
            write_product_info(f, product)
        
        f.write("## Baked Beans Products\n\n")
        for product in baked_beans:
            write_product_info(f, product)
    
    print("Reference guide generated: product_reference_guide.md")


def write_product_info(file, product):
    """Write detailed product information to the file."""
    file.write(f"### {product['name']} - {product['variant']}\n\n")
    file.write(f"**QR Code ID:** {product['qr_code_id']}\n\n")
    file.write(f"**Product ID:** {product['product_id']}\n\n")
    file.write(f"**Batch Number:** {product['batch_number']}\n\n")
    file.write(f"**Manufacturing Date:** {product['manufacturing_date']}\n\n")
    file.write(f"**Expiration Date:** {product['expiration_date']}\n\n")
    
    # Materials
    file.write("#### Materials\n\n")
    for material, description in product['materials'].items():
        file.write(f"- **{material}:** {description}\n")
    file.write("\n")
    
    # Compliance
    file.write("#### Compliance Standards\n\n")
    for standard in product['compliance_standards']:
        file.write(f"- {standard}\n")
    file.write("\n")
    
    # Sustainability
    file.write("#### Sustainability Metrics\n\n")
    for metric, value in product['sustainability_metrics'].items():
        file.write(f"- **{metric}:** {value}\n")
    file.write("\n")
    
    # Traceability
    file.write("#### Traceability Information\n\n")
    for info, value in product['traceability'].items():
        file.write(f"- **{info}:** {value}\n")
    file.write("\n")
    
    # Compliance checklist
    file.write("#### Compliance Checklist\n\n")
    for check in product['compliance_checklist']:
        file.write(f"- [ ] {check}\n")
    file.write("\n")
    file.write("---\n\n")


if __name__ == "__main__":
    generate_standalone_qr_codes()
    generate_offline_reference_guide()
    print("Process completed successfully!")