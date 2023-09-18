# Magista Backend
Magista Backend is the server for the Magista e-commerce platform built with **Django** and **Django Rest Framework**.

 - Magista Customer frontend repository is available [here](https://github.com/alirezabhr/magista_front_customer).
 - Magista Vendor frontend repository is available [here](https://github.com/alirezabhr/magista_front_vendor).

## Features:

 - User authentication - signup, login, verification via OTP
 - JWT tokens for authentication
 - Vendor accounts - online shops can create accounts and sync products from Instagram
 - Auto retrieve product images from Instagram and allow vendors to tag products
 - Vendors can add pricing, generate discount codes, and set shipping methods
 - Customers can add products to cart and pay invoices via Bank Gateway
 - Customers can track and check their order status
 - Vendor payouts and withdrawals
 - Payment integration with bank gateway APIs
 - SMS sending for OTP verification


## Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Migrate database models
python manage.py migrate

# Run development server
python manage.py runserver
```
