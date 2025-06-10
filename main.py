import os
from typing import Dict, List, Optional
import streamlit as st
from langchain_core.documents import Document
from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import OllamaLLM
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import base64
from typing import List, Dict
from email import message_from_bytes
from email.header import decode_header
from datetime import datetime
import pickle

# Define state for LangGraph
class State(Dict):
    credentials: Optional[Credentials] = None
    unread_emails: List[Dict] = []
    categorized_emails: Dict[str, List[Dict]] = {}
    documents: List[Document] = []
    summary: str = ""
    error: Optional[str] = None

    def __add__(self, other):
        if isinstance(other, dict):
            new_state = State(self.copy())
            new_state.update(other)
            return new_state
        return NotImplemented

    def __radd__(self, other):
        if isinstance(other, dict):
            new_state = State(other.copy())
            new_state.update(self)
            return new_state
        return NotImplemented

# Initialize LLM
llm = OllamaLLM(model="qwen2.5:latest", num_gpu=1)
output_parser = StrOutputParser()

# Define prompts
categorize_prompt = ChatPromptTemplate.from_template(
    """Analyze the following email and categorize it into one of these categories:
    - 'newsletters'
    - 'personal'
    - 'work'
    - 'promotions'
    - 'notifications'
    - 'social'
    - 'other'
    
    Email Subject: {subject}
    Email Sender: {sender}
    Email Snippet: {snippet}
    
    Return only the category name, nothing else."""
)

summary_prompt = ChatPromptTemplate.from_template(
    """Summarize the following email content in 2-3 sentences. Focus on key points and actions needed:
    
    From: {sender}
    Subject: {subject}
    Date: {date}
    Content: {content}
    
    Summary:"""
)

# Helper functions
def get_gmail_credentials() -> Optional[Credentials]:
    """Authenticate with Gmail using OAuth2"""
    SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
    creds = None
    
    try:
        # Load saved credentials if they exist
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, initiate OAuth2 flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for future use
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        return creds
    
    except Exception as e:
        st.error(f"Authentication failed: {e}")
        return None

def fetch_unread_emails(state: State) -> State:
    """Fetch unread emails from Gmail"""
    try:
        # Build the Gmail service
        gmail_service = build('gmail', 'v1', credentials=state['credentials'])
        
        # Search for messages
        results = gmail_service.users().messages().list(
            userId="me",
            q="is:unread",
            maxResults=20
        ).execute()
        
        emails = []
        
        if 'messages' in results:
            for msg in results['messages']:
                email_id = msg['id']
                try:
                    # Get full message details
                    message = gmail_service.users().messages().get(
                        userId="me",
                        id=email_id,
                        format="raw"
                    ).execute()
                    
                    # Parse the raw email
                    msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
                    mime_msg = message_from_bytes(msg_str)
                    
                    # Extract headers
                    subject = header_decode(mime_msg.get('Subject', ''))
                    sender = header_decode(mime_msg.get('From', ''))
                    date = datetime.fromtimestamp(int(message['internalDate'])/1000).strftime('%Y-%m-%d %H:%M:%S')
                    snippet = message.get('snippet', '')
                    
                    # Extract plain text content
                    plain_text_content = get_email_body(mime_msg)
                    
                    # Add to results
                    emails.append({
                        'id': email_id,
                        'subject': subject,
                        'sender': sender,
                        'snippet': snippet[:250],
                        'date': date,
                        'content': plain_text_content[:250] or snippet[:250]
                    })
                    
                except Exception as e:
                    print(f"Error processing email {email_id}: {str(e)}")
                    emails.append({
                        'id': email_id,
                        'subject': '[Error]',
                        'sender': '[Error]',
                        'snippet': f'Error processing email: {str(e)}',
                        'date': '',
                        'content': f'Error processing email: {str(e)}'
                    })
        
        return {'unread_emails': emails}
    
    except Exception as e:
        return {'error': f"Failed to fetch emails: {e}"}

def get_email_body(mime_msg) -> str:
    """Extract plain text body from email message."""
    plain_text = ""
    for part in mime_msg.walk():
        if part.get_content_type() == "text/plain":
            try:
                payload = part.get_payload(decode=True)
                charset = part.get_content_charset() or 'utf-8'
                plain_text += payload.decode(charset, errors='replace')
            except Exception as e:
                print(f"Error decoding part: {str(e)}")
    return plain_text.strip()

