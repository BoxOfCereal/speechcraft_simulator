# AI Debate Game

A text-based debating game powered by LlamaIndex and GROQ API. In this game, you can engage in debates with an AI opponent on various topics.

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the root directory and add your GROQ API key:
```
GROQ_API_KEY=your_api_key_here
```

3. Run the game:
```bash
python debate_game.py
```

## How to Play

1. Choose a debate topic when prompted
2. Take turns making arguments with the AI
3. The game will evaluate arguments and provide responses
4. Continue the debate until a conclusion is reached

## How the DebateGame Class Works

The `DebateGame` class is the core of this application. Here's how it works:

### Key Components

1. **Initialization (`__init__`)**
   - Sets up the game with an optional AI personality
   - Default personality is an unhinged debater who gets very emotional
   - Initializes debate history and logging

2. **Topic Generation**
   - Uses `generate_topic()` to create unusual and provocative debate topics
   - Topics are designed to be weird but not inappropriate

3. **AI Responses**
   - `get_ai_response(player_argument)` generates the AI's counter-arguments
   - Takes into account:
     - Current topic
     - Debate history
     - Your last argument
     - AI's personality

4. **Argument Evaluation**
   - `evaluate_argument()` rates arguments on a scale of 1-10
   - Provides feedback on argument strength

5. **Logging**
   - Automatically saves all debate interactions to a log file
   - Logs are stored in the `logs` directory with timestamps

### Game Flow

1. Start the game by creating a `DebateGame` instance
2. Game generates a random debate topic
3. Take turns making arguments:
   - You type your argument
   - AI generates a response
   - Each argument is evaluated
4. Debate continues until you choose to end it

### Example Usage

```python
# Create a game with default unhinged personality
game = DebateGame()

# Or specify a custom personality
game = DebateGame(ai_personality="Your custom personality here")

# Start the game
game.play()
```

## Features

- Dynamic topic selection
- AI-powered argument generation and evaluation
- Turn-based debate structure
- Argument quality assessment
