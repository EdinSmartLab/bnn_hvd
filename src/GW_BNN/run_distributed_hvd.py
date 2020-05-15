import os
import numpy as np
import argparse
import time
#from functions_spin_1 import *

# from fun_spin_hvd_adaptive import *
from functions_spin_distributed_hvd import *


parser = argparse.ArgumentParser()
parser.add_argument("--alpha_KL", default= 1.,help="Scaling the KL term in the ELBO Loss",type=float)
parser.add_argument("--vary_var", default=False,help="Fit for the var, default=False",type=bool)
parser.add_argument("--hvd", default=False,help="Use hvd, default=False",type=bool)
parser.add_argument("--pout", default=False,help="print output, default=False",type=bool)
parser.add_argument("--TestDataRun", default=True,help="Run Testing dataset, default=True",type=bool)
parser.add_argument("--fixed_var", default=0.2,help="Fixed var, default=0.2",type=float)
parser.add_argument("--num_mc", default=100,help="Num MonteCarlo samples, default=100",type=int)
parser.add_argument("--num_iter", default=9000,help="Num iterations, default=9000",type=int)
parser.add_argument("--batchsize", default=32,help="batch size, default=32",type=int)
parser.add_argument("--TestIter", default=50,help=" Test iteration to start every # training steps, default=50",type=int)
parser.add_argument("--PrintStep", default=50,help=" Print the relative error every # steps, default=50",type=int)
parser.add_argument("--TFseed", default=1234,help="TF random seed, default=1234",type=int)
parser.add_argument("--Model_Name", default='spin_GW_BNn_RUN',help=" Name of the Dir to create, default='spin_omegas_model_var_check_10_BNN'",type=str)
parser.add_argument("--train_logs", default='train_logs',help="log directory name",type=str)
parser.add_argument("--Datasave_path",default='/projects/datascience/hsharma/GW_Project/Single_Script/data_store',help="Save the Data generated by the code",type=str)
parser.add_argument("--Re_Start", default=False,help="Re start flag true if checkpoints present , default=False",type=bool)
parser.add_argument('--lr', default=0.0008, type=float,help='learning rate')
parser.add_argument('--toler',default=2e-2,type=float, help='Tolerance for stopping')
parser.add_argument('--num_intra', type=int,default=128,
                    help='num_intra')
parser.add_argument('--num_inter', type=int,default=1,
                    help='num_inter')
parser.add_argument('--kmp_blocktime', type=int, default=0,
                    help='KMP BLOCKTIME')
parser.add_argument('--kmp_affinity', default='granularity=fine,verbose,compact,1,0',
                    help='KMP AFFINITY')

args = parser.parse_args()

# Total RUN-Time
Total_Time_Start = time.time()

Seed_set = Setup_Seed(args)

if args.hvd:
    #print ('Initalizing HVD')
    import horovod.tensorflow as hvd
    hvd.init()
    if hvd.rank() == 0:
        print("args:",args)
else:
    #print ('HVD False')
    print ("args:",args)
    





model_name = args.Model_Name

if_shift = True
if_real_noise = True
if_zero = False

Time_startdataset = time.time()


EOBdataset = Dataset(args, SNR=3., shift=if_shift, real_noise=if_real_noise,SEED=Seed_set,
                     zero=if_zero, save_path=args.Datasave_path,model_name=model_name)

End_time_LoadDataset = time.time() - Time_startdataset

if args.hvd:
    import horovod.tensorflow as hvd
    hvd.init()
    if hvd.rank() == 0:
        print("End_Time to Load dataset 0 SNR {} sec:".format(End_time_LoadDataset))
else:
    print("End_Time to Load dataset 0 SNR  {}:".format(End_time_LoadDataset))

config=create_config_proto(args)

Model = Train_Model(SEED=Seed_set)

model = RUN_Model(config,args,model=Model,batch_size=args.batchsize, signal_length=8192, SEED=Seed_set,num_of_pred_var=3,beta1=1., beta2=1., beta3=1.)


model.train(EOBdataset, iterations=args.num_iter, print_step=args.PrintStep)

#### 
Total_End_Time = time.time() - Total_Time_Start


if args.hvd:
    import horovod.tensorflow as hvd
    hvd.init()
    if hvd.rank() == 0:
        print ("*"*60)
        print("TIME:Loading dataset 0 SNR {} sec:".format(End_time_LoadDataset))
        print("TIME:Run Script Total Run Time: {} sec".format(Total_End_Time))
        print ("*"*60)
else:
    print("TIME:Loading dataset 0 SNR {} sec:".format(End_time_LoadDataset))
    print("TIME:Run Script Total Run Time: {} sec".format(Total_End_Time))