import openai
import re

which_model = "chatgpt"
which_model = "gpt3.5"

if which_model == "chatgpt":
    # Initialize a Chatbot instance with a session token
    try:
        session_token = "{ENTER_YOUR_CHATGPT_SESSION_TOKEN_HERE}"
        global chatbot
        chatbot = AsyncChatbot({"session_token": session_token})
    except Exception as e:
        print(e)
        exit()
    # chatbot = AsyncChatbot({"session_token": session_token})

def chatgptapi(prompt):
    import openai

    openai.api_key = ""
    openai.api_base = "https://free.churchless.tech/v1"

    import os

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
        )

    return response.choices[0].message.content

# Define a function to split text into 3000-word chunks, stopping at the end of the last sentence
def chunk_text(text, MAX_CHUNK_LENGTH):
    # Split the text into words using whitespace as the delimiter
    words = text.split()
    
    # Initialize variables
    chunks = []
    current_chunk = ""
    current_chunk_word_count = 0
    
    # Loop through each word in the text
    for word in words:
        # Add the current word to the current chunk and update the word count
        current_chunk += word + " "
        current_chunk_word_count += 1
        
        # If adding the current word to the current chunk would exceed 3000 words and the current
        # word is the end of a sentence, add the current chunk to the list of chunks and start a new chunk
        if current_chunk_word_count == MAX_CHUNK_LENGTH:
            print("current_chunk_word_count: ", current_chunk_word_count)
        # if current_chunk_word_count > MAX_CHUNK_LENGTH and re.match(r'[.!?]', word):
            # input("Wait...")
            chunks.append(current_chunk)
            current_chunk = ""
            current_chunk_word_count = 0
    
    # Add the last chunk to the list of chunks
    chunks.append(current_chunk)
    
    return chunks


# Define a function to summarize a chunk of text using the OpenAI API
def summarize_chunk(chunk, prompt_text):  
    # return summary
    prompt_text = prompt_text + chunk
    print("chunk: ", prompt_text)
    print("len(chunk): ", len(prompt_text))

    if which_model == "chatgpt":
        response = chatbot.ask(prompt_text)
        response = response

    if which_model == "gpt3.5":
        response = chatgptapi(prompt_text)
    
    return response

# Define a function to summarize a long text using the OpenAI API by splitting it into chunks
def summarize_long_text(long_text, max_chunk_length, final_max_tokens):
    # Split the long text into chunks
    chunks = chunk_text(long_text, max_chunk_length)
    
    user_input = input("\nAsk a question about the text or press enter to summarize the text: ")
    if user_input == "":
        prompt_text = "Summarize this text using bullet points:\n\n"
    else:
        prompt_text = f"{user_input}\n\n"

    # Summarize each chunk using the OpenAI API
    summaries = [summarize_chunk(chunk, prompt_text) for chunk in chunks]
    [print(f"\n\nSummary {summary_num}: ", summaries) for summary_num, summaries in enumerate(summaries, start=1)]
    
    # Combine the summaries into a new, shorter text
    combined_summary = " ".join(summaries)

    # Summarize the combined summary using the OpenAI API again
    final_summary = summarize_chunk(combined_summary, prompt_text)

    return final_summary

# Open the file in read mode
with open('text to summarize.txt', 'r', encoding="cp1252", errors="replace") as file:
    # Read the entire file as a string
    file_contents = file.read()

from youtube_transcript_api import YouTubeTranscriptApi
import re

def get_transcript(video_url):
    # Fetch transcript from API
    video_id = video_url.split("watch?v=")[1]
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    return transcript

def is_youtube_link(link: str) -> bool:
    # The regex doesn't account for the mobile links
    link = link.replace("https://m.", "https://")
    # Works for any youtube link
    pattern = r'^(https?://)?(www\.)?(youtube\.com|youtu\.be)/(watch\?v=)?[a-zA-Z0-9_-]{11}$'
    # Returns True if the link is a valid youtube link
    return bool(re.match(pattern, link))

def get_video_transcript(video_url):
    if is_youtube_link(video_url):
        transcript = get_transcript(video_url)
        text_transcript = ''

        # Convert transcript with timestamp to transcript with text only
        for d in transcript:
            if isinstance(d, dict):
                text_transcript += d['text'] + ' '

    return text_transcript

# Check if the file_contents is a youtube link and nothing else
if is_youtube_link(file_contents):
    file_contents = get_video_transcript(file_contents)

if which_model == "chatgpt":
    max_chunk_length = 1500
    final_max_tokens = 50
if which_model == "gpt3.5":
    max_chunk_length = 1800
    final_max_tokens = 100

final_summary = summarize_long_text(file_contents, max_chunk_length, final_max_tokens)

print(f"\nFinal summary: {final_summary}")

# Ask for any follow up questions
user_input = input("\nAsk a follow up question about the text or press enter to exit: ")
while user_input != "":
    if which_model == "chatgpt":
        response = chatbot.ask(user_input)
        response = response
    if which_model == "gpt3.5":
        response = chatgptapi(user_input)
    print(f"\n{response}")

    user_input = input("\nAsk a follow up question about the text or press enter to exit: ")
