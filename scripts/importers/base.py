from abc import ABC, abstractmethod


class BaseImporter(ABC):
    """Base class for all importers."""

    @abstractmethod
    def add_arguments(self, parser):
        """Add importer-specific arguments to the parser."""
        pass

    @abstractmethod
    def run(self, args):
        """Execute the importer with the given arguments."""
        pass
