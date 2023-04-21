import yaml
from slugify import slugify

class metadata:
    # row is an array containing at positions :
    # 0: id
    # 2: title (titre)
    # 7: body (texte)
    # 9: date
    def __init__(self, row):
        self.id = row[0]
        self.title = row[2]
        self.date = row[9]
    def get_title(self):
        return "# {}\n".format(self.title)
    def get_slug(self):
        return slugify("{}-{}".format(self.id, self.title))
    def get_frontmatter(self):
        return "---\n{}---".format(yaml.dump({"title": self.title, "date": self.date}))
