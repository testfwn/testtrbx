import re

# Input text
text = """
# """

# Regular expression to extract all links
links = re.findall(r"https?://\S+", text)

# Print the list of links
print(links)
