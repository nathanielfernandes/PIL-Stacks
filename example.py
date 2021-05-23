from src import *
import os

a = Editor(
    name="example",
    Background="src/pil_stacks/Assets/example_background.png",
    Background_as_constant=False,
)
a.show_fps = True
a.__debug_info__ = True

stack = a.Launch()
# stack.export_template() #uncomment to test exporting


# meme = Stack(name="test123", base="src/pil_stacks/Assets/example_background.png")
# meme.import_template("example_TEMPLATE.zip")

# img = meme.generate()

# img.show()
