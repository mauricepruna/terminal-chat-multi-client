import os
import readline
import sys
import threading
import time

import anthropic
from dotenv import load_dotenv
from google import genai
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Configure readline for better input experience
readline.set_startup_hook(None)
readline.parse_and_bind("tab: complete")
readline.parse_and_bind("set editing-mode emacs")  # Enable emacs-style editing (Ctrl+A, Ctrl+E, etc.)
readline.parse_and_bind("set bell-style none")     # Disable terminal bell

# Initialize clients
try:
    openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
except KeyError:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

try:
    anthropic_client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
except KeyError:
    raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

try:
    gemini_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
except KeyError:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

# Global variable for stopping the print_dots function
stop_printing = False


def print_dots():
    global stop_printing
    while not stop_printing:
        print(".", end="", flush=True)
        time.sleep(0.5)


def get_multiline_input(prompt=""):
    """
    Get multi-line input with proper backspace and editing support.
    Press Enter twice to finish input, or Ctrl+D to finish.
    """
    print(prompt)
    lines = []
    
    try:
        while True:
            try:
                # Use readline for better input handling
                line = input()
                
                # If empty line, check if we have content to finish
                if line.strip() == "":
                    if lines:  # If we have content, finish input
                        break
                    else:  # If no content yet, continue waiting
                        continue
                
                lines.append(line)
                
            except KeyboardInterrupt:
                # Handle Ctrl+C - clear current input and start over
                print("\n[Input cleared - press Ctrl+C again to quit, or start typing your message]")
                lines = []
                continue
                
    except EOFError:
        # Handle Ctrl+D - finish input
        if not lines:
            return None
    
    return "\n".join(lines)


def chat():
    global stop_printing
    conversation_history_openai = []
    conversation_history_anthropic = []
    conversation_history_gemini = []

    options = {"1": "ChatGPT", "2": "Claude", "3": "Gemini", "4": "All"}
    while True:
        print("Please choose an option:")
        for key, value in options.items():
            print(f"{key}: {value}")

        try:
            user_input = input("Enter the number of your choice: ")
        except KeyboardInterrupt:
            print("\nExiting chat. Goodbye!")
            sys.exit(0)
        except EOFError:
            print("\nExiting chat. Goodbye!")
            sys.exit(0)

        if user_input in options:
            number_selected = user_input
            while True:
                # Get user input with improved handling
                user_input = get_multiline_input("========================\nYou (press Enter twice to send, Ctrl+C to clear, Ctrl+D to finish):")
                
                # Handle case where user pressed Ctrl+D with no input
                if user_input is None:
                    print("\nExiting chat. Goodbye!")
                    break

                # Check if the user wants to quit
                if user_input.lower() == "quit":
                    print("Exiting chat. Goodbye!")
                    break

                # Add user input to conversation history
                initial_message = {"role": "user", "content": user_input}
                if number_selected == "1" or number_selected == "4":
                    conversation_history_openai.append(initial_message)

                if number_selected == "2" or number_selected == "4":
                    conversation_history_anthropic.append(initial_message)

                if number_selected == "3" or number_selected == "4":
                    conversation_history_gemini.append(initial_message)

                # Start printing dots in a separate thread
                stop_printing = False
                dot_thread = threading.Thread(target=print_dots)
                dot_thread.start()

                if number_selected == "1" or number_selected == "4":
                    # Send the conversation history to GPT
                    response_openai = openai_client.chat.completions.create(
                        model=os.environ["OPENAI_MODEL"],
                        messages=conversation_history_openai,
                    )

                if number_selected == "2" or number_selected == "4":
                    # Send the conversation history to Claude
                    response_claude = anthropic_client.messages.create(
                        model=os.environ["CLAUDE_MODEL"],
                        max_tokens=1024,
                        messages=conversation_history_anthropic,
                    )
                if number_selected == "3" or number_selected == "4":
                    # Send the conversation history to Gemini
                    prompt = "\n".join(
                        [msg["content"] for msg in conversation_history_gemini]
                    )
                    response_gemini = gemini_client.models.generate_content(
                        model=os.environ["GEMINI_MODEL"],
                        contents=prompt,
                    )

                # Stop printing dots
                stop_printing = True
                dot_thread.join()

                if number_selected == "1" or number_selected == "4":
                    gpt_response = response_openai.choices[0].message.content
                    # Print a newline to separate dots from the response
                    print(
                        "\n================================================\nGPT: "
                        + gpt_response
                    )
                    # Add GPT's response to conversation history
                    conversation_history_openai.append(
                        {"role": "assistant", "content": gpt_response}
                    )

                if number_selected == "2" or number_selected == "4":
                    # Get Claude's response
                    claude_response = response_claude.content[0].text
                    # Print Claude's response
                    print(
                        f"\n================================================\nClaude: {claude_response}"
                    )
                    # Add Claude's response to conversation history
                    conversation_history_anthropic.append(
                        {"role": "assistant", "content": claude_response}
                    )

                if number_selected == "3" or number_selected == "4":
                    # Get Gemini's response
                    gemini_response = response_gemini.text
                    # Print Gemini's response
                    print(
                        f"\n================================================\nGemini: {gemini_response}"
                    )
                    # Add Gemini's response to conversation history
                    conversation_history_gemini.append(
                        {"role": "assistant", "content": gemini_response}
                    )

            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    stop_printing = False
    chat()
