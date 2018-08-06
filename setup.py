from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='RTUview',
    version='0.0.1',
    license='MIT',
    url='https://github.com/sourceperl/RTUview',
    platforms='any',
    install_requires=required,
    scripts=[
        'scripts/rtu_ts_monitor',
        'scripts/rtu_write_id'
    ]
)
