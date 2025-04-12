from setuptools import setup, find_packages

setup(
    name='mouse_trajectory_generator',
    version='0.0.1',
    description='A library to generate trajectory from mouse movements',
    long_description=open('USAGE.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Felipe Padula Sanches',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'numpy',
        'opencv_python'
    ],
    license='MIT',
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'mouse_trajectory_generator = mouse_trajectory_generator.cli:main',
        ],
    },
    include_package_data=True,
    package_data={"mouse_trajectory_generator": ["*.csv"]}
)
