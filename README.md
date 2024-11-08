﻿#  Booking System
  

##  Description

This application combines powerful backend functionality with an intuitive frontend design to create an efficient and easy-to-use classroom booking system. Built with FastAPI and enriched with a modern user interface, it allows users to seamlessly register, log in, and book classrooms in a visually engaging and user-friendly manner. Whether you're an administrator managing resources or a student reserving a study room, this app offers an enjoyable and streamlined experience.


##  Features

- **User Registration and Authentication**: Users can sign up and log in securely to access classroom booking features.

- **Secure Login and Session Management**: Secure user login with password hashing and session handling.

- **Classroom Viewing**: View available classrooms with real-time information on booking availability.

- **Responsive Frontend Design**: The application features a modern, responsive design for easy access on all devices.

- **Event logging**: Important events are recorded in log files for easy debugging.

  

##  Technologies Used

- **Python 3.8+**: Primary programming language.

- **SQLite**: For storage of information.

- **Jinja2**: Template engine for rendering HTML pages.

- **bcrypt (Passlib)**: For password hashing and user security.

- **Logging**: To log events and errors.
  

##  How to Run

1. Clone the repository:

```bash
git clone https://github.com/Alexx6MR/Booking_System_FastAPI
cd Booking_System_FastAPI
```
2. Create a folder logs at root-level if it does not exist:

```bash
+logs -> new folder
app/
```
3. Create a virtual environment (optional but recommended):

```bash
mac: python3 -m venv .venv
windows: py -3 -m venv .venv
```
4. Activate the virtual environment:

```bash
Windows: .venv\Scripts\activate
Mac: . .venv/bin/activate
```
5. Install the dependencies:

```bash
pip install -r requirements.txt
```
6. Run the program:

```bash
fastapi dev app/main.py
```
