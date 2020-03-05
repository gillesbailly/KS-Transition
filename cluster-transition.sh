#PBS -N transition
#PBS -d /home/gbailly/transition_model/KS-Transition
#PBS -m bae
#PBS -l nodes=1:ppn=2
/home/gbailly/miniconda3/bin/python main-console.py "RW" &
/home/gbailly/miniconda3/bin/python main-console.py "CK" &

wait

echo "C'est fini !"
