# --------------------------------------------
# Main part of the plugin
#
# JL Diaz (c) 2019
# MIT License
# --------------------------------------------
from collections  import defaultdict
from pathlib import Path
import logging
import jinja2
from mkdocs.plugins import BasePlugin
from mkdocs.config.config_options import Type
from mkdocs.utils import string_types
from mkdocs.structure.files import File
from mkdocs.commands.build import build

hash_previous = None

class TagsPlugin(BasePlugin):
    """
    Creates "tags.md" file containing a list of the pages grouped by tags

    It uses the info in the YAML metadata of each page, for the pages which
    provide a "tags" keyword (whose value is a list of strings)
    """

    config_scheme = (
        ('tags_filename', Type(string_types, default='tags.md')),
        ('tags_folder', Type(string_types, default='aux')),
        ('tags_template', Type(string_types)),
    )

    def __init__(self):
        self.metadata = []
        self.tags_filename = "tags.md"
        self.tags_folder = "aux"
        self.tags_template = None

    def on_config(self, config):
        # Re assign the options from configuration
        self.tags_filename = Path(self.config.get("tags_filename") or self.tags_filename)
        self.tags_folder = Path(self.config.get("tags_folder") or self.tags_folder)
        # Make sure that the tags folder is absolute, and exists
        if not self.tags_folder.is_absolute():
            self.tags_folder = Path(config["docs_dir"]) / ".." / self.tags_folder
        if not self.tags_folder.exists():
            self.tags_folder.mkdir(parents=True)
        if self.config.get("tags_template"):
            self.tags_template = Path(self.config.get("tags_template"))

    def on_files(self, files, config):
        # Add tags.md to the list of files, if tag.md exists
        # Also update hash_previous with the hash of the contents of tags.md
        global hash_previous
        self.metadata = []
        tagsfile = self.tags_folder / self.tags_filename
        if tagsfile.exists():
            newfile = File(
                path=str(self.tags_filename),
                src_dir=str(self.tags_folder),
                dest_dir=config["site_dir"],
                use_directory_urls=False
            )
            files.append(newfile)
            # Also compute and store its hash
            with tagsfile.open() as f:
                hash_previous = hash(f.read())

    def on_page_markdown(self, markdown, page, config, files):
        # Collect page metadata
        if page.meta:
            meta = page.meta.copy()
            meta.update(filename=page.url)
            if "title" not in meta:
                meta.update(title=page.title)
            self.metadata.append(meta)

    def on_post_build(self, config):
        # Create tags.md file and trigger a new build if required
        global hash_previous
        content = self.generate_tags_file()
        if hash(content) != hash_previous:
            hash_previous = hash(content)
            build(config)
        else:
            # print("INFO: Rebuild is not neccessary")
            pass

    # Helper functions
    def generate_tags_file(self):
        # Groups pages by tags, creates tags.md file
        tag_dict = defaultdict(list)
        for e in self.metadata:
            if not e:
                continue
            if "title" not in e:
                e["title"] = "Untitled"
            for tag in e.get("tags", []):
                tag_dict[tag].append(e)

        t = self.generate_tags_page_contents(tag_dict)

        with open(str(self.tags_folder / self.tags_filename), "w") as f:
            f.write(t)
        return t

    def generate_tags_page_contents(self, data):
        # Returns the markddown to write into tags.md
        if self.tags_template is None:
            templ_path = Path(__file__).parent  / Path("templates")
            environment = jinja2.Environment(
                loader=jinja2.FileSystemLoader(str(templ_path))
                )
            templ = environment.get_template("tags.md.template")
        else:
            environment = jinja2.Environment(
                loader=jinja2.FileSystemLoader(searchpath=str(self.tags_template.parent))
            )
            templ = environment.get_template(str(self.tags_template.name))
        output_text = templ.render(
                tags=sorted(data.items(), key=lambda t: t[0].lower()),
        )
        return output_text
