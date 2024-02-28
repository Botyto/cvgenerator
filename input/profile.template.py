from model import *

PROFILE = Profile(
    name="John Doe",
    title="Professional Title",
    accent_color = "rgb(30, 144, 255)",
    phone="+123 456 7890",
    email="me@johndoe.com",
    location="City, Country",
    link="https://www.linkedin.com/in/john-doe",
    photo_file="photo.png",
    sections=[
        Section("Summary",
            column=0,
            entries=[
                TextEntry("A summary of me"),
            ],
        ),
        Section("Experience",
            column=0,
            entries=[
                ExperienceEntry(
                    start_date=Date(2010, 5),
                    end_date=Date(2020, 8),
                    title="Professional Title",
                    subtitle="Company Name",
                    location="City, Country",
                    link="https://www.company.site/",
                    description="Your job description",
                    bullets=[
                        "What you did",
                        "What you achieved",
                    ],
                ),
            ],
        ),
        Section("Expertise",
            column=1,
            groups=[
                SkillsEntry(skills=[
                    "Math",
                    "Mentorship",
                    "Microsoft Office",
                ]),
            ],
        ),
        Section("Education",
            column=1,
            entries=[
                ExperienceEntry(
                    start_date=Date(2013),
                    end_date=Date(2017),
                    title="Bachelor of Science in Computer Science",
                    subtitle="University of Example",
                    bullets=[
                        "What you learned",
                        "What you achieved",
                    ],
                ),
            ],
        ),
    ],
)
