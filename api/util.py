# utils.py
from lxml import etree
from .models import Invoice
import qrcode

def generate_invoice_xml(invoice):
    # Creating XML root
    namespaces = {
        "": "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
    }
    
    invoice_element = etree.Element("Invoice", nsmap=namespaces)
    
    # Invoice general info
    etree.SubElement(invoice_element, "cbc:ID").text = invoice.invoice_number
    etree.SubElement(invoice_element, "cbc:IssueDate").text = invoice.date_issued.strftime('%Y-%m-%d')
    etree.SubElement(invoice_element, "cbc:DocumentCurrencyCode").text = "SAR"
    
    # Seller Information
    seller_party = etree.SubElement(invoice_element, "cac:AccountingSupplierParty")
    seller_party_name = etree.SubElement(seller_party, "cbc:Name")
    seller_party_name.text = invoice.seller_name
    seller_vat = etree.SubElement(seller_party, "cbc:CompanyID", schemeID="SA")
    seller_vat.text = invoice.seller_vat_number

    # Buyer Information
    buyer_party = etree.SubElement(invoice_element, "cac:AccountingCustomerParty")
    buyer_party_name = etree.SubElement(buyer_party, "cbc:Name")
    buyer_party_name.text = invoice.buyer_name
    buyer_vat = etree.SubElement(buyer_party, "cbc:CompanyID", schemeID="SA")
    buyer_vat.text = invoice.buyer_vat_number
    
    # Invoice Line Items (you can add more as needed)
    line_item = etree.SubElement(invoice_element, "cac:InvoiceLine")
    etree.SubElement(line_item, "cbc:ID").text = "1"
    etree.SubElement(line_item, "cbc:InvoicedQuantity", unitCode="C62").text = "1"
    etree.SubElement(line_item, "cbc:LineExtensionAmount", currencyID="SAR").text = str(invoice.subtotal)

    # Tax Information
    tax_total = etree.SubElement(invoice_element, "cac:TaxTotal")
    etree.SubElement(tax_total, "cbc:TaxAmount", currencyID="SAR").text = str(invoice.tax_amount)

    # Legal Monetary Totals
    monetary_total = etree.SubElement(invoice_element, "cac:LegalMonetaryTotal")
    etree.SubElement(monetary_total, "cbc:LineExtensionAmount", currencyID="SAR").text = str(invoice.subtotal)
    etree.SubElement(monetary_total, "cbc:TaxExclusiveAmount", currencyID="SAR").text = str(invoice.subtotal)
    etree.SubElement(monetary_total, "cbc:TaxInclusiveAmount", currencyID="SAR").text = str(invoice.total_amount)
    etree.SubElement(monetary_total, "cbc:PayableAmount", currencyID="SAR").text = str(invoice.total_amount)

    # Convert to a string
    xml_string = etree.tostring(invoice_element, pretty_print=True, encoding="UTF-8").decode()
    return xml_string


# utils.py (continued)
def generate_qr_code(invoice):
    qr_data = f"VAT:{invoice.seller_vat_number}|Total:{invoice.total_amount}|Date:{invoice.date_issued}|Invoice:{invoice.invoice_number}"
    qr = qrcode.make(qr_data)
    qr_path = f"media/qr_codes/{invoice.invoice_number}.png"
    qr.save(qr_path)
    return qr_path


# utils.py (continued)
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization

def sign_invoice_xml(xml_data):
    # Load private key (ensure it's securely stored)
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    
    # Sign the XML
    signature = private_key.sign(
        xml_data.encode(),
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    
    return signature
