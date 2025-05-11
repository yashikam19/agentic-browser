![Python](https://img.shields.io/badge/Python-3.12+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.44%2B-brightgreen)
![Playwright](https://img.shields.io/badge/Playwright-1.51.0-yellow)
![autogen](https://img.shields.io/badge/autogen-0.8.5-orange)
![openai](https://img.shields.io/badge/openai-1.68.2-blueviolet)
![uv](https://img.shields.io/badge/uv-package%20manager-purple)
![MIT License](https://img.shields.io/badge/license-MIT-green)

# Agentic Browser

A powerful web automation tool that combines Playwright with AI agents to perform complex web interactions and data extraction tasks.

## 🚀 Features

- **AI-Powered Web Automation**: Uses AI agents to plan and execute web interactions
- **Smart DOM Parsing**: Efficient DOM parsing with unique element identification
- **Secure Credential Handling**: Safe management of login credentials
- **Multi-Agent System**: Collaborative agents for planning and execution
- **Streamlit Interface**: User-friendly web interface for interaction

## 🏗️ Architecture

The project consists of three main components:

1. **Playwright Manager** (`playwright_helper/`)
   - Handles browser automation
   - Manages DOM parsing and element interaction
   - Provides clean DOM representations

2. **Agent System** (`agents/`)
   - **Planner Agent**: Plans and breaks down tasks
   - **Browser Agent**: Executes web interactions
   - **User Proxy Agent**: Handles user verification

3. **Web Interface** (`app.py`)
   - Streamlit-based user interface
   - Task input and result visualization
   - Credential management

## 🛠️ Prerequisites

- Python 3.12+
- Node.js (for Playwright)
- OpenAI API key
- [Homebrew](https://brew.sh/) (for uv installation)

## ⚙️ Installation

1. Install uv using Homebrew:
   ```bash
   brew install uv
   ```

2. Clone the repository:
   ```bash
   git clone https://github.com/yashikam19/crustdata-agentic-browser.git
   cd crustdata-agentic-browser
   ```

3. Install dependencies and create virtual environment:
   ```bash
   # Install dependencies and create virtual environment
   uv sync
   
   # Activate virtual environment
   source .venv/bin/activate
   ```

4. Install Playwright browsers:
   ```bash
   playwright install
   ```

5. Set up environment variables:
   Create a `.env` file in the root directory:
   ```bash
   OPENAI_API_KEY="your_openai_api_key"
   ```

6. Configure Streamlit secrets:
   Create `.streamlit/secrets.toml`:
   ```toml
   [credentials]
   username = "your_username"
   password = "your_password"
   ```

## 🚀 Usage

1. Start the application:
   ```bash
   streamlit run app.py
   ```

2. Access the web interface at `http://localhost:8501`

3. Enter your task in the input field and submit

## 📝 Example Tasks

- Web scraping
- Form filling
- Data extraction
- Automated testing
- Multi-step workflows

## 🔒 Security

- Credentials are stored securely in Streamlit secrets
- API keys are managed through environment variables
- No sensitive data is logged or stored in plain text

## 🐛 Troubleshooting

Common issues and solutions:

1. **Browser Launch Issues**
   - Ensure Playwright browsers are installed
   - Check system requirements for browser compatibility

2. **API Key Errors**
   - Verify OpenAI API key in `.env` file
   - Check API key permissions and quota

3. **Credential Issues**
   - Verify credentials in `.streamlit/secrets.toml`
   - Check file permissions

4. **uv Installation Issues**
   - Ensure uv is properly installed via Homebrew
   - Check Python version compatibility (requires Python 3.12+)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For support, please open an issue in the GitHub repository or contact the maintainers.
