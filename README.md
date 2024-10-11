# Café Aroma

Welcome to Café Aroma, a cozy online platform designed to bring the warmth of your favorite café directly to your home. Our website offers a delightful selection of coffee products, user-friendly features for a seamless ordering experience, and a commitment to quality.

Table of Contents
Features
Technologies Used
Installation
Usage

Features
User Registration and Authentication: Custom user model for secure login and registration.
Product Showcase: Browse a curated selection of premium coffee products with detailed descriptions.
Cart Functionality: Add products to your cart and manage your orders with ease.
Order Management: Users can place orders and track their status.
Payment Integration: Seamless payment processing through Razorpay.
Responsive Design: Optimized for mobile and desktop viewing, ensuring a smooth user experience.
Technologies Used
Backend: Django
Frontend: HTML, CSS 
Database: SQLite
Payment Gateway: Razorpay
Others: Git, GitHub
Installation
To set up the Café Aroma project locally, follow these steps:

Clone the repository:

bash
Copy code
git clone https://github.com/yourusername/cafe-aroma.git
Navigate to the project directory:

bash
Copy code
cd cafe-aroma
Install dependencies:

bash
Copy code
python -m pip install -r requirements.txt
Run database migrations:

bash
Copy code
python manage.py migrate
Create a superuser (for admin access):

bash
Copy code
python manage.py createsuperuser
Start the development server:

bash
Copy code
python manage.py runserver
Access the application: Open your web browser and go to http://127.0.0.1:8000/.

Usage
Navigate through the product listings, select your desired coffee products, and add them to your cart.
Proceed to checkout to complete your order and make payments through Razorpay.
Use the admin panel to manage products view orders, users, and manage delivery status at ease!. 
