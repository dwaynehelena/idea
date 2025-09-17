Feature: Shooting
  Scenario: Player shoots and bullet is created
    Given the player is at position x=0,y=0
    When the player presses Space
    Then a bullet is spawned in front of the player
    And the bullet travels forward and is removed when z < -200
