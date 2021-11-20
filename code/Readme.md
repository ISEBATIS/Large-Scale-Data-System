@Author Sebati Ilias
@Author Gomez Herrera Maria Andrea Liliana

@Date January 2021
@Year-Of-Study B3Q1


Project of large scale data systems. This project is about trying to reach consensus between several computers.


------------ TUTORIAL 


The code is composed of three main files: 

    - without-ksp.py is the  main file for creating the process. But before	running this file you first need to create the n computers.

    - computers.py is the file containing  the class FlightComputer. This file should not be used (i.e: do not run it) .

    -computer.py is the file representing a computer you can run it with the following command (you need first to go in the starter-code directory): 
    
    $ python3 computer.py fligh_computer_number
    
    fligh_computer_number is the number of the flight computer starting from 1 to n.  The servers (i.e: computer) do not print on the terminal (e.g. GET requests...) to be more efficiant and to see the errors. However, you can comment the lines 13, 14, and 15 to enable it again (of the computer.py file).


    For instance:
    If you want to test the without-ksp.py program with 3 computers. You will first create three terminals (each one representing a computer). From the first terminal to the last one you will do : 

    First terminal:
    $ python3 computer.py 1 
    
    Second terminal:
    $ python3 computer.py 2

    Third terminal:
    $ python3 computer.py 3
    
    
    After creating all your computers you can start the without-ksp.py program. 
    You first need to go in the `code` directory. Then type:
    
    $ python3 starter-code/without-ksp.py --flight-computers 3
    --correct-fraction fraction

    Where fraction is the fraction of correct computers (e.g: 1.0).

