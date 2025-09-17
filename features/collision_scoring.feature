Feature: Collision and scoring
  Scenario: Bullet hits enemy
    Given an enemy at position x=0,y=0,z=-10 with radius 0.85
    And a bullet in front of the enemy traveling forward
    When the bullet intersects the enemy
    Then the enemy is removed and score increases by 100
