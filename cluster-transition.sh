#PBS -N transition
#PBS -d /home/gbailly/transition_model/KS-Transition
#PBS -m bae
#PBS -l nodes=1:ppn=2
python main-console.py "RW"
python main-console.py "CK"
