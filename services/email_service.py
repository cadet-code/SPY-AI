import requests
import json
from datetime import datetime
from typing import Optional
from core.config import settings

class EmailService:
    def __init__(self):
        self.api_key = settings.resend_api_key
        self.base_url = "https://api.resend.com"
        self.from_email = "noreply@yourspa.com"  # Update with your verified domain
    
    async def send_email(self, to_email: str, subject: str, html_content: str, text_content: str = None):
        """Send email using Resend API"""
        
        if not self.api_key:
            print("⚠️ Resend API key not configured. Email not sent.")
            return False
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "from": self.from_email,
            "to": [to_email],
            "subject": subject,
            "html": html_content,
            "text": text_content or self._html_to_text(html_content)
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/emails",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                print(f"✅ Email sent successfully to {to_email}")
                return True
            else:
                print(f"❌ Failed to send email: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            return False
    
    def _html_to_text(self, html_content: str) -> str:
        """Convert HTML content to plain text"""
        # Simple HTML to text conversion
        import re
        text = re.sub(r'<[^>]+>', '', html_content)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _create_booking_confirmation_html(self, client_name: str, service_name: str, 
                                        appointment_datetime: datetime, price: float, 
                                        confirmation_code: str) -> str:
        """Create HTML email for booking confirmation"""
        
        formatted_date = appointment_datetime.strftime("%A, %B %d, %Y")
        formatted_time = appointment_datetime.strftime("%I:%M %p")
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Booking Confirmation - {settings.spa_name}</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .booking-details {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #667eea; }}
                .confirmation-code {{ background: #667eea; color: white; padding: 15px; border-radius: 5px; text-align: center; font-size: 18px; font-weight: bold; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
                .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✨ {settings.spa_name}</h1>
                    <p>Your appointment has been confirmed!</p>
                </div>
                
                <div class="content">
                    <h2>Hello {client_name},</h2>
                    <p>Thank you for choosing {settings.spa_name}! Your appointment has been successfully booked.</p>
                    
                    <div class="booking-details">
                        <h3>📅 Appointment Details</h3>
                        <p><strong>Service:</strong> {service_name}</p>
                        <p><strong>Date:</strong> {formatted_date}</p>
                        <p><strong>Time:</strong> {formatted_time}</p>
                        <p><strong>Duration:</strong> 60 minutes</p>
                        <p><strong>Total:</strong> ${price:.2f}</p>
                    </div>
                    
                    <div class="confirmation-code">
                        Confirmation Code: {confirmation_code}
                    </div>
                    
                    <h3>📍 Location</h3>
                    <p>{settings.spa_address}</p>
                    <p>Phone: {settings.spa_phone}</p>
                    
                    <h3>📋 Important Information</h3>
                    <ul>
                        <li>Please arrive 15 minutes before your appointment</li>
                        <li>Bring comfortable clothing</li>
                        <li>24-hour cancellation policy applies</li>
                        <li>Free parking available on-site</li>
                    </ul>
                    
                    <p>We look forward to providing you with an exceptional spa experience!</p>
                    
                    <p>Best regards,<br>The {settings.spa_name} Team</p>
                </div>
                
                <div class="footer">
                    <p>This email was sent to confirm your appointment at {settings.spa_name}</p>
                    <p>If you have any questions, please contact us at {settings.spa_phone}</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _create_manager_notification_html(self, service_name: str, appointment_datetime: datetime, 
                                        price: float, confirmation_code: str, client_details) -> str:
        """Create HTML email for manager notification"""
        
        formatted_date = appointment_datetime.strftime("%A, %B %d, %Y")
        formatted_time = appointment_datetime.strftime("%I:%M %p")
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>New Booking - {settings.spa_name}</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #28a745; color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .booking-details {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #28a745; }}
                .client-details {{ background: #e9ecef; padding: 15px; border-radius: 5px; margin: 15px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 New Booking Received</h1>
                    <p>{settings.spa_name}</p>
                </div>
                
                <div class="content">
                    <h2>New Appointment Booked</h2>
                    
                    <div class="booking-details">
                        <h3>📅 Appointment Details</h3>
                        <p><strong>Service:</strong> {service_name}</p>
                        <p><strong>Date:</strong> {formatted_date}</p>
                        <p><strong>Time:</strong> {formatted_time}</p>
                        <p><strong>Duration:</strong> 60 minutes</p>
                        <p><strong>Total:</strong> ${price:.2f}</p>
                        <p><strong>Confirmation Code:</strong> {confirmation_code}</p>
                    </div>
                    
                    <div class="client-details">
                        <h3>👤 Client Information</h3>
                        <p><strong>Name:</strong> {client_details.client_name}</p>
                        <p><strong>Email:</strong> {client_details.client_email}</p>
                        <p><strong>Phone:</strong> {client_details.client_phone}</p>
                        {f'<p><strong>Special Requests:</strong> {client_details.special_requests}</p>' if client_details.special_requests else ''}
                    </div>
                    
                    <p>This booking has been automatically added to your calendar and tracking system.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _create_inquiry_response_html(self, client_name: str, subject: str, response: str) -> str:
        """Create HTML email for inquiry response"""
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Response to your inquiry - {settings.spa_name}</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .response {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #667eea; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>💬 {settings.spa_name}</h1>
                    <p>Response to your inquiry</p>
                </div>
                
                <div class="content">
                    <h2>Hello {client_name},</h2>
                    <p>Thank you for contacting {settings.spa_name}. Here's our response to your inquiry:</p>
                    
                    <div class="response">
                        <h3>Re: {subject}</h3>
                        <p>{response}</p>
                    </div>
                    
                    <p>If you have any additional questions, please don't hesitate to reach out to us.</p>
                    
                    <p>Best regards,<br>The {settings.spa_name} Team</p>
                </div>
                
                <div class="footer">
                    <p>This email was sent in response to your inquiry at {settings.spa_name}</p>
                    <p>Contact us: {settings.spa_phone} | {settings.spa_address}</p>
                </div>
            </div>
        </body>
        </html>
        """

# Global email service instance
email_service = EmailService()

async def send_booking_confirmation(client_email: str, client_name: str, service_name: str, 
                                  appointment_datetime: datetime, price: float, 
                                  confirmation_code: str, is_manager: bool = False, 
                                  client_details = None):
    """Send booking confirmation email"""
    
    if is_manager:
        subject = f"New Booking: {service_name} - {appointment_datetime.strftime('%B %d, %Y')}"
        html_content = email_service._create_manager_notification_html(
            service_name, appointment_datetime, price, confirmation_code, client_details
        )
    else:
        subject = f"Booking Confirmation - {settings.spa_name}"
        html_content = email_service._create_booking_confirmation_html(
            client_name, service_name, appointment_datetime, price, confirmation_code
        )
    
    return await email_service.send_email(client_email, subject, html_content)

async def send_inquiry_response(client_email: str, client_name: str, subject: str, 
                              response: str, is_manager: bool = False):
    """Send inquiry response email"""
    
    if is_manager:
        email_subject = f"Manager Notification: {subject}"
        html_content = f"""
        <h2>Manager Notification</h2>
        <p><strong>From:</strong> {client_name} ({client_email})</p>
        <p><strong>Subject:</strong> {subject}</p>
        <p><strong>AI Response:</strong> {response}</p>
        """
    else:
        email_subject = f"Re: {subject} - {settings.spa_name}"
        html_content = email_service._create_inquiry_response_html(client_name, subject, response)
    
    return await email_service.send_email(client_email, email_subject, html_content)
