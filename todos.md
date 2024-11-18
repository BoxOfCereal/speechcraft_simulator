# To-Do List for Debate Game

## Scoring System
- [ ] Update the audience scoring system
  - Current: Scores are awarded independently
  - Desired: Make it a zero-sum game where Audience points are awarded to either player or AI
  - Example format:
    ```
    Player: 85% (+5%) points
    AI: 15 (-5%) points
    ```
  - This will make the scoring more competitive and dynamic
  - Need to update score parsing logic to handle the new format

## Future Ideas
- [ ] Add support for different Conversational objectives
- [ ] Implement a tournament mode where player faces multiple AI personalities
- [ ] Add debate topics categories (e.g., philosophy, technology, society)
