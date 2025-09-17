Feature: Player movement
  As a player
  I want to move the ship using arrow keys
  So that I can dodge enemy fire and position for shots

  Scenario: Move left and right within bounds
    Given the player starts at position x=0, y=0
    When the player presses ArrowRight for 1 second
    Then the player's x position increases but remains <= 8
    When the player presses ArrowLeft for 2 seconds
    Then the player's x position is >= -8

  Scenario: Move up and down within bounds
    Given the player starts at position x=0, y=0
    When the player presses ArrowUp
    Then the player's y position is <= 8
    When the player presses ArrowDown
    Then the player's y position is >= -3
