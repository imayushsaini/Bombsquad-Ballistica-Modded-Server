# Released under the MIT License. See LICENSE for details.
"""Command registry system for chat commands."""

from typing import Callable, List, Dict, Optional

class Command:
    """Represents a registered chat command."""
    def __init__(self, names: List[str], category: str, handler: Callable):
        self.names = [name.lower() for name in names]
        self.category = category
        self.handler = handler

class CommandRegistry:
    """Registry to manage and look up chat commands."""
    def __init__(self) -> None:
        self._commands: Dict[str, Command] = {}

    def register(self, names: List[str], category: str) -> Callable:
        """Decorator to register a list of command names/aliases under a category."""
        def decorator(func: Callable) -> Callable:
            cmd = Command(names, category, func)
            for name in cmd.names:
                self._commands[name] = cmd
            return func
        return decorator

    def get_command(self, name: str) -> Optional[Command]:
        """Look up a command by its name or alias."""
        return self._commands.get(name.lower())

    def get_all_commands(self) -> Dict[str, Command]:
        """Return all registered commands."""
        return self._commands

# Global registry instance
registry = CommandRegistry()
