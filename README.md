Money Tracker AI

Overview
Money Tracker AI is a FastAPI-based application designed to assist users in managing their personal finances. The application leverages the OpenRouter AI service to provide intelligent financial insights and assistance.

Features
- Expense Tracking: Help users track their expenses and income.
- Financial Insights: Provide analysis related to personal finance.
- Investment Suggestions: Suggest ways to improve financial habits and manage investments effectively.
- Budgeting Assistance: Answer questions about budgeting, savings, taxes, and money management specific to Indonesia.

Installation
1. Clone the repository:
   git clone https://github.com/yourusername/money-tracker-ai.git
   cd money-tracker-ai
2. Install dependencies using Make:
   make install

Configuration
- Create a .env file in the root directory:
   cp .env.example .env
- Edit the .env file to set environment variables:
   OPENROUTER_API_KEY=your_openrouter_api_key
   OPENROUTER_API_URL=your_openrouter_api_url

Running the Application
To start the application, run:
   make run

Usage
- Send a POST request to /api/chat/ with a JSON payload containing the user's message and an optional model override.

Testing
Run the tests using:
   make test

Linting and Formatting
Use Ruff for linting and formatting:
   make lint
   make format

License
This project is licensed under the MIT License. See the LICENSE file for details.

Acknowledgments
- OpenRouter AI for providing the AI capabilities.
- FastAPI for the web framework.