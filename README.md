# DataBlend

DataBlend is a tool that allows users to automatically store and retrieve data about Blender objects in a PostgreSQL database. The tool uses Python and the psycopg2 library to connect to the database, and stores information such as object name, vertex count, location, and dimensions. Users can easily update and delete object data from within Blender and see those changes reflected in the database.

This tool is useful for artists and developers who want to store and organize large amounts of object data, such as in a game development pipeline. By automatically updating the database, users can easily keep track of changes to their objects and make informed decisions about their workflow.

## Features

- Automatically insert or update data about objects in the database when changes are made in Blender, including the object's name, vertex count, location, and dimensions.
- Automatically delete data from the database when objects are deleted in Blender.
- Allow users to view and manipulate object data in the database using SQL queries.
- Support for multiple Blender files and multiple users, with each object assigned to a specific file and user.


## Getting Started

First run the install_psycopg2.py file using blender to connect to the PostgreSql database.

Then, run the DataBlend.py file in blender.

    
