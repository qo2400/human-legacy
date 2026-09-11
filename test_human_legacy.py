"""
Test suite for Human Legacy civilization simulation.
Tests core game mechanics and engine functionality.
"""

import json
import tempfile
from pathlib import Path

from human_legacy import Civilization, get_save_path


class TestCivilization:
    """Tests for the Civilization class."""

    def test_initialization(self):
        """Test that a civilization initializes with correct defaults."""
        civ = Civilization()
        
        assert civ.year == -10000
        assert civ.population == 120.0
        assert civ.knowledge == 5.0
        assert civ.government == "Tribal Council"
        assert len(civ.history) == 1

    def test_population_growth(self):
        """Test that population grows when advancing."""
        civ = Civilization()
        initial_pop = civ.population
        
        civ.advance()
        
        assert civ.population > initial_pop

    def test_science_generation(self):
        """Test that science points are generated each turn."""
        civ = Civilization()
        initial_knowledge = civ.knowledge
        
        civ.advance()
        
        assert civ.knowledge > initial_knowledge

    def test_research_agriculture(self):
        """Test researching Agriculture technology."""
        civ = Civilization()
        civ.knowledge = 100  # Ensure enough knowledge
        
        success, message = civ.research("Agriculture", 8)
        
        assert success is True
        assert civ.techs["Agriculture"] is True
        assert "Agriculture" in message

    def test_research_insufficient_knowledge(self):
        """Test that research fails with insufficient knowledge."""
        civ = Civilization()
        civ.knowledge = 1  # Not enough
        
        success, message = civ.research("Agriculture", 8)
        
        assert success is False
        assert "Not enough knowledge" in message

    def test_research_already_discovered(self):
        """Test that researching twice fails."""
        civ = Civilization()
        civ.knowledge = 100
        
        civ.research("Agriculture", 8)
        success, message = civ.research("Agriculture", 8)
        
        assert success is False
        assert "Already discovered" in message

    def test_government_evolution(self):
        """Test that government changes based on values."""
        civ = Civilization()
        civ.values["Authority"] = 80
        civ.values["Militarism"] = 70
        
        gov = civ.government_for_values()
        
        assert gov == "Military Empire"

    def test_republic_government(self):
        """Test Republic government formation."""
        civ = Civilization()
        civ.values["Freedom"] = 75
        civ.values["Equality"] = 70
        
        gov = civ.government_for_values()
        
        assert gov == "Republic"

    def test_clamp_values(self):
        """Test that clamp() keeps values in valid range."""
        civ = Civilization()
        civ.stability = 150
        civ.happiness = -50
        civ.values["Science"] = 120
        
        civ.clamp()
        
        assert civ.stability == 100.0
        assert civ.happiness == 0.0
        assert civ.values["Science"] == 100.0

    def test_policy_changes_values(self):
        """Test that promoting a policy increases its value."""
        civ = Civilization()
        initial_science = civ.values["Science"]
        
        civ.policy("Science")
        
        assert civ.values["Science"] > initial_science

    def test_history_logging(self):
        """Test that events are logged to history."""
        civ = Civilization()
        initial_history_len = len(civ.history)
        
        civ._log("Test event")
        
        assert len(civ.history) == initial_history_len + 1
        assert "Test event" in civ.history

    def test_history_capped(self):
        """Test that history is capped at MAX_HISTORY."""
        civ = Civilization()
        
        # Add events beyond the cap
        for i in range(Civilization.MAX_HISTORY + 100):
            civ._log(f"Event {i}")
        
        assert len(civ.history) <= Civilization.MAX_HISTORY

    def test_available_research(self):
        """Test that available research is empty at start."""
        civ = Civilization()
        
        research_options = civ.available_research()
        
        # Should have Agriculture available at start
        tech_names = [option[0] for option in research_options]
        assert "Agriculture" in tech_names

    def test_agriculture_unlocks_writing(self):
        """Test that Agriculture allows researching Writing."""
        civ = Civilization()
        civ.knowledge = 100
        civ.techs["Agriculture"] = True
        
        research_options = civ.available_research()
        tech_names = [option[0] for option in research_options]
        
        assert "Writing" in tech_names

    def test_random_event(self):
        """Test that random events generate valid text."""
        civ = Civilization()
        
        event = civ.random_event()
        
        assert isinstance(event, str)
        assert len(event) > 0
        assert event in civ.history[-1]

    def test_year_advances(self):
        """Test that time advances by 25 years per turn."""
        civ = Civilization()
        start_year = civ.year
        
        civ.advance()
        
        assert civ.year == start_year + 25

    def test_save_and_load(self):
        """Test saving and loading game state."""
        civ1 = Civilization()
        civ1.year = 5000
        civ1.population = 1000
        civ1.knowledge = 50
        civ1.techs["Agriculture"] = True
        
        # Save
        success = civ1.save()
        assert success is True
        
        # Load into new civilization
        civ2 = Civilization()
        success = civ2.load()
        
        assert success is True
        assert civ2.year == 5000
        assert civ2.population == 1000
        assert civ2.knowledge == 50
        assert civ2.techs["Agriculture"] is True

    def test_environment_degrades_with_population(self):
        """Test that large population degrades environment."""
        civ = Civilization()
        civ.population = 25000
        initial_env = civ.environment
        
        civ.advance()
        
        assert civ.environment < initial_env
