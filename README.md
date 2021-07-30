# Run-BLAST

## Introduction
This project is basically a wrapper for the NCBI BLAST programs, which also gives the user the ability to run multiple jobs in parallel. The program will dectect how many cpu's your machine has, and it will then launch the number of jobs equal to the Number of CPU's minus one. I have found it faster to blast multiple sequences locally by running the jobs in parallel. Other than that, all of the other functionality of the BLAST programs are preserved and used similarly to running the standalone BLAST programs by themselves.  

### Dependences
* BLAST+
* Git
* Python 3
* PIP
* Conda
* progress
* progressbar2
* alive-progress
* tqdm

## General Setup
This project was developed for the Linux Operating System. This project was developed using Debian 10.

### Update
Run the following command to update your system and ensure everything install properly.
```
sudo apt-get update
sudo apt-get upgrade
```

### Install Git
```
sudo apt-get install git
```

### Install Conda
This program uses Conda to properlly install dependencies. This procedure is based on the tutoral [How to Install Anaconda on Linux](https://linoxide.com/how-install-anaconda-ubuntu-linux-guide/).

Download the installer.
```
wget https://repo.continuum.io/archive/Anaconda3-5.0.0.1-Linux-x86_64.sh
```

Run the installer
```
sh Anaconda3-5.0.0.1-Linux-x86_64.sh
```

When prompted, press enter to view the license and continue to press enter to scroll through the license agreement.

Whem prompted, type yes to accept the license.

Press enter to confirm the installation location. 

Towards the end, when it asks if you want to prepend Anaconda to your OS’s PATH variable, select ‘Yes’. 

### Install Python 3
The project relies on Python 3 in order to runs. This can be install by running the following commands on the terminal.
```
sudo apt install python3-pip
sudo apt install python-pip
```

### Cloning This Repo with HTTPS
To download this repository on your device, you must clone this repo using either HTTPS or SSH. The easiest way to clone this repository on your local device is through HTTPS. If you SDK allows you to clone a repo through HTTPS, then do so. Otherwise, you can do it directly on the command prompt. To do so, open up the command prompt and move to the desired directory. Then simply run the following command and enter you credentials.
```
git clone https://github.com/denkovarik/Run-BLAST.git
```
After the repo has been cloned on your device, move into the Run-BLAST directory from the command line.
```
cd Annotate-KEGG-Pathway
```

### Cloning This Repo with SSH
You can also clone this repo using SSH. Follow the instructions below to clone the repo using SSH. Please note that if you have already cloned the repo using HTTPS, then you can skip to the 'Install Dependencies' step.

#### Generate an SSH Key Pair
```
ssh-keygen
```

#### Add Your Public SSH Key to GitHub
Once you have an SSH Key Pair generated, you need to add your public SSH key to GitHub. Follow [How to view your SSH keys in Linux, macOS, and Windows](https://www.techrepublic.com/article/how-to-view-your-ssh-keys-in-linux-macos-and-windows/) to access you public key. Then follow [Adding a new SSH key to your GitHub account](https://docs.github.com/en/github/authenticating-to-github/adding-a-new-ssh-key-to-your-github-account) to add your public SSH key to GitHub.

#### Clone the Repository
If your SDK allows for it, then clone this repository through you SDK. Otherwise, open up the command prompt, move the the directory of your choice, then run the following command.
```
git clone git@github.com:denkovarik/Run-BLAST.git
```
After the repo has been cloned on your device, move into the Run-BLAST directory from the command line.
```
cd Run-BLAST
```

### Install Dependencies
Next, install the dependencies needed for the project. This can be done by simply running 'setup.sh'.
```
./setup.sh
```

## Usage
This program is basically a wrapper for the BLAST+ programs, except this program gives you the option to run multiple jobs in parallel. This can be done by specifying the commandline argument [-query_parallel multi-sequence_fasta].

Example useage using blastp and the nr database.
```
python run_blast.py -program blastp -db path/to/database/nr -query_parallel multi_sequence_fasta.fasta -outfmt 5
```
When done, blast results can be found in the directory 'blast_rslts/', and each BLAST result will be named by their description in the FASTA file. 


## Author
* Dennis Kovarik
