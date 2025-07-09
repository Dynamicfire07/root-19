# Quiz App

A web-based quiz application built with Django that allows users to register, log in, practice questions, and track progress. This project features a dynamic and user-friendly interface, including a hero section, session-based authentication, and animated feedback.

This version uses **MongoDB** for data storage instead of the default SQLite database. All data is stored in MongoDB collections and accessed via `pymongo`.

## Features

- **User Authentication**:
  - Registration with email, password, and user role (Student/Teacher).
  - Login and Logout functionality.
  - Navbar displays "Welcome, User" when logged in.
  
- **Question Management**:
  - Practice questions by selecting session codes and subtopics.
  - Dynamic loading of subtopics based on the selected session code.
  - Feedback for correct/incorrect answers.
  
- **Home Page**:
  - Animated hero section.
  - Real-time display of the total number of questions in the database.

## Prerequisites

Make sure you have the following installed:

- Python 3.x
- Django 4.x
- MongoDB server (or Atlas cluster)
- pymongo

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/quiz-app.git
   cd quiz-app
