# Gmail Processing Agent

## Description

Welcome to the **Gmail Processing Agent**, a Python application designed to automate the management and summarization of your unread Gmail emails. This tool fetches your unread emails, categorizes them into relevant groups (e.g., newsletters, personal, work), and provides concise summaries, all accessible through a user-friendly web interface built with [Streamlit](https://streamlit.io/). Ideal for anyone looking to streamline their email management, this project leverages advanced AI technologies to make sense of your inbox efficiently.

## Why Use This Project?

- **Save Time**: Automatically categorize and summarize unread emails, reducing the time spent on manual sorting.
- **Stay Organized**: Keep your inbox tidy with emails grouped into categories like newsletters, personal, work, and more.
- **AI-Powered Insights**: Use advanced language models to generate meaningful summaries and identify key actions.
- **User-Friendly**: Enjoy a simple Streamlit interface that makes managing emails intuitive and accessible.
- **Secure**: Utilizes OAuth2 for secure authentication with Gmail, ensuring your data remains private.

## Features

- **Secure Authentication**: Connects to Gmail using Google OAuth2 for safe and private access.
- **Email Fetching**: Retrieves up to 20 unread emails from your inbox.
- **Categorization**: Uses AI to sort emails into categories such as newsletters, personal, work, promotions, notifications, social, or other.
- **Summarization**: Generates 2-3 sentence summaries for each email, highlighting key points and actions.
- **User Interface**: Streamlit web app for easy interaction, including category metrics and detailed summaries.
- **Error Handling**: Robust error management to ensure smooth operation even with problematic emails.

## Installation

To set up the Gmail Processing Agent, follow these steps:

1. **Install Python 3.8 or Higher**:
   - Download and install Python from [Python.org](https://www.python.org/downloads/).
   - Verify installation:
     ```bash
     python --version
     ```

2. **Install Required Libraries**:
   - Install the necessary Python packages:
     ```bash
     pip install streamlit langchain-core langgraph langchain-ollama google-auth-oauthlib google-api-python-client base64 email datetime pickle
     ```

3. **Set up Google OAuth2 Credentials**:
   - Create a project in the [Google Developer Console](https://console.developers.google.com/).
   - Enable the Gmail API for your project.
   - Create OAuth 2.0 credentials (Desktop app type) and download the `credentials.json` file.
   - Place the `credentials.json` file in the same directory as `main.py`.

4. **Install and Set up Ollama**:
   - Install Ollama from [Ollama.com](https://ollama.com/).
   - Pull the required language model:
     ```bash
     ollama pull qwen2.5
     ```
   - Start Ollama:
     ```bash
     ollama serve
     ```

5. **Clone the Repository**:
   
   ```bash
     git clone https://github.com/armanjscript/Gmail-Processing-Agent.git
     ```
   - Navigate to the project directory:
     ```bash
     cd Gmail-Processing-Agent
     ```

6. **Run the Application**:
   - Launch the Streamlit app:
     ```bash
     streamlit run main.py
     ```

**Note**: Ensure a stable internet connection for initial setup and sufficient system resources (e.g., 16GB RAM, CPU/GPU) for running Ollama.

## Usage

1. **Launch the Application**:
   - Run `streamlit run main.py` to open the app in your default web browser.

2. **Authenticate with Gmail**:
   - Follow the OAuth2 authentication flow to grant access to your Gmail account.
   - Log in and authorize the app when prompted in the browser.

3. **Process Emails**:
   - Click the "Process Unread Emails" button to fetch and process up to 20 unread emails.

4. **View Results**:
   - The app displays:
     - A breakdown of email categories (e.g., number of newsletters, personal emails).
     - Summaries for each email, including key points and required actions.
     - Option to view raw email data for detailed inspection.

**Note**: Ensure your Gmail account has the necessary permissions and unread emails to process.

## Technologies Used

| Technology                  | Role                                                                 |
|-----------------------------|----------------------------------------------------------------------|
| **Python**                  | Primary programming language.                                        |
| **Streamlit**               | Creates the interactive web interface for user interaction.          |
| **LangGraph**               | Manages the workflow of email processing from fetching to summarizing.|
| **LangChain**               | Handles document creation and prompt management for AI interactions. |
| **OllamaLLM**               | Provides the language model for email categorization and summarization. |
| **google-auth-oauthlib**    | Handles OAuth2 authentication with Gmail.                            |
| **google-api-python-client**| Interacts with Gmail API to fetch unread emails.                      |
| **Email Library**           | Parses email content and headers.                                    |

## Contributing

Contributions are welcome! To contribute:
1. Fork the repository on [GitHub](https://github.com/).
2. Create a new branch for your changes.
3. Make modifications and ensure alignment with project goals.
4. Submit a pull request with a clear description.
5. For bug reports or feature requests, open an issue.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For questions or feedback, open an issue on [GitHub](https://github.com/armanjscript) or email [armannew73@gmail.com].