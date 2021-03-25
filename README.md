# AI and MAS: client



Winter 2021 DTU 02285 Artificial Intelligence and Multi-Agent Systems course project.



## Group 28 - Members



        Jiayan Wu - s202534

        Elvis Antônio Ferreira Camilo - s190395

        Dimosthenis Karafylias - s202632

        Prashanna Raveendra Kumar - s192140



This readme describes how to use the re-written version of the Python client with the server. 



The Python search client requires at least Python version 3.8, and has been tested with CPython.



The search client requires the 'psutil' and other packages. They can be installed with pip:



    $ pip install -r requirements.txt



All the following commands assume the working directory is the one this readme is located in.



You can read about the server options using the -h argument:



    $ java -jar ../server.jar -h



Starting the server using the client: 



    $ java -jar ../server.jar -l ../levels/SAD1.lvl -c "python bin/main.py" -g -s 150 -t 1800

