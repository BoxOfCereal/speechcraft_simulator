import os
from dotenv import load_dotenv
from llama_index.llms.groq import Groq
from llama_index.core import Prompt
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variables
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("Please set GROQ_API_KEY in your .env file")

# Initialize Groq models
llm = Groq(model="llama3-8b-8192", api_key=groq_api_key)

class DebateGame:
    def __init__(self, ai_personality=None):
        self.debate_history = []
        self.current_topic = None
        self.ai_personality = ai_personality or "You are an extremely passionate and unhinged debater who gets overly emotional and dramatic about your arguments. You make wild connections between topics, use excessive punctuation, and occasionally go off on tangents while still trying to make somewhat logical points. You LOVE using CAPS for emphasis and dramatic effect."
        self.log_file = None
        
        # Define prompt templates
        self.topic_prompt = ("Generate an unusual and provocative topic that would make for a heated discussion. "
            "The topic should be absurd or unconventional, possibly combining unrelated concepts in unexpected ways. "
            "Make it weird but not inappropriate or offensive. "
            "Format: Just return the topic as a single sentence.")
        
        self.response_prompt = ("Personality: {personality}\n\n"
            "You are participating in a debate on the topic: {topic}\n"
            "Previous arguments:\n{history}\n"
            "Latest argument from opponent: {last_argument}\n"
            "Generate a well-reasoned counter-argument that addresses the points made while staying true to your personality. "
            "Keep the response concise and focused.")
        
        self.evaluation_prompt = ("Evaluate the following argument in the context of the debate:\n"
            "Topic: {topic}\n"
            "Argument: {argument}\n"
            "Rate the argument's strength on a scale of 1-10 and provide brief feedback.")

    def start_logging(self):
        """Start logging the debate conversation."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_dir = os.path.join(os.path.dirname(__file__), "logs")
        os.makedirs(log_dir, exist_ok=True)
        self.log_file = open(os.path.join(log_dir, f"debate_{timestamp}.txt"), "w", encoding="utf-8")
        
    def log_message(self, message):
        """Log a message to the debate log file."""
        if self.log_file:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.log_file.write(f"[{timestamp}] {message}\n")
            self.log_file.flush()

    def generate_topic(self):
        """Generate a debate topic using the LLM."""
        response = llm.complete(self.topic_prompt)
        self.current_topic = response.text.strip()
        self.log_message(f"Topic: {self.current_topic}")
        return self.current_topic

    def get_ai_response(self, player_argument):
        """Generate AI's response to the player's argument."""
        history = "\n".join([f"- {arg}" for arg in self.debate_history])
        prompt = self.response_prompt.format(
            personality=self.ai_personality,
            topic=self.current_topic,
            history=history,
            last_argument=player_argument
        )
        response = llm.complete(prompt)
        ai_response = response.text.strip()
        self.log_message(f"AI: {ai_response}")
        return ai_response

    def evaluate_argument(self, argument):
        """Evaluate the strength of an argument."""
        prompt = self.evaluation_prompt.format(
            topic=self.current_topic,
            argument=argument
        )
        response = llm.complete(prompt)
        evaluation = response.text.strip()
        self.log_message(f"Evaluation: {evaluation}")
        return evaluation

    def play(self):
        """Main game loop."""
        self.start_logging()
        self.log_message("=== Debate Started ===")
        
        print("Welcome to the AI Debate Game!")
        print("\nGenerating a topic for debate...")
        topic = self.generate_topic()
        print(f"\nToday's debate topic: {topic}")
        
        while True:
            # Player's turn
            print("\nYour turn! Make your argument:")
            try:
                player_argument = input("> ")
                if not player_argument:
                    print("Thanks for playing!")
                    break
            except (EOFError, KeyboardInterrupt):
                print("\nThanks for playing!")
                break
                
            self.log_message(f"Player: {player_argument}")
            self.debate_history.append(f"Player: {player_argument}")
            
            # Evaluate player's argument
            print("\nEvaluating your argument...")
            evaluation = self.evaluate_argument(player_argument)
            print(f"Feedback: {evaluation}")
            
            # AI's turn
            print("\nAI is thinking of a response...")
            ai_response = self.get_ai_response(player_argument)
            print(f"\nAI: {ai_response}")
            self.debate_history.append(f"AI: {ai_response}")
            
            # Evaluate AI's argument
            print("\nEvaluating AI's argument...")
            evaluation = self.evaluate_argument(ai_response)
            print(f"Feedback: {evaluation}")
        
        self.log_message("=== Debate Ended ===")
        if self.log_file:
            self.log_file.close()
            self.log_file = None

if __name__ == "__main__":
    game = DebateGame()
    game.play()
