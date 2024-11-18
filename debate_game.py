import os
from dotenv import load_dotenv
from llama_index.llms.groq import Groq
from llama_index.core import Prompt
from datetime import datetime
from game_settings import GameSettings
from dataclasses import dataclass, field
from typing import Dict, List

def load_personalities():
    """Load personalities from the markdown file."""
    personalities = {}
    current_personality = None
    
    with open("personalities.md", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("## "):
                current_personality = line[3:].strip()
                personalities[current_personality] = ""
            elif current_personality and line and not line.startswith("#"):
                personalities[current_personality] += line + "\n"
    
    return {name: desc.strip() for name, desc in personalities.items()}

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variables
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("Please set GROQ_API_KEY in your .env file")

# Initialize Groq models
llm = Groq(model="llama3-8b-8192", api_key=groq_api_key)

@dataclass
class PlayerScore:
    strategy: int = 0
    sophistry: int = 0
    morality: int = 0
    experience: int = 0
    
    def update(self, round_scores: Dict[str, int]):
        self.strategy += round_scores.get('strategy', 0)
        self.sophistry += round_scores.get('sophistry', 0)
        self.morality += round_scores.get('morality', 0)
        self.experience += round_scores.get('experience', 0)
    
    def to_dict(self) -> dict:
        return {
            'strategy': self.strategy,
            'sophistry': self.sophistry,
            'morality': self.morality,
            'experience': self.experience
        }

class DebateScores:
    def __init__(self):
        self.player = PlayerScore()
        self.ai = PlayerScore()
        self.player_history: List[Dict[str, int]] = []
        self.ai_history: List[Dict[str, int]] = []
    
    def update_scores(self, scores: Dict[str, int], is_player: bool):
        if is_player:
            self.player.update(scores)
            self.player_history.append(scores)
        else:
            self.ai.update(scores)
            self.ai_history.append(scores)
    
    def get_scores(self, is_player: bool) -> Dict[str, int]:
        return self.player.to_dict() if is_player else self.ai.to_dict()
    
    def get_history(self, is_player: bool) -> List[Dict[str, int]]:
        return self.player_history if is_player else self.ai_history

@dataclass
class AudienceReaction:
    support_shift: int = 0  # Range from -100 to 100
    reaction: str = ""
    current_support: Dict[str, int] = field(default_factory=lambda: {"player": 50, "ai": 50})
    
    def update_support(self, support_shift: int, for_player: bool):
        max_shift = min(abs(support_shift), 20)  # Limit maximum shift per turn
        actual_shift = max_shift if support_shift > 0 else -max_shift
        
        if for_player:
            self.current_support["player"] = min(100, max(0, self.current_support["player"] + actual_shift))
            self.current_support["ai"] = min(100, max(0, self.current_support["ai"] - actual_shift))
        else:
            self.current_support["ai"] = min(100, max(0, self.current_support["ai"] + actual_shift))
            self.current_support["player"] = min(100, max(0, self.current_support["player"] - actual_shift))

class DebateGame:
    def __init__(self, settings: GameSettings = None):
        self.debate_history = []
        self.current_topic = None
        self.settings = settings or GameSettings.default()
        self.personalities = load_personalities()
        self.scores = DebateScores()
        self.round_number = 0
        self.audience_reactions = []
        
        # Load personality based on settings
        self.ai_personality = self.personalities.get(
            self.settings.personality,
            self.personalities.get("Unhinged")
        )
        
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
            "Generate a counter-argument that addresses the points made while staying true to your personality. "
            "Keep the response concise and focused.")
        
        self.evaluation_prompt = (
            "You are judging a debate argument. Review the full context and score ONLY the {participant}'s most recent argument.\n\n"
            "Topic: {topic}\n"
            "Full Debate Context:\n{history}\n\n"
            "Score the {participant}'s argument on these criteria:\n"
            "1. Strategy (1-10): How well-structured and effective is the argumentation?\n"
            "2. Sophistry (1-10): How clever or persuasive are the rhetorical techniques used?\n"
            "3. Morality (1-10): How ethically sound is the argument's reasoning?\n"
            "4. Experience Points (0-100): Overall performance considering creativity, engagement, and impact\n\n"
            "Format scores exactly as:\n"
            "Strategy: [score] - [one-line explanation]\n"
            "Sophistry: [score] - [one-line explanation]\n"
            "Morality: [score] - [one-line explanation]\n"
            "Experience: [score] - [one-line explanation]\n"
            "Overall: [brief summary of strongest and weakest points]"
        )
        
        self.audience_prompt = (
            "You are the audience of this debate. You represent a diverse crowd with various viewpoints.\n\n"
            "Topic: {topic}\n"
            "Current Debate Context:\n{history}\n\n"
            "Latest {participant} Argument: {argument}\n\n"
            "Current Audience Support:\n"
            "Player Support: {player_support}%\n"
            "AI Support: {ai_support}%\n\n"
            "Evaluate how this argument affected the audience's support:\n"
            "1. Rate the support shift (-100 to +100, where positive means gaining support)\n"
            "2. Describe the audience's reaction and mood\n\n"
            "Format your response exactly as:\n"
            "Support Shift: [number]\n"
            "Reaction: [one or two sentences describing the audience reaction and current mood]"
        )

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

    def evaluate_argument(self, argument, is_player=True):
        """Evaluate the strength of an argument with detailed scoring."""
        # Format the debate history to show the flow of conversation
        history = ""
        for i, arg in enumerate(self.debate_history, 1):
            history += f"Turn {i}: {arg}\n"
        if is_player:
            history += f"Turn {len(self.debate_history) + 1}: Player: {argument}"
        
        prompt = self.evaluation_prompt.format(
            participant="Player" if is_player else "AI",
            topic=self.current_topic,
            history=history
        )
        
        response = llm.complete(prompt)
        evaluation = response.text.strip()
        
        # Parse scores from evaluation
        scores = self._parse_scores(evaluation)
        self.scores.update_scores(scores, is_player)
        
        # Log the evaluation
        participant = "Player" if is_player else "AI"
        self.log_message(f"{participant} Evaluation: {evaluation}")
        self.log_message(f"Round {self.round_number} {participant} Scores: {scores}")
        self.log_message(f"Total {participant} Scores: {self.scores.get_scores(is_player)}")
        
        return evaluation

    def _parse_scores(self, evaluation: str) -> Dict[str, int]:
        """Parse scores from evaluation text."""
        scores = {
            'strategy': 0,
            'sophistry': 0,
            'morality': 0,
            'experience': 0
        }
        
        for line in evaluation.split('\n'):
            line = line.lower()
            if 'strategy:' in line:
                scores['strategy'] = self._extract_score(line)
            elif 'sophistry:' in line:
                scores['sophistry'] = self._extract_score(line)
            elif 'morality:' in line:
                scores['morality'] = self._extract_score(line)
            elif 'experience:' in line:
                scores['experience'] = self._extract_score(line)
        
        return scores
    
    def _extract_score(self, line: str) -> int:
        """Extract numerical score from evaluation line."""
        try:
            # Find the first number in the line
            import re
            numbers = re.findall(r'\d+', line)
            if numbers:
                return int(numbers[0])
        except ValueError:
            pass
        return 0

    def get_audience_reaction(self, argument: str, is_player: bool) -> AudienceReaction:
        """Get the audience's reaction to an argument."""
        current_support = self.audience_reactions[-1].current_support if self.audience_reactions else {"player": 50, "ai": 50}
        
        prompt = self.audience_prompt.format(
            topic=self.current_topic,
            history="\n".join(f"Turn {i+1}: {arg}" for i, arg in enumerate(self.debate_history)),
            participant="Player" if is_player else "AI",
            argument=argument,
            player_support=current_support["player"],
            ai_support=current_support["ai"]
        )
        
        response = llm.complete(prompt)
        reaction_text = response.text.strip()
        
        # Parse the reaction
        support_shift = 0
        reaction = ""
        for line in reaction_text.split('\n'):
            if line.startswith('Support Shift:'):
                try:
                    support_shift = int(line.split(':')[1].strip())
                except ValueError:
                    support_shift = 0
            elif line.startswith('Reaction:'):
                reaction = line.split(':')[1].strip()
        
        audience_reaction = AudienceReaction(support_shift=support_shift, reaction=reaction)
        audience_reaction.current_support = current_support.copy()
        audience_reaction.update_support(support_shift, is_player)
        
        self.audience_reactions.append(audience_reaction)
        return audience_reaction

    def determine_winner(self) -> str:
        """Determine the winner based on final audience support."""
        if not self.audience_reactions:
            return "No winner determined - no audience reactions recorded"
        
        final_support = self.audience_reactions[-1].current_support
        player_support = final_support["player"]
        ai_support = final_support["ai"]
        
        if player_support > ai_support:
            margin = player_support - ai_support
            return f"Player wins with {player_support}% support! ({margin}% margin of victory)"
        elif ai_support > player_support:
            margin = ai_support - player_support
            return f"AI wins with {ai_support}% support! ({margin}% margin of victory)"
        else:
            return "It's a tie! Both debaters have equal audience support."

    def play(self):
        """Main game loop."""
        self.start_logging()
        self.log_message("=== Debate Started ===")
        self.log_message(f"Game Settings: {self.settings.to_dict()}")
        
        print("Welcome to the AI Debate Game!")
        print(f"\nPersonality: {self.settings.personality}")
        print("\nGenerating a topic for debate...")
        topic = self.generate_topic()
        print(f"\nToday's debate topic: {topic}")
        print("\nAudience starts with neutral (50/50) support.")
        
        max_turns = self.settings.max_turns
        while self.round_number < max_turns:
            self.round_number += 1
            print(f"\nRound {self.round_number} of {max_turns}")
            
            # Player's turn
            print("\nYour turn! Make your argument:")
            try:
                player_argument = input("> ")
                if not player_argument:
                    break
            except (EOFError, KeyboardInterrupt):
                break
                
            self.log_message(f"Player: {player_argument}")
            self.debate_history.append(f"Player: {player_argument}")
            
            # Get audience reaction to player's argument
            print("\nGauging audience reaction...")
            audience_reaction = self.get_audience_reaction(player_argument, is_player=True)
            print(f"\nAudience Reaction: {audience_reaction.reaction}")
            print(f"Support Shift: {audience_reaction.support_shift:+d}")
            print(f"Current Support - Player: {audience_reaction.current_support['player']}% | AI: {audience_reaction.current_support['ai']}%")
            
            # Evaluate player's argument
            print("\nEvaluating your argument...")
            evaluation = self.evaluate_argument(player_argument, is_player=True)
            print(f"Feedback: {evaluation}")
            print(f"\nPlayer Scores:")
            for category, score in self.scores.get_scores(True).items():
                print(f"{category.title()}: {score}")
            
            # AI's turn
            print("\nAI is thinking of a response...")
            ai_response = self.get_ai_response(player_argument)
            print(f"\nAI: {ai_response}")
            self.debate_history.append(f"AI: {ai_response}")
            
            # Get audience reaction to AI's argument
            print("\nGauging audience reaction...")
            audience_reaction = self.get_audience_reaction(ai_response, is_player=False)
            print(f"\nAudience Reaction: {audience_reaction.reaction}")
            print(f"Support Shift: {audience_reaction.support_shift:+d}")
            print(f"Current Support - Player: {audience_reaction.current_support['player']}% | AI: {audience_reaction.current_support['ai']}%")
            
            # Evaluate AI's response if enabled
            if self.settings.custom_settings.get('evaluate_ai', False):
                print("\nEvaluating AI's argument...")
                ai_evaluation = self.evaluate_argument(ai_response, is_player=False)
                print(f"AI Feedback: {ai_evaluation}")
                print(f"\nAI Scores:")
                for category, score in self.scores.get_scores(False).items():
                    print(f"{category.title()}: {score}")
        
        # Display final results
        print("\n=== Final Results ===")
        print("\nDebate Winner:")
        print(self.determine_winner())
        
        print("\nFinal Scores:")
        print("\nPlayer Scores:")
        for category, score in self.scores.get_scores(True).items():
            print(f"{category.title()}: {score}")
        
        if self.settings.custom_settings.get('evaluate_ai', False):
            print("\nAI Scores:")
            for category, score in self.scores.get_scores(False).items():
                print(f"{category.title()}: {score}")
        
        self.log_message("=== Debate Ended ===")
        if self.log_file:
            self.log_file.close()
            self.log_file = None

if __name__ == "__main__":
    # Example of creating a game with custom settings
    settings = GameSettings(
        personality="Lucien Lachance",
        max_turns=3,  # Set number of debate rounds
        custom_settings={"debate_style": "formal", "evaluate_ai": True}
    )
    
    game = DebateGame(settings)
    game.play()
