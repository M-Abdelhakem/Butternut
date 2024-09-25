# Peppercorn - Email Marketing Platform 📧✨

Welcome to **Peppercorn**, your all-in-one, user-friendly email marketing platform! Designed to help businesses create, manage, and deliver personalized email campaigns effortlessly. Leveraging the power of **AI-generated content** with **OpenAI GPT**, **AWS SES** for seamless email delivery, and **Stripe** for subscription management, Peppercorn provides a robust, scalable solution for businesses looking to meaningfully engage their customers.

---

## 🚀 **Key Features**

### 🔐 **User Onboarding & Authentication**
- **Secure Registration**: Users register with their email and a strong password.
- **JWT-Based Authentication**: Ensures secure login sessions.
- **Password Recovery**: Forgot your password? Recover it via email.

### 👥 **Customer Management**
- **Dynamic Customer List**: Easily manage, edit, and search through your customer database.
- **Bulk Upload**: Upload customer data using CSV files for seamless integration.
- **Editing and Deletion**: Modify customer data or delete them in bulk with a simple click.

### ✉️ **AI-Powered Email Generation**
- **OpenAI GPT Integration**: Generate personalized email content by simply providing a prompt and business context.
- **Multiple Email Styles**: Choose from short, long, formal, or informal versions.
- **Context-Aware Emails**: Create emails tailored to individual customer needs and preferences.

### 📤 **Email Delivery with AWS SES**
- **High Deliverability**: Ensure that emails reach the inbox, not the spam folder.
- **Batch Sending**: Send personalized emails to hundreds or thousands of customers at once.

### 💳 **Subscription & Payment Management via Stripe**
- **Smooth Subscription Flow**: Users can subscribe to **Basic** or **Premium** plans via Stripe.
- **Automated Subscription Tracking**: The platform automatically checks subscription status before generating or sending emails.

### ✅ **Success & Cancel Pages**
- **Success Flow**: Users are redirected to a success page after completing a Stripe payment.
- **Cancel Flow**: If payment is canceled, users are redirected to a notification page and prompted to try again.

---

## 📚 **How It Works**

1. **Register & Login**: Sign up with a secure email and password, and fill in your profile information.
2. **Manage Your Customers**: Upload customer lists, edit or delete customer data as needed.
3. **Create Personalized Emails**: Use OpenAI GPT to generate emails by entering a custom prompt.
4. **Send Emails**: Deliver your generated emails to your customers via AWS SES.
5. **Subscription Handling**: Use Stripe to manage your subscription, and access premium features like bulk email sending.
6. **Track Subscription Status**: The platform checks subscription validity before allowing you to send emails.

---

## 💻 **How We Built It**

**Backend**:
- **FastAPI**: Provides a fast and secure backend API.
- **MongoDB**: Stores user, customer, and subscription data.

**Frontend**:
- **HTML/CSS/JavaScript**: For a responsive and user-friendly experience.
- **CKEditor**: Allows users to format and customize their emails easily.

**Integrations**:
- **OpenAI GPT API**: For generating personalized email content.
- **AWS SES**: For sending reliable and high-deliverability emails.
- **Stripe API**: For managing subscription plans and payments.

---

## 🔧 **Setting Up Locally**

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-repo/peppercorn.git
   cd peppercorn
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   - Create a `.env` file with your **OpenAI API Key**, **AWS SES credentials**, **MongoDB URI**, and **Stripe API Keys**.

4. **Run the server**:
   ```bash
   uvicorn main:app --reload
   ```

5. **Access the platform**:
   - Open `http://localhost:8000` in your browser to access the application.

---

## 🔒 **Security Features**

- **JWT Token Authentication**: Keeps user sessions secure.
- **Strong Password Enforcement**: Protects user accounts from unauthorized access.
- **Email Verification**: Ensures only valid users can use the platform.
- **Stripe Security**: All payment processing is securely handled by Stripe.

---

## 🛠️ **Technology Stack**

- **Backend**: FastAPI, Python
- **Database**: MongoDB
- **Frontend**: HTML, CSS, JavaScript
- **Email Sending**: AWS SES
- **AI Integration**: OpenAI GPT API
- **Subscription Management**: Stripe API

---

## 🌟 **What’s Next?**

- **Deeper Personalization**: Add features for further customization based on user-specific factors (age, health conditions, etc.).
- **AI Assistant Integration**: Future updates will integrate with AI assistants like Siri and Alexa for hands-free control.
- **Enhanced Tracking**: Incorporate more in-depth analysis and tracking for health-conscious users.
