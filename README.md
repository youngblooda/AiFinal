This Repo is the result of work between Pierce And Ahanu, resulting in a game of Minesweeper
that uses Z3 Sat solving with constraints in order to assist the player with figuring out where the mines are. 

There are 4 main files, AISolver.py, Game.py, Minesweepr.py, Accuracy_Data.txt, Main.py

Minesweeper.py is The first iteration of our project and is a standalone game of Minesweeper with nothing attached to it. 

For the minesweeper with AI please execute Main.py as that is our handler for all other files. Once main.py has been run, a pygame client will open on your computer
With this pygame client, there are 3 options for difficulty easy, medium, and hard. Once a difficulty has been selected and clicked, it will load you into a game called minesweeper.
Now you can test your skill on Minesweeper or you can click the AI Solver button, 
This button acts as an assistance tool taking in data of the squares you have clicked and making a prediction on where it thinks mines are located.
This AI assistance tool uses Z3-solver SAT solving with different constraints to predict where mines are. The accuracy of this AI algorithm goes down the larger the grid. 
If you decide to use the AI Solver, because the AI solver updates its prediction after each click, the main function will write to a text file the accuracy of the predictions being made. 

