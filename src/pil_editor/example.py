from Editor import Editor
import os
a = Editor(Background=os.path.join("Assets","example_background.png"))
a.show_fps = True
a.__debug_info__ = True
a.Launch()