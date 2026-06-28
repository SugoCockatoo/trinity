# nodes.py

class ProgramNode:
    """The root container of your entire source file."""
    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return f"ProgramNode({self.statements})"


class BlockNode:
    """Represents configuration blocks like Train { epochs = 50 }"""
    def __init__(self, name, assignments):
        self.name = name
        self.assignments = assignments

    def __repr__(self):
        return f"BlockNode({self.name}, assignments={self.assignments})"


class AssignNode:
    """Represents a property definition like epochs = 50"""
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return f"AssignNode({self.name} = {self.value})"


class CallNode:
    """Represents a library execution line like trinity.train.start()"""
    def __init__(self, path):
        self.path = path  # This will be a string like 'trinity.train.start'

    def __repr__(self):
        return f"CallNode({self.path}())"