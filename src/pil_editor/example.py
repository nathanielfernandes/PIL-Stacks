from Editor import Editor
import os
a = Editor(name="example",Background=os.path.join("Assets","example_background.png"))
a.show_fps = True
a.__debug_info__ = True

stack = a.Launch()
#stack.export_template() uncomment to test exporting