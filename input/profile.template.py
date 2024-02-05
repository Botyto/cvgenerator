from model import *

PROFILE = Profile(
    name="John Doe",
    title="Professional Title",
    accent_color = "rgb(30, 144, 255)",
    phone="+123 456 7890",
    email="me@johndoe.com",
    location="City, Country",
    link=Link.linkedin("https://www.linkedin.com/in/john-doe"),
    photo_file="photo.png",
    sections=[
        TextSection("Summary",
            column=0,
            entries=[
                TextEntry("A summary of me"),
            ],
        ),
        JobSection("Experience",
            column=0,
            entries=[
                JobEntry(
                    start_date=Date(2010, 5),
                    end_date=Date(2020, 8),
                    title="Professional Title",
                    company="Company Name",
                    location="City, Country",
                    link=Link.homepage("https://www.company.site/"),
                    description="Your job description",
                    bullets=[
                        "What you did",
                        "What you achieved",
                    ],
                ),
            ],
        ),
        SkillsSection("Expertise",
            column=1,
            groups=[
                SkillsGroup(entries=[
                    SkillEntry(name="Math"),
                    SkillEntry(name="Mentorship"),
                    SkillEntry(name="Microsoft Office"),
                ]),
            ],
        ),
        EducationSection("Education",
            column=1,
            entries=[
                EducationEntry(
                    start_date=Date(2013),
                    end_date=Date(2017),
                    field="Bachelor of Science in Computer Science",
                    school="University of Example",
                    bullets=[
                        "What you learned",
                        "What you achieved",
                    ],
                ),
            ],
        ),
    ],
)
