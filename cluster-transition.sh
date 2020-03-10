#PBS -N transition
#PBS -d /home/gbailly/transition_model/KS-Transition
#PBS -l walltime=24:00:00
#PBS -m bae
#PBS -l nodes=1:ppn=2
#/home/gbailly/miniconda3/bin/python main-console.py "RW" &
#/home/gbailly/miniconda3/bin/python main-console.py "CK" &
#/home/gbailly/miniconda3/bin/python main-console.py "RW_D" &
/home/gbailly/miniconda3/bin/python main-console.py "RW_CK" &
/home/gbailly/miniconda3/bin/python main-console.py "RW_IGM" &

#/home/gbailly/miniconda3/bin/python main-console.py "RW_CK" &


wait

echo "C'est fini !"
