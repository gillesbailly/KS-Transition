#PBS -N transition
#PBS -d /home/transition_model
#PBS -m bae
#PBS nodes=1:ppn=2
python main-console.py "RW"
python main-console.py "CK"
