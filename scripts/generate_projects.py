import json
import random
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional, Union
import os

from faker import Faker

__file__ = Path(__file__).resolve()
BASE_DIR = __file__.parent.parent
SCRIPTS_DIR = __file__.parent
TEST_DIR = BASE_DIR / "tests"


def jsonify(cls):
    def to_json(self) -> str:
        # Convert dataclass object to dictionary recursively
        def to_dict(obj):
            if isinstance(obj, (str, int, float, bool, type(None))):
                return obj
            elif isinstance(obj, Enum):
                return obj.value
            elif isinstance(obj, list):
                return [to_dict(item) for item in obj]
            elif hasattr(obj, "__dict__"):
                return {key: to_dict(value) for key, value in obj.__dict__.items()}
            else:
                return str(obj)

        serialized_data = json.dumps(to_dict(self), indent=4)
        # Remove lines with "null" values
        # This is useful for optional fields with None values
        serialized_data = "\n".join(
            [line for line in serialized_data.splitlines() if "null" not in line]
        )
        return serialized_data

    cls.to_json = to_json
    return cls


class MediaType(Enum):
    IMAGE = "image"
    VIDEO = "video"


@jsonify
@dataclass
class MediaContent:
    type: MediaType
    url: str
    caption: Optional[str] = None


class ContentType(Enum):
    TEXT = "text"
    TITLE = "title"
    MEDIA = "media"


@jsonify
@dataclass
class Content:
    type: ContentType
    value: Union[str, MediaContent]


@jsonify
@dataclass
class Person:
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone_number: Optional[str] = None


@jsonify
@dataclass
class Section:
    title: str
    contents: List[Content]


@jsonify
@dataclass
class Project:
    id: str
    title: str
    description: str
    image_url: str
    sections: List[Section]
    start_date: str
    end_date: Optional[str] = None
    members: Optional[List[Person]] = None
    tags: Optional[List[str]] = None


class ProjectGenerator:
    """
    Generate random projects with fake data.

    Attributes:
        fake: Faker object for generating

    Methods:
        generate_project: Generate a random project
        generate_person: Generate a random person
        generate_section: Generate a random section
        generate_content: Generate a random content
        generate_media_content: Generate a random media content
    """

    def __init__(
        self,
        min_members: int = 1,
        max_members: int = 5,
        min_sections: int = 1,
        max_sections: int = 5,
        min_content: int = 1,
        max_content: int = 5,
        min_nb_chars_description: int = 10,
        max_nb_chars_description: int = 1000,
        min_nb_chars_section_title: int = 10,
        max_nb_chars_section_title: int = 100,
        min_nb_chars_content_text: int = 10,
        max_nb_chars_content_text: int = 1000,
        min_nb_chars_content_title: int = 10,
        max_nb_chars_content_title: int = 100,
    ):
        self.fake = Faker()
        self.min_members = min_members
        self.max_members = max_members
        self.min_sections = min_sections
        self.max_sections = max_sections
        self.min_content = min_content
        self.max_content = max_content
        self.min_nb_chars_description = min_nb_chars_description
        self.max_nb_chars_description = max_nb_chars_description
        self.min_nb_chars_section_title = min_nb_chars_section_title
        self.max_nb_chars_section_title = max_nb_chars_section_title
        self.min_nb_chars_content_text = min_nb_chars_content_text
        self.max_nb_chars_content_text = max_nb_chars_content_text
        self.min_nb_chars_content_title = min_nb_chars_content_title
        self.max_nb_chars_content_title = max_nb_chars_content_title

    def generate_project(self) -> Project:
        tags = (
            self.fake.words() if self.fake.boolean(chance_of_getting_true=50) else None
        )
        end_date = (
            self.fake.date() if self.fake.boolean(chance_of_getting_true=50) else None
        )
        members = (
            [
                self.generate_person()
                for _ in range(random.randint(self.min_members, self.max_members))
            ]
            if self.fake.boolean(chance_of_getting_true=50)
            else None
        )

        project = Project(
            id=str(self.fake.unique.random_int()),
            title=self.fake.sentence(),
            description=self.fake.text(
                max_nb_chars=random.randint(
                    self.min_nb_chars_description, self.max_nb_chars_description
                )
            ),
            image_url=self.fake.image_url(),
            tags=tags,
            start_date=self.fake.date(),
            end_date=end_date,
            members=members,
            sections=[
                self.generate_section()
                for _ in range(random.randint(self.min_sections, self.max_sections))
            ],
        )
        return project

    def generate_person(self) -> Person:
        email = (
            self.fake.email() if self.fake.boolean(chance_of_getting_true=50) else None
        )
        phone_number = (
            self.fake.phone_number()
            if self.fake.boolean(chance_of_getting_true=50)
            else None
        )

        person = Person(
            first_name=self.fake.first_name(),
            last_name=self.fake.last_name(),
            email=email,
            phone_number=phone_number,
        )
        return person

    def generate_section(self) -> Section:
        section = Section(
            title=self.fake.text(
                max_nb_chars=random.randint(
                    self.min_nb_chars_section_title, self.max_nb_chars_section_title
                )
            ),
            contents=[
                self.generate_content()
                for _ in range(random.randint(self.min_content, self.max_content))
            ],
        )
        return section

    def generate_content(self) -> Content:
        type = random.choice(list(ContentType))
        if type == ContentType.MEDIA:
            value = self.generate_media_content()
        elif type == ContentType.TITLE:
            value = self.fake.text(
                max_nb_chars=random.randint(
                    self.min_nb_chars_content_title, self.max_nb_chars_content_title
                )
            )
        else:
            value = self.fake.text(
                max_nb_chars=random.randint(
                    self.min_nb_chars_content_text, self.max_nb_chars_content_text
                )
            )
        content = Content(type=type, value=value)
        return content

    def generate_media_content(self) -> MediaContent:
        type = random.choice(list(MediaType))
        media_content = MediaContent(
            type=type,
            url=self.fake.image_url() if type == MediaType.IMAGE else self.fake.url(),
            caption=self.fake.sentence(),
        )
        return media_content

    def __next__(self) -> Project:
        return self.generate_project()

    def __iter__(self):
        return self


def main() -> None:
    num_projects = 10
    generator = ProjectGenerator(
        min_members=1,
        max_members=5,
        min_sections=1,
        max_sections=5,
        min_content=1,
        max_content=5,
        min_nb_chars_description=10,
        max_nb_chars_description=1000,
        min_nb_chars_section_title=10,
        max_nb_chars_section_title=100,
        min_nb_chars_content_text=10,
        max_nb_chars_content_text=1000,
        min_nb_chars_content_title=10,
        max_nb_chars_content_title=100,
    )

    # Check if directory is empty
    assert not os.listdir(TEST_DIR), "Directory is not empty"

    # Generate projects
    projects_file = TEST_DIR / "projects.json"
    with open(projects_file, "w") as fp_projects:
        fp_projects.write("[\n")
        for i, project in enumerate(generator):
            # Create a new file for each project
            project_dir = TEST_DIR / str(project.id)
            project_dir.mkdir(parents=True, exist_ok=True)
            project_file = project_dir / "project.json"
            with open(project_file, "w") as fp_project:
                fp_project.write(project.to_json())
                fp_project.write("\n")

            fp_projects.write(project.to_json())
            if i < num_projects - 1:
                fp_projects.write(",\n")
            else:
                fp_projects.write("\n")
            if i == num_projects - 1:
                break

        fp_projects.write("]\n")


if __name__ == "__main__":
    main()
