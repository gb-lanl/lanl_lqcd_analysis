import sys
import lsqfit
import gvar as gv
import importlib
import h5py
import copy
import os
import pathlib
import random
import matplotlib.pyplot as plt
import argparse
import numpy as np
import argparse
import pandas as pd

np.seterr(invalid='ignore') 



# lanl_analysis_suite libs.modules
# sys.path.insert(0,'./lqcd_corr_analysis')
path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(path)
from fitter import *
from utilities import * 
from tests import * 

import fitter.plotting as visualize
import fitter.coalesce as coalesce
import fitter.prelim_fit as prelim 


def main():
        print(*sys.argv)
        #     reparse_argv()
        less_indent_formatter = lambda prog: argparse.RawTextHelpFormatter(prog, max_help_position=40)
        parser = argparse.ArgumentParser(description = 
        
        " This is the master executable for analysis of \n"
        " lqcd correlator and form factor data. The fallback default arguments are contained in /tests/input_file/defaults.py. \n"
         
        "Features have been added with modularity/user flexibility in mind. However, with this type of analysis,"
        " The human-provided input remains necessary. ")
        
        parser.add_argument('fit_params',    help='input file to specify fit')
        parser.add_argument('-b', '--block', default=1, type=int,
                        help=            'specify bin/blocking size in terms of saved configs')
        parser.add_argument('--states',      nargs='+',
                        help=            'specify states to fit?')
        parser.add_argument('--plot-file', default = None, dest = 'res_filename',
                help = "Plot the correlator from a file instead of performing a fit. \n"
                " You can pass a fitmass... file here")
        parser.add_argument('--plot-start', action = 'store_true', dest = 'plot_start',
                help = "Do not perform a fit. Instead generate a plot with the start parameters.\n"
                " Has to be passed along with --start-params")


        # # parser.add_argument('filename', help = "The filename containing the data")
        # # parser.add_argument('n_states override', help = "override given n_states in input file here \n")
        # # parser.add_argument('--Nt', 
        # #         help = "dont compute Nt from data, use this one. WARNING: correlator \n"
        # # "will not be symmetrized")
        # # parser.add_argument('--log-level', default = "INFO",
        # #         help = "log level options: WARN, INFO, PROGRESS, DETAILS, DEBUG, NONE \n")
        # # parser.add_argument('n_states override', help = "override given n_states in input file here \n")

        # # parser.add_argument('channel', help='Select channels to fit')
        # # parser.add_argument('run_src', help= "Run fit for C_2pt at the src?")
        # # parser.add_argument('run_snk', help= "Run fit for C_2pt at the snk?")
        # # parser.add_argument('run_ratio', help= "Run fit for C_3pt/C_2pt?")
        # # parser.add_argument('run_direct', help= "Run fit for spectral decomposition (not using C_2pt)?")
        # # parser.add_argument('summary', help="print summary of fit results in current shell?") #TODO to txt, save data pickle


        args = parser.parse_args()
        # TODO set up buffers
        # Buffer = 
        # buffers = []
        # Channel = namedtuple("Channel", ['abbr','name'])
        # channels = []

        ''' parse provided input/label file '''
        sys.path.append(os.path.dirname(os.path.abspath(args.fit_params)))
        fp = importlib.import_module(
                args.fit_params.split('/')[-1].split('.py')[0])
        
        # block data
        bl = args.block
        if 'block' in dir(fp) and fp.block != 1:
                bl = fp.block
        if args.block != 1: # allow cl override
                bl = args.block

        if args.states:
                states = args.states
        else:
                states = fp.fit_states

        # corr_raw = 

        # ''' process correlator data '''
        # corr_gv = fitter.prepare_data_lanl.coalesce_data(corr_raw)

        # ''' data handling options ''' 

        '''parsing generated h5 files from run_data_options'''
        h5f = h5py.File('proton_all.h5','r')
        string_2pt = '2pt/proton/src10.0_snk10.0/proton/AMA'
        h5f_3pt = h5py.File('3pt_out.h5','r')
        c3_data = {'A3' : {}, 'V4' : {}}
        c2_data = {}
        # h5f_sp = h5py.File('proton_SP.h5','r')
        string = '2pt/proton/src10.0_snk10.0/proton/AMA'
        string_sp = '2pt/proton_SP/src10.0_snk10.0/proton/AMA'

        ''' fill 2pt corr dict'''
        c2_path_concat_data = {}
        c2_path_concat_data['proton'] = {
                'src':'2pt/proton/src10.0_snk10.0/proton/AMA', 
                'snk' : '2pt/proton_SP/src10.0_snk10.0/proton/AMA'
                                        }
        c2_path_concat_data['pion'] = {
                'src':'2pt/pion/src10.0_snk10.0/pion/AMA', 
                'snk' : '2pt/pion_SP/src10.0_snk10.0/pion/AMA'
                                        }

        ''' 
        fill charges dict with tsep vals as keys
        Note: charges are extracted from ratio at 0 momentum,
        form factor extraction from permutations of momentum indices TODO 
        ''' 
        c3_path_concat_data = {}
        c3_path_concat_data[int(13)]   = {'A3':'13/_l0_g11/qz+0_qy+0_qx+0/AMA','V4':'13/_l0_g8/qz+0_qy+0_qx+0/AMA'
                                        ''} #WHY ARE U AND D DSETS NOT BEING SEP! 
        c3_path_concat_data[int(15)]   = {'A3':'15/_l0_g11/qz+0_qy+0_qx+0/AMA','V4':'15/_l0_g8/qz+0_qy+0_qx+0/AMA'} #WHY ARE U AND D DSETS NOT BEING SEP! 
        c3_path_concat_data[int(17)]   = {'A3':'17/_l0_g11/qz+0_qy+0_qx+0/AMA','V4':'17/_l0_g8/qz+0_qy+0_qx+0/AMA'} #WHY ARE U AND D DSETS NOT BEING SEP! 
        c3_path_concat_data[int(19)]   = {'A3':'19/_l0_g11/qz+0_qy+0_qx+0/AMA','V4':'19/_l0_g8/qz+0_qy+0_qx+0/AMA'} #WHY ARE U AND D DSETS NOT BEING SEP! 
        c3_path_concat_data[int(21)]   = {'A3':'21/_l0_g11/qz+0_qy+0_qx+0/AMA','V4':'21/_l0_g8/qz+0_qy+0_qx+0/AMA'} #WHY ARE U AND D DSETS NOT BEING SEP! 

        

        to_array = lambda f, path : pd.DataFrame(f[path][:]) #real for v4, imag else
        # ydata = {}                                        
        # ydata['proton'] = to_array(h5f,c2_path_concat_data['proton']['src'])
        # ydata_out = ld.bs_to_gvar(data=ydata, corr='proton',bs_N=100) #576?

        print(ydata_out)
        
        temp_data = {'A3':{}, 'V4':{}, 'P5' : {}, 'T2':{}}
        temp_data['A3'][int(13)] = (to_array(h5f_3pt,c3_path_concat_data[int(13)]['A3']))['im'] 
        temp_data['A3'][int(15)] = (to_array(h5f_3pt,c3_path_concat_data[int(15)]['A3']))['im'] 
        temp_data['A3'][int(17)] = (to_array(h5f_3pt,c3_path_concat_data[int(17)]['A3']))['im'] 
        temp_data['A3'][int(19)] = (to_array(h5f_3pt,c3_path_concat_data[int(19)]['A3']))['im'] 
        temp_data['A3'][int(21)] = (to_array(h5f_3pt,c3_path_concat_data[int(21)]['A3']))['im'] 

        temp_data['V4'][int(13)] = (to_array(h5f_3pt,c3_path_concat_data[int(13)]['V4']))['re']
        temp_data['V4'][int(15)] = (to_array(h5f_3pt,c3_path_concat_data[int(15)]['V4']))['re'] 
        temp_data['V4'][int(17)] = (to_array(h5f_3pt,c3_path_concat_data[int(17)]['V4']))['re'] 
        temp_data['V4'][int(19)] = (to_array(h5f_3pt,c3_path_concat_data[int(19)]['V4']))['re'] 
        temp_data['V4'][int(21)] = (to_array(h5f_3pt,c3_path_concat_data[int(21)]['V4']))['re'] 
        
        # TODO PS,S,T

        print(temp_data)

        # temp_data['P5'][int(13)] = (to_array(h5f_3pt,c3_path_concat_data[int(13)]['P5']))['re']
        # temp_data['P5'][int(15)] = (to_array(h5f_3pt,c3_path_concat_data[int(15)]['P5']))['re'] 
        # temp_data['P5'][int(17)] = (to_array(h5f_3pt,c3_path_concat_data[int(17)]['P5']))['re'] 
        # temp_data['P5'][int(19)] = (to_array(h5f_3pt,c3_path_concat_data[int(19)]['P5']))['re'] 
        # temp_data['P5'][int(21)] = (to_array(h5f_3pt,c3_path_concat_data[int(21)]['P5']))['re'] 

        n_cfg = []
        for n_cfg in temp_data['A3'].values():
                print(n_cfg.shape[0])


                # c3pt_data[g_type]

        # print(temp_data)
        ''' bin/block/resize data '''

        # ydict_3pt = {}
        # ydict_3pt['proton_SS'] = np.reshape(corrs['proton'], (Ncfg//bl, bl))
        # ydict_3pt['proton_SP'] = np.reshape(corrs['proton_SP'], (Ncfg//bl, bl))
        # ydict_3pt[int(13)] = np.reshape(c3pt_data[int(13)], (Ncfg_3pt//bl_, bl_))
        # print(ydict_3pt[int(13)])

        # TODO this should just inherit same struct as temp_data and apply fcn to it .. 
        c3pt_data = {'A3': {}, 'V4' : {}}
        c2pt_data = {}
        
        # # only need real part for 2pt correlators
        # _ifil = pd.DataFrame(temp_data)
        # # print(_ifil)
        # _ifil_sp = pd.DataFrame(ifil_sp)['re'] 
        # corrs = {}
        # corrs['proton'] = _ifil.to_numpy()
        # corrs['proton_SP'] = _ifil_sp.to_numpy()
        # corrs[int(13)] = _ifil_13.to_numpy()
        # corrs.columns
        # Ncfg = corrs['proton'].shape[0]
        # bl = 18
        # Ncfg_3pt = 8232 #c3pt_data[int(13)].shape[0]
        # bl_ = 294
        
        ydata = {}
        
        # ydata[int(15)] = 
        # ydata[int(17)] = 
        # ydata[int(19)] =
        # ydata[int(21)] = 

        # print(ydata.keys())
        ydata_out = ld.bs_to_gvar(data=ydata, corr='proton_SS',bs_N=100) #576?

        x, priors = ld.prepare_xyp(states, fp, ydata_out)
        # print(x,priors)
        c2pt = {}
        c2_src = cf.C_2pt(tag='proton', ydata=c2_path_concat_data['proton'],p=priors)
        c2_snk = cf.C_2pt(tag='proton_SP', ydata=c2_path_concat_data['proton_SP'],p=priors)

        print(c2_src)
        print(c2_src.meff())

        args = parser.parse_args()
        # TODO set up buffers
        # Buffer = 
        # buffers = []
        # Channel = namedtuple("Channel", ['abbr','name'])
        # channels = []

        c2pt['SS'] = c2_src
        c2pt['PS'] = c2_snk
        print(c2_src.times)
        c2_avg = {tag: c2pt[tag].avg() for tag in c2pt}
        print(c2_avg)
        tfit = {}
        for tag in c2pt:
                # print(tag)
                tfit[tag] =  np.arange(c2pt[tag].times.tmin,c2pt[tag].times.tmax +1)
        print(tfit)
        # print(c2_src.plot_corr())
        print(plotting.get_nucleon_effective_mass(ydata_out))
        visualize.plot_effective_mass(ydata_out)
        
        c3 = {}
        c3 = cf.C_3pt('A3', ydata_3pt=ydata_3pt[int(13)],t_ins=range(12),T=[13,15,17])

        """ time containers for correlators """
        nts = [c2_src.times.nt,c2_snk.times.nt, c3.times.nt]
        print(nts)

        tmaxes = [c2_src.times.tmax, c2_snk.times.tmax, c3.times.tmax]
        tdata = np.arange(0, min(tmaxes))

        """ Estimate ground-state mass associated with source operator."""
        m_src = c2_src.mass

        """ Estimate ground-state mass associated with sink operator."""
        m_snk = c2_snk.mass
        if m_src is not None:
                c2_src.set_mass(m_src)
        if m_snk is not None:
                c2_snk.set_mass(m_snk)

   
        # print(c3.avg(m_src=c2_src.meff(), m_snk=c2_snk.meff()))
        # print(ydata_out)
        # for k,v in ydata_out.items():
        #         print(k,v)
        # print(states)
        
        

        # ''' data handling options ''' 

        # lg.set_log_level(args.log_level)
        # args = vars(args)
        # del args['log_level']

        # '''Run fits sequentially'''

        # if args.run_src:
        #         analysis.run_src(n=args.nstates)

        # if args.run_snk:
        #         analysis.run_snk(n=args.nstates)

        
        # if args.run_ratio:
        #         analysis.run_ratio(
        #                 n=args.nstates-1, 
        #                 tmin_src = c2_src.times.tmin,  
        #                 tmin_snk = c2_snk.times.tmin,
        #                 t_iter = c3.times.nt)
        #         # if args.axial:
        #         #         analysis
                
        # #         # if args.vector:
                
        # #         # if args.scalar:
                
        # #         # if args.tensor:

        # if args.run_spectral_decomp:
        #         analysis.spectral_decomp(nstates=args.nstates)
        
        # # if args.summary:
        # #         analysis.print_summary()





        











if __name__ == '__main__':
    main()