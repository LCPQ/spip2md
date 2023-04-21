import yaml
from slugify import slugify


class metadata:
    def __init__(self, article):
        self.id = article.id_article
        self.title = article.titre
        self.date = article.date

    def get_title(self):
        return "# {}\n".format(self.title)

    def get_slug(self):
        return slugify("{}-{}".format(self.id, self.title))

    def get_frontmatter(self):
        return "---\n{}---".format(yaml.dump({"title": self.title, "date": self.date}))