def header_decode(header: str) -> str:
    """Decode email headers that might be encoded."""
    try:
        decoded = []
        for part, encoding in decode_header(header):
            if isinstance(part, bytes):
                decoded.append(part.decode(encoding or 'utf-8', errors='replace'))
            else:
                decoded.append(part)
        return ' '.join(decoded)
    except:
        return str(header)

def categorize_emails(state: State) -> State:
    """Categorize emails using LLM"""
    try:
        categorized = {
            'newsletters': [],
            'personal': [],
            'work': [],
            'promotions': [],
            'notifications': [],
            'social': [],
            'other': []
        }
        
        chain = categorize_prompt | llm | output_parser
        
        for email in state['unread_emails']:
            category = chain.invoke({
                'subject': email['subject'],
                'sender': email['sender'],
                'snippet': email['snippet']
            })
            
            category = category.lower().strip()
            if category not in categorized:
                category = 'other'
            
            email['category'] = category
            categorized[category].append(email)
        
        return {'categorized_emails': categorized}
    
    except Exception as e:
        return {'error': f"Failed to categorize emails: {e}"}

def create_documents(state: State) -> State:
    """Create LangChain documents from emails"""
    try:
        documents = []
        
        for category, emails in state['categorized_emails'].items():
            for email in emails:
                metadata = {
                    'category': category,
                    'sender': email['sender'],
                    'subject': email['subject'],
                    'date': email['date'],
                    'email_id': email['id']
                }
                
                doc = Document(
                    page_content=email['content'],
                    metadata=metadata
                )
                
                documents.append(doc)
        
        return {'documents': documents}
    
    except Exception as e:
        return {'error': f"Failed to create documents: {e}"}

def summarize_emails(state: State) -> State:
    """Summarize email content"""
    try:
        chain = summary_prompt | llm | output_parser
        summaries = []
        
        for doc in state['documents']:
            summary = chain.invoke({
                'sender': doc.metadata['sender'],
                'subject': doc.metadata['subject'],
                'date': doc.metadata['date'],
                'content': doc.page_content
            })
            
            summaries.append({
                'category': doc.metadata['category'],
                'sender': doc.metadata['sender'],
                'subject': doc.metadata['subject'],
                'summary': summary,
                'email_id': doc.metadata['email_id']
            })
        
        summary_text = "📧 Email Summaries\n\n"
        
        for category, emails in state['categorized_emails'].items():
            if emails:
                summary_text += f"### {category.capitalize()} ({len(emails)})\n"
                
                for email in emails:
                    email_summary = next(
                        (s for s in summaries if s['email_id'] == email['id']),
                        {'summary': 'No summary available.'}
                    )
                    
                    summary_text += (
                        f"**From:** {email['sender']}\n"
                        f"**Subject:** {email['subject']}\n"
                        f"**Summary:** {email_summary['summary']}\n\n"
                    )
                    
        return {'summary': summary_text}
    
    except Exception as e:
        return {'error': f"Failed to summarize emails: {e}"}

# Create LangGraph workflow
workflow = StateGraph(State)
workflow.add_node("fetch_emails", fetch_unread_emails)
workflow.add_node("categorize_emails", categorize_emails)
workflow.add_node("create_documents", create_documents)
workflow.add_node("summarize_emails", summarize_emails)
workflow.set_entry_point("fetch_emails")
workflow.add_edge("fetch_emails", "categorize_emails")
workflow.add_edge("categorize_emails", "create_documents")
workflow.add_edge("create_documents", "summarize_emails")
workflow.add_edge("summarize_emails", END)

# Streamlit UI
def main():
    st.title("📧 Gmail Processing Agent")
    st.markdown("This agent fetches your unread Gmail messages, categorizes them, and provides summaries.")
    st.write("Click 'Process Emails' to start. A browser window will open for you to authenticate with Gmail.")
    
    if st.button("Process Emails"):
        with st.spinner("Authenticating and processing emails..."):
            initial_state = State()
            initial_state['credentials'] = get_gmail_credentials()
            
            if initial_state['credentials']:
                app = workflow.compile()
                result = app.invoke(initial_state)
                
                if 'error' in result:
                    st.error(result['error'])
                else:
                    st.success("Email processing complete!")
                    st.write("### Email Categories")
                    cols = st.columns(7)
                    for i, (category, emails) in enumerate(result['categorized_emails'].items()):
                        cols[i].metric(label=category.capitalize(), value=len(emails))
                    st.write("### Email Summaries")
                    st.markdown(result['summary'])
                    with st.expander("View Raw Email Data"):
                        st.json(result['unread_emails'])
            else:
                st.error("Failed to authenticate with Gmail")

if __name__ == "__main__":
    main()