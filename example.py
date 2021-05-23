from src import *
import os

a = Editor(name="example", Background="src/pil_stacks/Assets/example_background.png", Background_as_constant=True)
# a.show_fps = True
# a.__debug_info__ = True

stack = a.Launch()
# stack.export_template() #uncomment to test exporting
