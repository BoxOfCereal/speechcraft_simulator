import os
from dotenv import load_dotenv
from groq import Groq
from llama_index.llms import Groq as LlamaGroq
from llama_index.prompts import PromptTemplate

# Load environment variables
load_dotenv()

# Initialize Groq client
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("Please set GROQ_API_KEY in your .env file")

llm = LlamaGroq(api_key=groq_api_key)

class DebateGame:
    def __init__(self, ai_personality=None):
        self.debate_history = []
        self.current_topic = None
        self.ai_personality = ai_personality or "You are a logical and balanced debater who carefully considers all angles of an argument."
        
        # Define prompt templates
        self.topic_prompt = PromptTemplate(
            "Generate an interesting and debatable topic that would make for a good discussion. "
            "The topic should be thought-provoking but not overly controversial. "
            "Format: Just return the topic as a single sentence."
        )
        
        self.response_prompt = PromptTemplate(
            "Personality: {personality}\n\n"
            "You are participating in a debate on the topic: {topic}\n"
            "Previous arguments:\n{history}\n"
            "Latest argument from opponent: {last_argument}\n"
            "Generate a well-reasoned counter-argument that addresses the points made while staying true to your personality. "
            "Keep the response concise and focused."
        )
        
        self.evaluation_prompt = PromptTemplate(
            "Evaluate the following argument in the context of the debate:\n"
            "Topic: {topic}\n"
            "Argument: {argument}\n"
            "Rate the argument's strength on a scale of 1-10 and provide brief feedback."
        )

    def generate_topic(self):
        """Generate a debate topic using the LLM."""
        response = llm.complete(str(self.topic_prompt))
        self.current_topic = response.text.strip()
        return self.current_topic

    def get_ai_response(self, player_argument):
        """Generate AI's response to the player's argument."""
        history = "\n".join([f"- {arg}" for arg in self.debate_history])
        prompt_args = {
            "personality": self.ai_personality,
            "topic": self.current_topic,
            "history": history,
            "last_argument": player_argument
        }
        response = llm.complete(str(self.response_prompt.format(**prompt_args)))
        return response.text.strip()

    def evaluate_argument(self, argument):
        """Evaluate the strength of an argument."""
        prompt_args = {
            "topic": self.current_topic,
            "argument": argument
        }
        response = llm.complete(str(self.evaluation_prompt.format(**prompt_args)))
        return response.text.strip()

    def play(self):
        """Main game loop."""
        print("Welcome to the AI Debate Game!")
        print("\nGenerating a topic for debate...")
        topic = self.generate_topic()
        print(f"\nToday's debate topic: {topic}")
        
        while True:
            # Player's turn
            print("\nYour turn! Make your argument:")
            player_argument = input("> ")
            self.debate_history.append(f"Player: {player_argument}")
            
            # Evaluate player's argument
            print("\nEvaluating your argument...")
            evaluation = self.evaluate_argument(player_argument)
            print(f"Feedback: {evaluation}")
            
            # AI's turn
            print("\nAI is thinking...")
            ai_response = self.get_ai_response(player_argument)
            print(f"\nAI's response: {ai_response}")
            self.debate_history.append(f"AI: {ai_response}")
            
            # Ask if player wants to continue
            if input("\nContinue debate? (y/n): ").lower() != 'y':
                break
        
        print("\nThank you for participating in the debate!")

if __name__ == "__main__":
    game = DebateGame()
    game.play()
