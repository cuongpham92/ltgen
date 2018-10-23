# LTGen: Legitimate Traffic Generation System

LTGen is a traffic generation tool. Currently LTGen is able to generate traffic for five main application protocols, namely HTTP, IMAP, SMTP, and FTP, with distribution weights and average throughput defined by the users. In addition, to ensure the realism of the generated traffic, LTGen features built-in agents for each protocol, which generate various actions linked together by a probability model to reflect normal activities of real users in daily life.

## Installing LTGen

To run LTGen, we first need an environment, consisting of client machines, and server machines for HTTP, IMAP, SMTP, and FTP. In our experiments, we use OpenStack to create a virtual environment, with he topology as in `ltgen_environment.png`. This environment can be created in a automatic manner, by using HEAT module provided by OpenStack. An input YAML file, specifying this topology for HEAT, has been created in folder `heat_template`. To understand more about HEAT, please visit official websites of OpenStack. The base images, under format QCOW2, are also prepared. Please find them under the directory `base_images`.

After having installed the environment, please following the steps:

* Copy LTGen source code to all the client machines;
* For server machines, access to each one and follow the procedures to install services there.

## Running LTGen

Some key issues that must not be forgotten before proceeding to run LTGen are:

* The configuration file `rate_timetable.txt` is for inputting an interval and a throughput of traffic generated during that interval;

* The configuration file `protocol_weight.txt` is for inputting in one line the distrubtion weights among different protocols. The order of values are HTTP, IMAP, SMTP, and FTP.

Once these files are prepared, one can run LTGen by:

  `$ python3 main.py`

  
