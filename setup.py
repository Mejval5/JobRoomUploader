from setuptools import setup, find_packages

setup(
    name="job-room-uploader",
    version="1.0.0",
    description="A tool for managing and updating job applications on ORP job search platform",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Daniel Necesal",
    author_email="necesal.daniel@gmail.com",
    url="https://github.com/Mejval5/JobRoomUploader",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=["pandas>=1.0.0", "requests>=2.0.0"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
