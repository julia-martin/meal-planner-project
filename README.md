# meal-planner-project
Flask app created for CS50 final project

For my first-ever project, I created a meal planner web app. It’s something I find useful, since I like to plan out what I will cook a few days in advance to help plan for grocery shopping. 

What it does:
The meal planner app allows you to type in what meals you plan to have this week, along with (optionally) the key ingredients they need and a link to the recipe, if any. The data is saved to a SQL database and auto-loaded upon sign-in. The user can also keep track of what ingredients they have on hand, with functionality for adding and deleting. Ingredients are also stored in a SQL database for the user. Since each user’s meal plans are unique, the app requires users to create an account and be logged in before they can create a meal plan.

Files:
I created this app using Flask using the concepts I learned in CS50, supplemented by substantive online research. My project consists of an app.py file (with 5 routes), 5 HTML pages, and a styles.css file. I have a ‘layout.html’ file that contains the header and footer, which is extended in my other HTML files. There is a ‘login.html’ and ‘register.html’ page which behaves similarly to the ones in the Finance project. The ‘index.html’ file is the main page where the user can add and edit their meal plan. Finally, the ‘ingredients.html’ file is where the user can edit their ingredients list.

Design:
I used Bootstrap for the baseline CSS and then overrode most of it with my own styles. 
The ‘/ingredients’ route used to be on the same page as the index, but I had to split it out into its own route and make a new HTML page for it since there were so many different POST requests from the index page. 
For the text inputs where users input meal details, I debated between a form input and an editable div. I ended up using an editable div so that the content would stay on the page with each reload. 

Conclusion:
There were some additional features I thought of, but don’t know how to implement right now. I hope to continue adding to this as I pick up more skills.

This was certainly a challenging project (far more so than the Finance problem), but I learned so much about Flask, HTML, CSS, Bootstrap, jQuery, AJAX and more!
