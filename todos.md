# To-Do List for Debate Game

## Scoring System
- [ ] Update evaluation prompt to explicitly award points between player and AI
  - Current: Scores are awarded independently
  - Desired: Make it a zero-sum game where points are awarded to either player or AI
  - Example format:
    ```
    Strategy: Player +7, AI -7 - Player's argument was more structured
    Sophistry: Player -3, AI +3 - AI's rhetorical techniques were more effective
    ```
  - This will make the scoring more competitive and dynamic
  - Need to update score parsing logic to handle the new format

## Future Ideas
- [ ] Add support for different debate formats (e.g., Oxford style, Lincoln-Douglas)
- [ ] Implement a tournament mode where player faces multiple AI personalities
- [ ] Add debate topics categories (e.g., philosophy, technology, society)
