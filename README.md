# IBST
Stands for Internal BEST Structure Tool
<br>
Nothing fancy...
<br>
The idea behind this flask app is to create a tool that helps BEST Internal structure. <br>
There are a few ideas behind this project, the main purpose was to create a voting app. Other ideas range from creating a KM Database (Knowledge Managment Database), a Git-flow based university-notes (so that each student can download Notes from other Students and add more information to it) or an HR-Tool to have some control over BEST Madrid Members

Does this project spark your Interest? Well, I still need to write a few things to set it up. (Alembic Database Migrations, Members tool API (Members control, Roles creation, etc), IRV (Instant Runoff Voting), Profile pages, Front page for Minutes and Info for events

So yeah, If you try to set this up from 0, you probably won't see anything of value, because most of the things require you to have a role, like member, baby, full, or admin.  But you can add those roles by yourself in the database and create the relations between members and roles. Or you can also wait for me to end this project and create a setup script that creates a Admin user from 0 <br>
I just saw I didn't delete the database, so there is a db with random users. The password for all of them is <b>'noviembre'</b>, the admin user is me: <b>Lukas</b>, but there are other users with other roles.

The last push included avatar support for members and OAUTH sign up or login. The private keys are included, but it doesn't matter. The keys are only viable for https://localhost:5000, and wont be the keys in the production
